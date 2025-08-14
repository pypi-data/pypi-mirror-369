"""HTTP-level transformers for proxy service."""

from typing import TYPE_CHECKING, Any

import structlog
from typing_extensions import TypedDict

from ccproxy.core.transformers import RequestTransformer, ResponseTransformer
from ccproxy.core.types import ProxyRequest, ProxyResponse, TransformContext


if TYPE_CHECKING:
    pass


logger = structlog.get_logger(__name__)

# Claude Code system prompt constants
claude_code_prompt = "You are Claude Code, Anthropic's official CLI for Claude."

# claude_code_prompt = "<system-reminder>\nAs you answer the user's questions, you can use the following context:\n# important-instruction-reminders\nDo what has been asked; nothing more, nothing less.\nNEVER create files unless they're absolutely necessary for achieving your goal.\nALWAYS prefer editing an existing file to creating a new one.\nNEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.\n\n      \n      IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task.\n</system-reminder>\n"


def get_detected_system_field(
    app_state: Any = None, injection_mode: str = "minimal"
) -> Any:
    """Get the detected system field for injection.

    Args:
        app_state: App state containing detection data
        injection_mode: 'minimal' or 'full' mode

    Returns:
        The system field to inject (preserving exact Claude CLI structure), or None if no detection data available
    """
    if not app_state or not hasattr(app_state, "claude_detection_data"):
        return None

    claude_data = app_state.claude_detection_data
    detected_system = claude_data.system_prompt.system_field

    if injection_mode == "full":
        # Return the complete detected system field exactly as Claude CLI sent it
        return detected_system
    else:
        # Minimal mode: extract just the first system message, preserving its structure
        if isinstance(detected_system, str):
            return detected_system
        elif isinstance(detected_system, list) and detected_system:
            # Return only the first message object with its complete structure (type, text, cache_control)
            return [detected_system[0]]

    return None


def get_fallback_system_field() -> list[dict[str, Any]]:
    """Get fallback system field when no detection data is available."""
    return [
        {
            "type": "text",
            "text": claude_code_prompt,
            "cache_control": {"type": "ephemeral"},
        }
    ]


class RequestData(TypedDict):
    """Typed structure for transformed request data."""

    method: str
    url: str
    headers: dict[str, str]
    body: bytes | None


class ResponseData(TypedDict):
    """Typed structure for transformed response data."""

    status_code: int
    headers: dict[str, str]
    body: bytes


