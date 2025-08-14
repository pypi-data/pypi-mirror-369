"""FastAPI application factory for CCProxy API Server."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from structlog import get_logger

from ccproxy import __version__
from ccproxy.api.middleware.cors import setup_cors_middleware
from ccproxy.api.middleware.errors import setup_error_handlers
from ccproxy.api.middleware.logging import AccessLogMiddleware
from ccproxy.api.middleware.request_content_logging import (
    RequestContentLoggingMiddleware,
)
from ccproxy.api.middleware.request_id import RequestIDMiddleware
from ccproxy.api.middleware.server_header import ServerHeaderMiddleware
from ccproxy.api.routes.claude import router as claude_router
from ccproxy.api.routes.codex import router as codex_router
from ccproxy.api.routes.health import router as health_router
from ccproxy.api.routes.mcp import setup_mcp
from ccproxy.api.routes.metrics import (
    dashboard_router,
    logs_router,
    prometheus_router,
)
from ccproxy.api.routes.permissions import router as permissions_router
from ccproxy.api.routes.proxy import router as proxy_router
from ccproxy.auth.oauth.routes import router as oauth_router
from ccproxy.config.settings import Settings, get_settings
from ccproxy.core.logging import setup_logging
from ccproxy.utils.models_provider import get_models_list
from ccproxy.utils.startup_helpers import (
    check_claude_cli_startup,
    check_codex_cli_startup,
    check_version_updates_startup,
    flush_streaming_batches_shutdown,
    initialize_claude_detection_startup,
    initialize_claude_sdk_startup,
    initialize_codex_detection_startup,
    initialize_log_storage_shutdown,
    initialize_log_storage_startup,
    initialize_permission_service_startup,
    setup_permission_service_shutdown,
    setup_scheduler_shutdown,
    setup_scheduler_startup,
    setup_session_manager_shutdown,
    validate_claude_authentication_startup,
    validate_codex_authentication_startup,
)


logger = get_logger(__name__)


# Type definitions for lifecycle components
class LifecycleComponent(TypedDict):
    name: str
    startup: Callable[[FastAPI, Any], Awaitable[None]] | None
    shutdown: (
        Callable[[FastAPI], Awaitable[None]]
        | Callable[[FastAPI, Any], Awaitable[None]]
        | None
    )


class ShutdownComponent(TypedDict):
    name: str
    shutdown: Callable[[FastAPI], Awaitable[None]] | None


# Define lifecycle components for startup/shutdown organization
LIFECYCLE_COMPONENTS: list[LifecycleComponent] = [
    {
        "name": "Claude Authentication",
        "startup": validate_claude_authentication_startup,
        "shutdown": None,  # One-time validation, no cleanup needed
    },
    {
        "name": "Codex Authentication",
        "startup": validate_codex_authentication_startup,
        "shutdown": None,  # One-time validation, no cleanup needed
    },
    {
        "name": "Version Check",
        "startup": check_version_updates_startup,
        "shutdown": None,  # One-time check, no cleanup needed
    },
    {
        "name": "Claude CLI",
        "startup": check_claude_cli_startup,
        "shutdown": None,  # Detection only, no cleanup needed
    },
    {
        "name": "Codex CLI",
        "startup": check_codex_cli_startup,
        "shutdown": None,  # Detection only, no cleanup needed
    },
    {
        "name": "Claude Detection",
        "startup": initialize_claude_detection_startup,
        "shutdown": None,  # No cleanup needed
    },
    {
        "name": "Codex Detection",
        "startup": initialize_codex_detection_startup,
        "shutdown": None,  # No cleanup needed
    },
    {
        "name": "Claude SDK",
        "startup": initialize_claude_sdk_startup,
        "shutdown": setup_session_manager_shutdown,
    },
    {
        "name": "Scheduler",
        "startup": setup_scheduler_startup,
        "shutdown": setup_scheduler_shutdown,
    },
    {
        "name": "Log Storage",
        "startup": initialize_log_storage_startup,
        "shutdown": initialize_log_storage_shutdown,
    },
    {
        "name": "Permission Service",
        "startup": initialize_permission_service_startup,
        "shutdown": setup_permission_service_shutdown,
    },
]

# Additional shutdown-only components that need special handling
SHUTDOWN_ONLY_COMPONENTS: list[ShutdownComponent] = [
    {
        "name": "Streaming Batches",
        "shutdown": flush_streaming_batches_shutdown,
    },
]


# Create shared models router
models_router = APIRouter(tags=["models"])


@models_router.get("/v1/models", response_model=None)
async def list_models() -> dict[str, Any]:
    """List available models.

    Returns a combined list of Anthropic models and recent OpenAI models.
    This endpoint is shared between both SDK and proxy APIs.
    """
    return get_models_list()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager using component-based approach."""
    settings = get_settings()

    # Store settings in app state for reuse in dependencies
    app.state.settings = settings

    # Startup
    logger.info(
        "server_start",
        host=settings.server.host,
        port=settings.server.port,
        url=f"http://{settings.server.host}:{settings.server.port}",
    )
    logger.debug(
        "server_configured", host=settings.server.host, port=settings.server.port
    )

    # Log Claude CLI configuration
    if settings.claude.cli_path:
        logger.debug("claude_cli_configured", cli_path=settings.claude.cli_path)
    else:
        logger.debug("claude_cli_auto_detect")
        logger.debug(
            "claude_cli_search_paths", paths=settings.claude.get_searched_paths()
        )

    # Execute startup components in order
    for component in LIFECYCLE_COMPONENTS:
        if component["startup"]:
            component_name = component["name"]
            try:
                logger.debug(f"starting_{component_name.lower().replace(' ', '_')}")
                await component["startup"](app, settings)
            except Exception as e:
                logger.error(
                    f"{component_name.lower().replace(' ', '_')}_startup_failed",
                    error=str(e),
                    component=component_name,
                )
                # Continue with graceful degradation

    yield

    # Shutdown
    logger.debug("server_stop")

    # Execute shutdown-only components first
    for shutdown_component in SHUTDOWN_ONLY_COMPONENTS:
        if shutdown_component["shutdown"]:
            component_name = shutdown_component["name"]
            try:
                logger.debug(f"stopping_{component_name.lower().replace(' ', '_')}")
                await shutdown_component["shutdown"](app)
            except Exception as e:
                logger.error(
                    f"{component_name.lower().replace(' ', '_')}_shutdown_failed",
                    error=str(e),
                    component=component_name,
                )

    # Execute shutdown components in reverse order
    for component in reversed(LIFECYCLE_COMPONENTS):
        if component["shutdown"]:
            component_name = component["name"]
            try:
                logger.debug(f"stopping_{component_name.lower().replace(' ', '_')}")
                # Some shutdown functions need settings, others don't
                if component_name == "Permission Service":
                    await component["shutdown"](app, settings)  # type: ignore
                else:
                    await component["shutdown"](app)  # type: ignore
            except Exception as e:
                logger.error(
                    f"{component_name.lower().replace(' ', '_')}_shutdown_failed",
                    error=str(e),
                    component=component_name,
                )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional settings override. If None, uses get_settings().

    Returns:
        Configured FastAPI application instance.
    """
    if settings is None:
        settings = get_settings()
    # Configure logging based on settings BEFORE any module uses logger
    # This is needed for reload mode where the app is re-imported

    import structlog

    # Only configure if not already configured or if no file handler exists
    # okay we have the first debug line but after uvicorn start they are not show root_logger = logging.getLogger()
    # for h in root_logger.handlers:
    #     print(h)
    # has_file_handler = any(
    #     isinstance(h, logging.FileHandler) for h in root_logger.handlers
    # )

    if not structlog.is_configured():
        # Only setup logging if structlog is not configured at all
        # Always use console output, but respect file logging from settings
        json_logs = False
        setup_logging(
            json_logs=json_logs,
            log_level_name=settings.server.log_level,
            log_file=settings.server.log_file,
        )

    app = FastAPI(
        title="CCProxy API Server",
        description="High-performance API server providing Anthropic and OpenAI-compatible interfaces for Claude AI models",
        version=__version__,
        lifespan=lifespan,
    )

    # Setup middleware
    setup_cors_middleware(app, settings)
    setup_error_handlers(app)

    # Add request content logging middleware first (will run fourth due to middleware order)
    app.add_middleware(RequestContentLoggingMiddleware)

    # Add custom access log middleware second (will run third due to middleware order)
    app.add_middleware(AccessLogMiddleware)

    # Add request ID middleware fourth (will run first to initialize context)
    app.add_middleware(RequestIDMiddleware)

    # Add server header middleware (for non-proxy routes)
    # You can customize the server name here
    app.add_middleware(ServerHeaderMiddleware, server_name="uvicorn")

    # Include health router (always enabled)
    app.include_router(health_router, tags=["health"])

    # Include observability routers with granular controls
    if settings.observability.metrics_endpoint_enabled:
        app.include_router(prometheus_router, tags=["metrics"])

    if settings.observability.logs_endpoints_enabled:
        app.include_router(logs_router, prefix="/logs", tags=["logs"])

    if settings.observability.dashboard_enabled:
        app.include_router(dashboard_router, tags=["dashboard"])

    app.include_router(oauth_router, prefix="/oauth", tags=["oauth"])

    # Codex routes for OpenAI integration
    app.include_router(codex_router, tags=["codex"])

    # New /sdk/ routes for Claude SDK endpoints
    app.include_router(claude_router, prefix="/sdk", tags=["claude-sdk"])

    # New /api/ routes for proxy endpoints (includes OpenAI-compatible /v1/chat/completions)
    app.include_router(proxy_router, prefix="/api", tags=["proxy-api"])

    # Shared models endpoints for both SDK and proxy APIs
    app.include_router(models_router, prefix="/sdk", tags=["claude-sdk", "models"])
    app.include_router(models_router, prefix="/api", tags=["proxy-api", "models"])

    # Confirmation endpoints for SSE streaming and responses (conditional on builtin_permissions)
    if settings.claude.builtin_permissions:
        app.include_router(
            permissions_router, prefix="/permissions", tags=["permissions"]
        )
        setup_mcp(app)

    # Mount static files for dashboard SPA
    from pathlib import Path

    # Get the path to the dashboard static files
    current_file = Path(__file__)
    project_root = (
        current_file.parent.parent.parent
    )  # ccproxy/api/app.py -> project root
    dashboard_static_path = project_root / "ccproxy" / "static" / "dashboard"

    # Mount dashboard static files if they exist
    if dashboard_static_path.exists():
        # Mount the _app directory for SvelteKit assets at the correct base path
        app_path = dashboard_static_path / "_app"
        if app_path.exists():
            app.mount(
                "/dashboard/_app",
                StaticFiles(directory=str(app_path)),
                name="dashboard-assets",
            )

        # Mount favicon.svg at root level
        favicon_path = dashboard_static_path / "favicon.svg"
        if favicon_path.exists():
            # For single files, we'll handle this in the dashboard route or add a specific route
            pass

    return app


def get_app() -> FastAPI:
    """Get the FastAPI application instance.

    Returns:
        FastAPI application instance.
    """
    return create_app()
