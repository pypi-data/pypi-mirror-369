"""Startup utility functions for application lifecycle management.

This module contains simple utility functions to extract and organize
the complex startup logic from the main lifespan function, following
the KISS principle and avoiding overengineering.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog
from fastapi import FastAPI

from ccproxy.auth.credentials_adapter import CredentialsAuthManager
from ccproxy.auth.exceptions import CredentialsNotFoundError
from ccproxy.observability import get_metrics

# Note: get_claude_cli_info is imported locally to avoid circular imports
from ccproxy.observability.storage.duckdb_simple import SimpleDuckDBStorage
from ccproxy.scheduler.errors import SchedulerError
from ccproxy.scheduler.manager import start_scheduler, stop_scheduler
from ccproxy.services.claude_detection_service import ClaudeDetectionService
from ccproxy.services.claude_sdk_service import ClaudeSDKService
from ccproxy.services.codex_detection_service import CodexDetectionService
from ccproxy.services.credentials.manager import CredentialsManager


# Note: get_permission_service is imported locally to avoid circular imports

if TYPE_CHECKING:
    from ccproxy.config.settings import Settings

logger = structlog.get_logger(__name__)


async def validate_authentication_startup(app: FastAPI, settings: Settings) -> None:
    """Validate authentication credentials at startup.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    try:
        credentials_manager = CredentialsManager()
        validation = await credentials_manager.validate()

        if validation.valid and not validation.expired:
            credentials = validation.credentials
            oauth_token = credentials.claude_ai_oauth if credentials else None

            if oauth_token and oauth_token.expires_at_datetime:
                hours_until_expiry = int(
                    (
                        oauth_token.expires_at_datetime - datetime.now(UTC)
                    ).total_seconds()
                    / 3600
                )
                logger.debug(
                    "auth_token_valid",
                    expires_in_hours=hours_until_expiry,
                    subscription_type=oauth_token.subscription_type,
                    credentials_path=str(validation.path) if validation.path else None,
                )
            else:
                logger.debug("auth_token_valid", credentials_path=str(validation.path))
        elif validation.expired:
            logger.warning(
                "auth_token_expired",
                message="Authentication token has expired. Please run 'ccproxy auth login' to refresh.",
                credentials_path=str(validation.path) if validation.path else None,
            )
        else:
            logger.warning(
                "auth_token_invalid",
                message="Authentication token is invalid. Please run 'ccproxy auth login'.",
                credentials_path=str(validation.path) if validation.path else None,
            )
    except CredentialsNotFoundError:
        logger.warning(
            "auth_token_not_found",
            message="No authentication credentials found. Please run 'ccproxy auth login' to authenticate.",
            searched_paths=settings.auth.storage.storage_paths,
        )
    except Exception as e:
        logger.error(
            "auth_token_validation_error",
            error=str(e),
            message="Failed to validate authentication token. The server will continue without authentication.",
            exc_info=True,
        )


async def check_claude_cli_startup(app: FastAPI, settings: Settings) -> None:
    """Check Claude CLI availability at startup.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    try:
        from ccproxy.api.routes.health import get_claude_cli_info

        claude_info = await get_claude_cli_info()

        if claude_info.status == "available":
            logger.info(
                "claude_cli_available",
                status=claude_info.status,
                version=claude_info.version,
                binary_path=claude_info.binary_path,
            )
        else:
            logger.warning(
                "claude_cli_unavailable",
                status=claude_info.status,
                error=claude_info.error,
                binary_path=claude_info.binary_path,
                message=f"Claude CLI status: {claude_info.status}",
            )
    except Exception as e:
        logger.error(
            "claude_cli_check_failed",
            error=str(e),
            message="Failed to check Claude CLI status during startup",
        )


async def check_codex_cli_startup(app: FastAPI, settings: Settings) -> None:
    """Check Codex CLI availability at startup.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    try:
        from ccproxy.api.routes.health import get_codex_cli_info

        codex_info = await get_codex_cli_info()

        if codex_info.status == "available":
            logger.info(
                "codex_cli_available",
                status=codex_info.status,
                version=codex_info.version,
                binary_path=codex_info.binary_path,
            )
        else:
            logger.warning(
                "codex_cli_unavailable",
                status=codex_info.status,
                error=codex_info.error,
                binary_path=codex_info.binary_path,
                message=f"Codex CLI status: {codex_info.status}",
            )
    except Exception as e:
        logger.error(
            "codex_cli_check_failed",
            error=str(e),
            message="Failed to check Codex CLI status during startup",
        )