class HTTPRequestTransformer(RequestTransformer):
    """HTTP request transformer that implements the abstract RequestTransformer interface."""

    def __init__(self) -> None:
        """Initialize HTTP request transformer."""
        super().__init__()

    async def _transform_request(
        self, request: ProxyRequest, context: TransformContext | None = None
    ) -> ProxyRequest:
        """Transform a proxy request according to the abstract interface.

        Args:
            request: The structured proxy request to transform
            context: Optional transformation context

        Returns:
            The transformed proxy request
        """
        # Transform path
        transformed_path = self.transform_path(
            request.url.split("?")[0].split("/", 3)[-1]
            if "/" in request.url
            else request.url
        )

        # Build new URL with transformed path
        base_url = "https://api.anthropic.com"
        new_url = f"{base_url}{transformed_path}"

        # Add query parameters
        if request.params:
            import urllib.parse

            query_string = urllib.parse.urlencode(request.params)
            new_url = f"{new_url}?{query_string}"

        # Transform headers (requires access token from context)
        access_token = ""
        if context and hasattr(context, "access_token"):
            access_token = context.access_token
        elif context and isinstance(context, dict):
            access_token = context.get("access_token", "")

        # Extract app_state from context if available
        app_state = None
        if context and hasattr(context, "app_state"):
            app_state = context.app_state
        elif context and isinstance(context, dict):
            app_state = context.get("app_state")

        transformed_headers = self.create_proxy_headers(
            request.headers, access_token, self.proxy_mode, app_state
        )

        # Transform body
        transformed_body = request.body
        if request.body:
            if isinstance(request.body, bytes):
                transformed_body = self.transform_request_body(
                    request.body, transformed_path, self.proxy_mode, app_state
                )
            elif isinstance(request.body, str):
                transformed_body = self.transform_request_body(
                    request.body.encode("utf-8"),
                    transformed_path,
                    self.proxy_mode,
                    app_state,
                )
            elif isinstance(request.body, dict):
                import json

                transformed_body = self.transform_request_body(
                    json.dumps(request.body).encode("utf-8"),
                    transformed_path,
                    self.proxy_mode,
                    app_state,
                )

        # Create new transformed request
        return ProxyRequest(
            method=request.method,
            url=new_url,
            headers=transformed_headers,
            params={},  # Already included in URL
            body=transformed_body,
            protocol=request.protocol,
            timeout=request.timeout,
            metadata=request.metadata,
        )

    async def transform_proxy_request(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes | None,
        query_params: dict[str, str | list[str]] | None,
        access_token: str,
        target_base_url: str = "https://api.anthropic.com",
        app_state: Any = None,
        injection_mode: str = "minimal",
    ) -> RequestData:
        """Transform request using direct parameters from ProxyService.

        This method provides the same functionality as ProxyService._transform_request()
        but is properly located in the transformer layer.

        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            body: Request body
            query_params: Query parameters
            access_token: OAuth access token
            target_base_url: Base URL for the target API
            app_state: Optional app state containing detection data
            injection_mode: System prompt injection mode

        Returns:
            Dictionary with transformed request data (method, url, headers, body)
        """
        import urllib.parse

        # Transform path
        transformed_path = self.transform_path(path, self.proxy_mode)
        target_url = f"{target_base_url.rstrip('/')}{transformed_path}"

        # Add beta=true query parameter for /v1/messages requests if not already present
        if transformed_path == "/v1/messages":
            if query_params is None:
                query_params = {}
            elif "beta" not in query_params:
                query_params = dict(query_params)  # Make a copy

            if "beta" not in query_params:
                query_params["beta"] = "true"

        # Transform body first (as it might change size)
        proxy_body = None
        if body:
            proxy_body = self.transform_request_body(
                body, path, self.proxy_mode, app_state, injection_mode
            )

        # Transform headers (and update Content-Length if body changed)
        proxy_headers = self.create_proxy_headers(
            headers, access_token, self.proxy_mode, app_state
        )

        # Update Content-Length if body was transformed and size changed
        if proxy_body and body and len(proxy_body) != len(body):
            # Remove any existing content-length headers (case-insensitive)
            proxy_headers = {
                k: v for k, v in proxy_headers.items() if k.lower() != "content-length"
            }
            proxy_headers["Content-Length"] = str(len(proxy_body))
        elif proxy_body and not body:
            # New body was created where none existed
            proxy_headers["Content-Length"] = str(len(proxy_body))

        # Add query parameters to URL if present
        if query_params:
            query_string = urllib.parse.urlencode(query_params)
            target_url = f"{target_url}?{query_string}"

        return RequestData(
            method=method,
            url=target_url,
            headers=proxy_headers,
            body=proxy_body,
        )

    def transform_path(self, path: str, proxy_mode: str = "full") -> str:
        """Transform request path."""
        # Remove /api prefix if present (for new proxy endpoints)
        if path.startswith("/api"):
            path = path[4:]  # Remove "/api" prefix

        # Remove /openai prefix if present
        if path.startswith("/openai"):
            path = path[7:]  # Remove "/openai" prefix

        # Convert OpenAI chat completions to Anthropic messages
        if path == "/v1/chat/completions":
            return "/v1/messages"

        return path

    def create_proxy_headers(
        self,
        headers: dict[str, str],
        access_token: str,
        proxy_mode: str = "full",
        app_state: Any = None,
    ) -> dict[str, str]:
        """Create proxy headers from original headers with Claude CLI identity."""
        proxy_headers = {}

        # Strip potentially problematic headers
        excluded_headers = {
            "host",
            "x-forwarded-for",
            "x-forwarded-proto",
            "x-forwarded-host",
            "forwarded",
            # Authentication headers to be replaced
            "authorization",
            "x-api-key",
            # Compression headers to avoid decompression issues
            "accept-encoding",
            "content-encoding",
            # CORS headers - should not be forwarded to upstream
            "origin",
            "access-control-request-method",
            "access-control-request-headers",
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
            "access-control-allow-credentials",
            "access-control-max-age",
            "access-control-expose-headers",
        }

        # Copy important headers (excluding problematic ones)
        for key, value in headers.items():
            lower_key = key.lower()
            if lower_key not in excluded_headers:
                proxy_headers[key] = value

        # Set authentication with OAuth token
        if access_token:
            proxy_headers["Authorization"] = f"Bearer {access_token}"

        # Set defaults for essential headers
        if "content-type" not in [k.lower() for k in proxy_headers]:
            proxy_headers["Content-Type"] = "application/json"
        if "accept" not in [k.lower() for k in proxy_headers]:
            proxy_headers["Accept"] = "application/json"
        if "connection" not in [k.lower() for k in proxy_headers]:
            proxy_headers["Connection"] = "keep-alive"

        # Use detected Claude CLI headers when available
        if app_state and hasattr(app_state, "claude_detection_data"):
            claude_data = app_state.claude_detection_data
            detected_headers = claude_data.headers.to_headers_dict()
            proxy_headers.update(detected_headers)
            logger.debug("using_detected_headers", version=claude_data.claude_version)
        else:
            # Fallback to hardcoded Claude/Anthropic headers
            proxy_headers["anthropic-beta"] = (
                "claude-code-20250219,oauth-2025-04-20,"
                "interleaved-thinking-2025-05-14,fine-grained-tool-streaming-2025-05-14"
            )
            proxy_headers["anthropic-version"] = "2023-06-01"
            proxy_headers["anthropic-dangerous-direct-browser-access"] = "true"

            # Claude CLI identity headers
            proxy_headers["x-app"] = "cli"
            proxy_headers["User-Agent"] = "claude-cli/1.0.60 (external, cli)"

            # Stainless SDK compatibility headers
            proxy_headers["X-Stainless-Lang"] = "js"
            proxy_headers["X-Stainless-Retry-Count"] = "0"
            proxy_headers["X-Stainless-Timeout"] = "60"
            proxy_headers["X-Stainless-Package-Version"] = "0.55.1"
            proxy_headers["X-Stainless-OS"] = "Linux"
            proxy_headers["X-Stainless-Arch"] = "x64"
            proxy_headers["X-Stainless-Runtime"] = "node"
            proxy_headers["X-Stainless-Runtime-Version"] = "v24.3.0"
            logger.debug("using_fallback_headers")

        # Standard HTTP headers for proper API interaction
        proxy_headers["accept-language"] = "*"
        proxy_headers["sec-fetch-mode"] = "cors"
        # Note: accept-encoding removed to avoid compression issues
        # HTTPX handles compression automatically

        return proxy_headers

    def _count_cache_control_blocks(self, data: dict[str, Any]) -> dict[str, int]:
        """Count cache_control blocks in different parts of the request.

        Returns:
            Dictionary with counts for 'injected_system', 'user_system', and 'messages'
        """
        counts = {"injected_system": 0, "user_system": 0, "messages": 0}

        # Count in system field
        system = data.get("system")
        if system:
            if isinstance(system, str):
                # String system prompts don't have cache_control
                pass
            elif isinstance(system, list):
                # Count cache_control in system prompt blocks
                # The first block(s) are injected, rest are user's
                injected_count = 0
                for i, block in enumerate(system):
                    if isinstance(block, dict) and "cache_control" in block:
                        # Check if this is the injected prompt (contains Claude Code identity)
                        text = block.get("text", "")
                        if "Claude Code" in text or "Anthropic's official CLI" in text:
                            counts["injected_system"] += 1
                            injected_count = max(injected_count, i + 1)
                        elif i < injected_count:
                            # Part of injected system (multiple blocks)
                            counts["injected_system"] += 1
                        else:
                            counts["user_system"] += 1

        # Count in messages
        messages = data.get("messages", [])
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and "cache_control" in block:
                        counts["messages"] += 1

        return counts

    def _limit_cache_control_blocks(
        self, data: dict[str, Any], max_blocks: int = 4
    ) -> dict[str, Any]:
        """Limit the number of cache_control blocks to comply with Anthropic's limit.

        Priority order:
        1. Injected system prompt cache_control (highest priority - Claude Code identity)
        2. User's system prompt cache_control
        3. User's message cache_control (lowest priority)

        Args:
            data: Request data dictionary
            max_blocks: Maximum number of cache_control blocks allowed (default: 4)

        Returns:
            Modified data dictionary with cache_control blocks limited
        """
        import copy

        # Deep copy to avoid modifying original
        data = copy.deepcopy(data)

        # Count existing blocks
        counts = self._count_cache_control_blocks(data)
        total = counts["injected_system"] + counts["user_system"] + counts["messages"]

        if total <= max_blocks:
            # No need to remove anything
            return data

        logger.warning(
            "cache_control_limit_exceeded",
            total_blocks=total,
            max_blocks=max_blocks,
            injected=counts["injected_system"],
            user_system=counts["user_system"],
            messages=counts["messages"],
        )

        # Calculate how many to remove
        to_remove = total - max_blocks
        removed = 0

        # Remove from messages first (lowest priority)
        if to_remove > 0 and counts["messages"] > 0:
            messages = data.get("messages", [])
            for msg in reversed(messages):  # Remove from end first
                if removed >= to_remove:
                    break
                content = msg.get("content")
                if isinstance(content, list):
                    for block in reversed(content):
                        if removed >= to_remove:
                            break
                        if isinstance(block, dict) and "cache_control" in block:
                            del block["cache_control"]
                            removed += 1
                            logger.debug("removed_cache_control", location="message")

        # Remove from user system prompts next
        if removed < to_remove and counts["user_system"] > 0:
            system = data.get("system")
            if isinstance(system, list):
                # Find and remove cache_control from user system blocks (non-injected)
                for block in reversed(system):
                    if removed >= to_remove:
                        break
                    if isinstance(block, dict) and "cache_control" in block:
                        text = block.get("text", "")
                        # Skip injected prompts (highest priority)
                        if (
                            "Claude Code" not in text
                            and "Anthropic's official CLI" not in text
                        ):
                            del block["cache_control"]
                            removed += 1
                            logger.debug(
                                "removed_cache_control", location="user_system"
                            )

        # In theory, we should never need to remove injected system cache_control
        # but include this for completeness
        if removed < to_remove:
            logger.error(
                "cannot_preserve_injected_cache_control",
                needed_to_remove=to_remove,
                actually_removed=removed,
            )

        return data

    def transform_request_body(
        self,
        body: bytes,
        path: str,
        proxy_mode: str = "full",
        app_state: Any = None,
        injection_mode: str = "minimal",
    ) -> bytes:
        """Transform request body."""
        if not body:
            return body

        # Check if this is an OpenAI request and transform it
        if self._is_openai_request(path, body):
            # Transform OpenAI format to Anthropic format
            body = self._transform_openai_to_anthropic(body)

        # Apply system prompt transformation for Claude Code identity
        return self.transform_system_prompt(body, app_state, injection_mode)

    def transform_system_prompt(
        self, body: bytes, app_state: Any = None, injection_mode: str = "minimal"
    ) -> bytes:
        """Transform system prompt based on injection mode.

        Args:
            body: Original request body as bytes
            app_state: Optional app state containing detection data
            injection_mode: System prompt injection mode ('minimal' or 'full')

        Returns:
            Transformed request body as bytes with system prompt injection
        """
        try:
            import json

            data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Return original if not valid JSON
            logger.warning(
                "http_transform_json_decode_failed",
                error=str(e),
                body_preview=body[:200].decode("utf-8", errors="replace")
                if body
                else None,
                body_length=len(body) if body else 0,
            )
            return body

        # Get the system field to inject
        detected_system = get_detected_system_field(app_state, injection_mode)
        if detected_system is None:
            # No detection data, use fallback
            detected_system = get_fallback_system_field()

        # Always inject the system prompt (detected or fallback)
        if "system" not in data:
            # No existing system prompt, inject the detected/fallback one
            data["system"] = detected_system
        else:
            # Request has existing system prompt, prepend the detected/fallback one
            existing_system = data["system"]

            if isinstance(detected_system, str):
                # Detected system is a string
                if isinstance(existing_system, str):
                    # Both are strings, convert to list format
                    data["system"] = [
                        {"type": "text", "text": detected_system},
                        {"type": "text", "text": existing_system},
                    ]
                elif isinstance(existing_system, list):
                    # Detected is string, existing is list
                    data["system"] = [
                        {"type": "text", "text": detected_system}
                    ] + existing_system
            elif isinstance(detected_system, list):
                # Detected system is a list
                if isinstance(existing_system, str):
                    # Detected is list, existing is string
                    data["system"] = detected_system + [
                        {"type": "text", "text": existing_system}
                    ]
                elif isinstance(existing_system, list):
                    # Both are lists, concatenate
                    data["system"] = detected_system + existing_system

        # Limit cache_control blocks to comply with Anthropic's limit
        data = self._limit_cache_control_blocks(data)

        return json.dumps(data).encode("utf-8")

    def _is_openai_request(self, path: str, body: bytes) -> bool:
        """Check if this is an OpenAI API request."""
        # Check path-based indicators
        if "/openai/" in path or "/chat/completions" in path:
            return True

        # Check body-based indicators
        if body:
            try:
                import json

                data = json.loads(body.decode("utf-8"))
                # Look for OpenAI-specific patterns
                model = data.get("model", "")
                if model.startswith(("gpt-", "o1-", "text-davinci")):
                    return True
                # Check for OpenAI message format with system in messages
                messages = data.get("messages", [])
                if messages and any(msg.get("role") == "system" for msg in messages):
                    return True
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(
                    "openai_request_detection_json_decode_failed",
                    error=str(e),
                    body_preview=body[:100].decode("utf-8", errors="replace")
                    if body
                    else None,
                )
                pass

        return False

    def _transform_openai_to_anthropic(self, body: bytes) -> bytes:
        """Transform OpenAI request format to Anthropic format."""
        try:
            # Use the OpenAI adapter for transformation
            import json

            from ccproxy.adapters.openai.adapter import OpenAIAdapter

            adapter = OpenAIAdapter()
            openai_data = json.loads(body.decode("utf-8"))
            anthropic_data = adapter.adapt_request(openai_data)
            return json.dumps(anthropic_data).encode("utf-8")

        except Exception as e:
            logger.warning(
                "openai_transformation_failed",
                error=str(e),
                operation="transform_openai_to_anthropic",
            )
            # Return original body if transformation fails
            return body


