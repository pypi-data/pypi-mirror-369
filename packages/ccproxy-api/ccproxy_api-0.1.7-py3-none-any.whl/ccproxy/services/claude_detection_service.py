"""Service for automatically detecting Claude CLI headers at startup."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
from pathlib import Path
from typing import Any

import structlog
from fastapi import FastAPI, Request, Response

from ccproxy.config.discovery import get_ccproxy_cache_dir
from ccproxy.config.settings import Settings
from ccproxy.models.detection import (
    ClaudeCacheData,
    ClaudeCodeHeaders,
    SystemPromptData,
)


logger = structlog.get_logger(__name__)


class ClaudeDetectionService:
    """Service for automatically detecting Claude CLI headers at startup."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Claude detection service."""
        self.settings = settings
        self.cache_dir = get_ccproxy_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cached_data: ClaudeCacheData | None = None

    async def initialize_detection(self) -> ClaudeCacheData:
        """Initialize Claude detection at startup."""
        try:
            # Get current Claude version
            current_version = await self._get_claude_version()

            # Try to load from cache first
            detected_data = self._load_from_cache(current_version)
            cached = detected_data is not None
            if cached:
                logger.debug("detection_claude_headers_debug", version=current_version)
            else:
                # No cache or version changed - detect fresh
                detected_data = await self._detect_claude_headers(current_version)
                # Cache the results
                self._save_to_cache(detected_data)

            self._cached_data = detected_data

            logger.info(
                "detection_claude_headers_completed",
                version=current_version,
                cached=cached,
            )

            # TODO: add proper testing without claude cli installed
            if detected_data is None:
                raise ValueError("Claude detection failed")
            return detected_data

        except Exception as e:
            logger.warning("detection_claude_headers_failed", fallback=True, error=e)
            # Return fallback data
            fallback_data = self._get_fallback_data()
            self._cached_data = fallback_data
            return fallback_data

    def get_cached_data(self) -> ClaudeCacheData | None:
        """Get currently cached detection data."""
        return self._cached_data

    async def _get_claude_version(self) -> str:
        """Get Claude CLI version."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Extract version from output like "1.0.60 (Claude Code)"
                version_line = result.stdout.strip()
                if "/" in version_line:
                    # Handle "claude-cli/1.0.60" format
                    version_line = version_line.split("/")[-1]
                if "(" in version_line:
                    # Handle "1.0.60 (Claude Code)" format - extract just the version number
                    return version_line.split("(")[0].strip()
                return version_line
            else:
                raise RuntimeError(f"Claude version command failed: {result.stderr}")

        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            logger.warning("claude_version_detection_failed", error=str(e))
            return "unknown"

    async def _detect_claude_headers(self, version: str) -> ClaudeCacheData:
        """Execute Claude CLI with proxy to capture headers and system prompt."""
        # Data captured from the request
        captured_data: dict[str, Any] = {}

        async def capture_handler(request: Request) -> Response:
            """Capture the Claude CLI request."""
            captured_data["headers"] = dict(request.headers)
            captured_data["body"] = await request.body()
            # Return a mock response to satisfy Claude CLI
            return Response(
                content='{"type": "message", "content": [{"type": "text", "text": "Test response"}]}',
                media_type="application/json",
                status_code=200,
            )

        # Create temporary FastAPI app
        temp_app = FastAPI()
        temp_app.post("/v1/messages")(capture_handler)

        # Find available port
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()

        # Start server in background
        from uvicorn import Config, Server

        config = Config(temp_app, host="127.0.0.1", port=port, log_level="error")
        server = Server(config)

        server_task = asyncio.create_task(server.serve())

        try:
            # Wait for server to start
            await asyncio.sleep(0.5)

            # Execute Claude CLI with proxy
            env = {**dict(os.environ), "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{port}"}

            process = await asyncio.create_subprocess_exec(
                "claude",
                "test",
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for process with timeout
            try:
                await asyncio.wait_for(process.wait(), timeout=30)
            except TimeoutError:
                process.kill()
                await process.wait()

            # Stop server
            server.should_exit = True
            await server_task

            if not captured_data:
                raise RuntimeError("Failed to capture Claude CLI request")

            # Extract headers and system prompt
            headers = self._extract_headers(captured_data["headers"])
            system_prompt = self._extract_system_prompt(captured_data["body"])

            return ClaudeCacheData(
                claude_version=version, headers=headers, system_prompt=system_prompt
            )

        except Exception as e:
            # Ensure server is stopped
            server.should_exit = True
            if not server_task.done():
                await server_task
            raise

    def _load_from_cache(self, version: str) -> ClaudeCacheData | None:
        """Load cached data for specific Claude version."""
        cache_file = self.cache_dir / f"claude_headers_{version}.json"

        if not cache_file.exists():
            return None

        try:
            with cache_file.open("r") as f:
                data = json.load(f)
                return ClaudeCacheData.model_validate(data)
        except Exception:
            return None

    def _save_to_cache(self, data: ClaudeCacheData) -> None:
        """Save detection data to cache."""
        cache_file = self.cache_dir / f"claude_headers_{data.claude_version}.json"

        try:
            with cache_file.open("w") as f:
                json.dump(data.model_dump(), f, indent=2, default=str)
            logger.debug(
                "cache_saved", file=str(cache_file), version=data.claude_version
            )
        except Exception as e:
            logger.warning("cache_save_failed", file=str(cache_file), error=str(e))

    def _extract_headers(self, headers: dict[str, str]) -> ClaudeCodeHeaders:
        """Extract Claude CLI headers from captured request."""
        try:
            return ClaudeCodeHeaders.model_validate(headers)
        except Exception as e:
            logger.error("header_extraction_failed", error=str(e))
            raise ValueError(f"Failed to extract required headers: {e}") from e

    def _extract_system_prompt(self, body: bytes) -> SystemPromptData:
        """Extract system prompt from captured request body."""
        try:
            data = json.loads(body.decode("utf-8"))
            system_content = data.get("system")

            if system_content is None:
                raise ValueError("No system field found in request body")

            return SystemPromptData(system_field=system_content)

        except Exception as e:
            logger.error("system_prompt_extraction_failed", error=str(e))
            raise ValueError(f"Failed to extract system prompt: {e}") from e

    def _get_fallback_data(self) -> ClaudeCacheData:
        """Get fallback data when detection fails."""
        logger.warning("using_fallback_claude_data")

        # Load fallback data from package data file
        package_data_file = (
            Path(__file__).parent.parent / "data" / "claude_headers_fallback.json"
        )
        with package_data_file.open("r") as f:
            fallback_data_dict = json.load(f)
            return ClaudeCacheData.model_validate(fallback_data_dict)