async def initialize_log_storage_startup(app: FastAPI, settings: Settings) -> None:
    """Initialize log storage if needed and backend is DuckDB.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    if (
        settings.observability.needs_storage_backend
        and settings.observability.log_storage_backend == "duckdb"
    ):
        try:
            storage = SimpleDuckDBStorage(
                database_path=settings.observability.duckdb_path
            )
            await storage.initialize()
            app.state.log_storage = storage
            logger.debug(
                "log_storage_initialized",
                backend="duckdb",
                path=str(settings.observability.duckdb_path),
                collection_enabled=settings.observability.logs_collection_enabled,
            )
        except Exception as e:
            logger.error("log_storage_initialization_failed", error=str(e))
            # Continue without log storage (graceful degradation)


async def initialize_log_storage_shutdown(app: FastAPI) -> None:
    """Close log storage if initialized.

    Args:
        app: FastAPI application instance
    """
    if hasattr(app.state, "log_storage") and app.state.log_storage:
        try:
            await app.state.log_storage.close()
            logger.debug("log_storage_closed")
        except Exception as e:
            logger.error("log_storage_close_failed", error=str(e))


async def setup_scheduler_startup(app: FastAPI, settings: Settings) -> None:
    """Start scheduler system and configure tasks.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    try:
        scheduler = await start_scheduler(settings)
        app.state.scheduler = scheduler
        logger.debug("scheduler_initialized")

        # Add session pool stats task if session manager is available
        if (
            scheduler
            and hasattr(app.state, "session_manager")
            and app.state.session_manager
        ):
            try:
                # Add session pool stats task that runs every minute
                await scheduler.add_task(
                    task_name="session_pool_stats",
                    task_type="pool_stats",
                    interval_seconds=60,  # Every minute
                    enabled=True,
                    pool_manager=app.state.session_manager,
                )
                logger.debug("session_pool_stats_task_added", interval_seconds=60)
            except Exception as e:
                logger.error(
                    "session_pool_stats_task_add_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
    except SchedulerError as e:
        logger.error("scheduler_initialization_failed", error=str(e))
        # Continue startup even if scheduler fails (graceful degradation)


async def setup_scheduler_shutdown(app: FastAPI) -> None:
    """Stop scheduler system.

    Args:
        app: FastAPI application instance
    """
    try:
        scheduler = getattr(app.state, "scheduler", None)
        await stop_scheduler(scheduler)
        logger.debug("scheduler_stopped_lifespan")
    except SchedulerError as e:
        logger.error("scheduler_stop_failed", error=str(e))


async def setup_session_manager_shutdown(app: FastAPI) -> None:
    """Shutdown Claude SDK session manager if it was created.

    Args:
        app: FastAPI application instance
    """
    if hasattr(app.state, "session_manager") and app.state.session_manager:
        try:
            await app.state.session_manager.shutdown()
            logger.debug("claude_sdk_session_manager_shutdown")
        except Exception as e:
            logger.error("claude_sdk_session_manager_shutdown_failed", error=str(e))


async def initialize_claude_detection_startup(app: FastAPI, settings: Settings) -> None:
    """Initialize Claude detection service.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    try:
        logger.debug("initializing_claude_detection")
        detection_service = ClaudeDetectionService(settings)
        claude_data = await detection_service.initialize_detection()
        app.state.claude_detection_data = claude_data
        app.state.claude_detection_service = detection_service
        logger.debug(
            "claude_detection_completed",
            version=claude_data.claude_version,
            cached_at=claude_data.cached_at.isoformat(),
        )
    except Exception as e:
        logger.error("claude_detection_startup_failed", error=str(e))
        # Continue startup with fallback - detection service will provide fallback data
        detection_service = ClaudeDetectionService(settings)
        app.state.claude_detection_data = detection_service._get_fallback_data()
        app.state.claude_detection_service = detection_service


async def initialize_codex_detection_startup(app: FastAPI, settings: Settings) -> None:
    """Initialize Codex detection service.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    try:
        logger.debug("initializing_codex_detection")
        detection_service = CodexDetectionService(settings)
        codex_data = await detection_service.initialize_detection()
        app.state.codex_detection_data = codex_data
        app.state.codex_detection_service = detection_service
        logger.debug(
            "codex_detection_completed",
            version=codex_data.codex_version,
            cached_at=codex_data.cached_at.isoformat(),
        )
    except Exception as e:
        logger.error("codex_detection_startup_failed", error=str(e))
        # Continue startup with fallback - detection service will provide fallback data
        detection_service = CodexDetectionService(settings)
        app.state.codex_detection_data = detection_service._get_fallback_data()
        app.state.codex_detection_service = detection_service


async def initialize_claude_sdk_startup(app: FastAPI, settings: Settings) -> None:
    """Initialize ClaudeSDKService and store in app state.

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    try:
        # Create auth manager with settings
        auth_manager = CredentialsAuthManager()

        # Get global metrics instance
        metrics = get_metrics()

        # Check if session pool should be enabled from settings configuration
        use_session_pool = settings.claude.sdk_session_pool.enabled

        # Initialize session manager if session pool is enabled
        session_manager = None
        if use_session_pool:
            from ccproxy.claude_sdk.manager import SessionManager

            # Create SessionManager with dependency injection
            session_manager = SessionManager(
                settings=settings, metrics_factory=lambda: metrics
            )

            # Start the session manager (initializes session pool if enabled)
            await session_manager.start()

        # Create ClaudeSDKService instance
        claude_service = ClaudeSDKService(
            auth_manager=auth_manager,
            metrics=metrics,
            settings=settings,
            session_manager=session_manager,
        )

        # Store in app state for reuse in dependencies
        app.state.claude_service = claude_service
        app.state.session_manager = (
            session_manager  # Store session_manager for shutdown
        )
        logger.debug("claude_sdk_service_initialized")
    except Exception as e:
        logger.error("claude_sdk_service_initialization_failed", error=str(e))
        # Continue startup even if ClaudeSDKService fails (graceful degradation)


async def initialize_permission_service_startup(
    app: FastAPI, settings: Settings
) -> None:
    """Initialize permission service (conditional on builtin_permissions).

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    if settings.claude.builtin_permissions:
        try:
            from ccproxy.api.services.permission_service import get_permission_service

            permission_service = get_permission_service()

            # Only connect terminal handler if not using external handler
            if settings.server.use_terminal_permission_handler:
                # terminal_handler = TerminalPermissionHandler()

                # TODO: Terminal handler should subscribe to events from the service
                # instead of trying to set a handler directly
                # The service uses an event-based architecture, not direct handlers

                # logger.info(
                #     "permission_handler_configured",
                #     handler_type="terminal",
                #     message="Connected terminal handler to permission service",
                # )
                # app.state.terminal_handler = terminal_handler
                pass
            else:
                logger.debug(
                    "permission_handler_configured",
                    handler_type="external_sse",
                    message="Terminal permission handler disabled - use 'ccproxy permission-handler connect' to handle permissions",
                )
                logger.warning(
                    "permission_handler_required",
                    message="Start external handler with: ccproxy permission-handler connect",
                )

            # Start the permission service
            await permission_service.start()

            # Store references in app state
            app.state.permission_service = permission_service

            logger.debug(
                "permission_service_initialized",
                timeout_seconds=permission_service._timeout_seconds,
                terminal_handler_enabled=settings.server.use_terminal_permission_handler,
                builtin_permissions_enabled=True,
            )
        except Exception as e:
            logger.error("permission_service_initialization_failed", error=str(e))
            # Continue without permission service (API will work but without prompts)
    else:
        logger.debug(
            "permission_service_skipped",
            builtin_permissions_enabled=False,
            message="Built-in permission handling disabled - users can configure custom MCP servers and permission tools",
        )


async def setup_permission_service_shutdown(app: FastAPI, settings: Settings) -> None:
    """Stop permission service (if it was initialized).

    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    if (
        hasattr(app.state, "permission_service")
        and app.state.permission_service
        and settings.claude.builtin_permissions
    ):
        try:
            await app.state.permission_service.stop()
            logger.debug("permission_service_stopped")
        except Exception as e:
            logger.error("permission_service_stop_failed", error=str(e))


async def flush_streaming_batches_shutdown(app: FastAPI) -> None:
    """Flush any remaining streaming log batches.

    Args:
        app: FastAPI application instance
    """
    try:
        from ccproxy.utils.simple_request_logger import flush_all_streaming_batches

        await flush_all_streaming_batches()
        logger.debug("streaming_batches_flushed")
    except Exception as e:
        logger.error("streaming_batches_flush_failed", error=str(e))