class HTTPResponseTransformer(ResponseTransformer):
    """HTTP response transformer that implements the abstract ResponseTransformer interface."""

    def __init__(self) -> None:
        """Initialize HTTP response transformer."""
        super().__init__()

    async def _transform_response(
        self, response: ProxyResponse, context: TransformContext | None = None
    ) -> ProxyResponse:
        """Transform a proxy response according to the abstract interface.

        Args:
            response: The structured proxy response to transform
            context: Optional transformation context

        Returns:
            The transformed proxy response
        """
        # Extract original path from context for transformation decisions
        original_path = ""
        if context and hasattr(context, "original_path"):
            original_path = context.original_path
        elif context and isinstance(context, dict):
            original_path = context.get("original_path", "")

        # Transform response body
        transformed_body = response.body
        if response.body:
            if isinstance(response.body, bytes):
                transformed_body = self.transform_response_body(
                    response.body, original_path
                )
            elif isinstance(response.body, str):
                body_bytes = response.body.encode("utf-8")
                transformed_body = self.transform_response_body(
                    body_bytes, original_path
                )
            elif isinstance(response.body, dict):
                import json

                body_bytes = json.dumps(response.body).encode("utf-8")
                transformed_body = self.transform_response_body(
                    body_bytes, original_path
                )

        # Calculate content length for transformed body
        content_length = 0
        if transformed_body:
            if isinstance(transformed_body, bytes):
                content_length = len(transformed_body)
            elif isinstance(transformed_body, str):
                content_length = len(transformed_body.encode("utf-8"))
            else:
                content_length = len(str(transformed_body))

        # Transform response headers
        transformed_headers = self.transform_response_headers(
            response.headers, original_path, content_length
        )

        # Create new transformed response
        return ProxyResponse(
            status_code=response.status_code,
            headers=transformed_headers,
            body=transformed_body,
            metadata=response.metadata,
        )

    async def transform_proxy_response(
        self,
        status_code: int,
        headers: dict[str, str],
        body: bytes,
        original_path: str,
        proxy_mode: str = "full",
    ) -> ResponseData:
        """Transform response using direct parameters from ProxyService.

        This method provides the same functionality as ProxyService._transform_response()
        but is properly located in the transformer layer.

        Args:
            status_code: HTTP status code
            headers: Response headers
            body: Response body
            original_path: Original request path for context
            proxy_mode: Proxy transformation mode

        Returns:
            Dictionary with transformed response data (status_code, headers, body)
        """
        # For error responses, handle OpenAI transformation if needed
        if status_code >= 400:
            transformed_error_body = body
            if self._is_openai_request(original_path):
                try:
                    import json

                    from ccproxy.adapters.openai.adapter import OpenAIAdapter

                    error_data = json.loads(body.decode("utf-8"))
                    openai_adapter = OpenAIAdapter()
                    openai_error = openai_adapter.adapt_error(error_data)
                    transformed_error_body = json.dumps(openai_error).encode("utf-8")
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Keep original error if parsing fails
                    pass

            return ResponseData(
                status_code=status_code,
                headers=headers,
                body=transformed_error_body,
            )

        # For successful responses, transform normally
        transformed_body = self.transform_response_body(body, original_path, proxy_mode)

        transformed_headers = self.transform_response_headers(
            headers, original_path, len(transformed_body), proxy_mode
        )

        return ResponseData(
            status_code=status_code,
            headers=transformed_headers,
            body=transformed_body,
        )

    def transform_response_body(
        self, body: bytes, path: str, proxy_mode: str = "full"
    ) -> bytes:
        """Transform response body."""
        # Basic body transformation - pass through for now
        return body

    def transform_response_headers(
        self,
        headers: dict[str, str],
        path: str,
        content_length: int,
        proxy_mode: str = "full",
    ) -> dict[str, str]:
        """Transform response headers."""
        transformed_headers = {}

        # Copy important headers
        for key, value in headers.items():
            lower_key = key.lower()
            if lower_key not in [
                "content-length",
                "transfer-encoding",
                "content-encoding",
                "date",  # Remove upstream date header to avoid conflicts
            ]:
                transformed_headers[key] = value

        # Set content length
        transformed_headers["Content-Length"] = str(content_length)

        # Add CORS headers
        transformed_headers["Access-Control-Allow-Origin"] = "*"
        transformed_headers["Access-Control-Allow-Headers"] = "*"
        transformed_headers["Access-Control-Allow-Methods"] = "*"

        return transformed_headers

    def _is_openai_request(self, path: str) -> bool:
        """Check if this is an OpenAI API request."""
        return "/openai/" in path or "/chat/completions" in path
