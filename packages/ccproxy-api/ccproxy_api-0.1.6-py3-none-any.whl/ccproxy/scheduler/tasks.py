"""Base scheduled task classes and task implementations."""

import asyncio
import contextlib
import random
import time
from abc import ABC, abstractmethod
from datetime import UTC
from typing import Any

import structlog


logger = structlog.get_logger(__name__)


class BaseScheduledTask(ABC):
    """
    Abstract base class for all scheduled tasks.

    Provides common functionality for task lifecycle management, error handling,
    and exponential backoff for failed executions.
    """

    def __init__(
        self,
        name: str,
        interval_seconds: float,
        enabled: bool = True,
        max_backoff_seconds: float = 300.0,
        jitter_factor: float = 0.25,
    ):
        """
        Initialize scheduled task.

        Args:
            name: Human-readable task name
            interval_seconds: Interval between task executions in seconds
            enabled: Whether the task is enabled
            max_backoff_seconds: Maximum backoff delay for failed tasks
            jitter_factor: Jitter factor for backoff randomization (0.0-1.0)
        """
        self.name = name
        self.interval_seconds = max(1.0, interval_seconds)
        self.enabled = enabled
        self.max_backoff_seconds = max_backoff_seconds
        self.jitter_factor = min(1.0, max(0.0, jitter_factor))

        self._consecutive_failures = 0
        self._last_run_time: float = 0
        self._running = False
        self._task: asyncio.Task[Any] | None = None

    @abstractmethod
    async def run(self) -> bool:
        """
        Execute the scheduled task.

        Returns:
            True if execution was successful, False otherwise
        """
        pass

    async def setup(self) -> None:
        """
        Perform any setup required before task execution starts.

        Called once when the task is first started. Override if needed.
        Default implementation does nothing.
        """
        # Default implementation - subclasses can override if needed
        return

    async def cleanup(self) -> None:
        """
        Perform any cleanup required after task execution stops.

        Called once when the task is stopped. Override if needed.
        Default implementation does nothing.
        """
        # Default implementation - subclasses can override if needed
        return

    def calculate_next_delay(self) -> float:
        """
        Calculate the delay before the next task execution.

        Returns exponential backoff delay for failed tasks, or normal interval
        for successful tasks, with optional jitter.

        Returns:
            Delay in seconds before next execution
        """
        if self._consecutive_failures == 0:
            base_delay = self.interval_seconds
        else:
            # Exponential backoff: interval * (2 ^ failures)
            base_delay = self.interval_seconds * (2**self._consecutive_failures)
            base_delay = min(base_delay, self.max_backoff_seconds)

        # Add jitter to prevent thundering herd
        if self.jitter_factor > 0:
            jitter = base_delay * self.jitter_factor * (random.random() - 0.5)
            base_delay += jitter

        return max(1.0, base_delay)

    async def start(self) -> None:
        """Start the scheduled task execution loop."""
        if self._running or not self.enabled:
            return

        self._running = True
        logger.debug("task_starting", task_name=self.name)

        try:
            await self.setup()
            self._task = asyncio.create_task(self._run_loop())
            logger.debug("task_started", task_name=self.name)
        except Exception as e:
            self._running = False
            logger.error(
                "task_start_failed",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    async def stop(self) -> None:
        """Stop the scheduled task execution loop."""
        if not self._running:
            return

        self._running = False
        logger.debug("task_stopping", task_name=self.name)

        # Cancel the running task
        if self._task and not self._task.done():
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

        try:
            await self.cleanup()
            logger.debug("task_stopped", task_name=self.name)
        except Exception as e:
            logger.error(
                "task_cleanup_failed",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )

    async def _run_loop(self) -> None:
        """Main execution loop for the scheduled task."""
        while self._running:
            try:
                start_time = time.time()

                # Execute the task
                success = await self.run()

                execution_time = time.time() - start_time

                if success:
                    self._consecutive_failures = 0
                    logger.debug(
                        "task_execution_success",
                        task_name=self.name,
                        execution_time=execution_time,
                    )
                else:
                    self._consecutive_failures += 1
                    logger.warning(
                        "task_execution_failed",
                        task_name=self.name,
                        consecutive_failures=self._consecutive_failures,
                        execution_time=execution_time,
                    )

                self._last_run_time = time.time()

                # Calculate delay before next execution
                delay = self.calculate_next_delay()

                if not success and self._consecutive_failures > 1:
                    logger.info(
                        "task_backoff_delay",
                        task_name=self.name,
                        consecutive_failures=self._consecutive_failures,
                        delay=delay,
                        max_backoff=self.max_backoff_seconds,
                    )

                # Wait for next execution or cancellation
                await asyncio.sleep(delay)

            except asyncio.CancelledError:
                logger.debug("task_cancelled", task_name=self.name)
                break
            except Exception as e:
                self._consecutive_failures += 1
                logger.error(
                    "task_execution_error",
                    task_name=self.name,
                    error=str(e),
                    error_type=type(e).__name__,
                    consecutive_failures=self._consecutive_failures,
                )

                # Use backoff delay for exceptions too
                backoff_delay = self.calculate_next_delay()
                await asyncio.sleep(backoff_delay)

    @property
    def is_running(self) -> bool:
        """Check if the task is currently running."""
        return self._running

    @property
    def consecutive_failures(self) -> int:
        """Get the number of consecutive failures."""
        return self._consecutive_failures

    @property
    def last_run_time(self) -> float:
        """Get the timestamp of the last execution."""
        return self._last_run_time

    def get_status(self) -> dict[str, Any]:
        """
        Get current task status information.

        Returns:
            Dictionary with task status details
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "running": self.is_running,
            "interval_seconds": self.interval_seconds,
            "consecutive_failures": self.consecutive_failures,
            "last_run_time": self.last_run_time,
            "next_delay": self.calculate_next_delay() if self.is_running else None,
        }


class PushgatewayTask(BaseScheduledTask):
    """Task for pushing metrics to Pushgateway periodically."""

    def __init__(
        self,
        name: str,
        interval_seconds: float,
        enabled: bool = True,
        max_backoff_seconds: float = 300.0,
    ):
        """
        Initialize pushgateway task.

        Args:
            name: Task name
            interval_seconds: Interval between pushgateway operations
            enabled: Whether task is enabled
            max_backoff_seconds: Maximum backoff delay for failures
        """
        super().__init__(
            name=name,
            interval_seconds=interval_seconds,
            enabled=enabled,
            max_backoff_seconds=max_backoff_seconds,
        )
        self._metrics_instance: Any | None = None

    async def setup(self) -> None:
        """Initialize metrics instance for pushgateway operations."""
        try:
            from ccproxy.observability.metrics import get_metrics

            self._metrics_instance = get_metrics()
            logger.debug("pushgateway_task_setup_complete", task_name=self.name)
        except Exception as e:
            logger.error(
                "pushgateway_task_setup_failed",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    async def run(self) -> bool:
        """Execute pushgateway metrics push."""
        try:
            if not self._metrics_instance:
                logger.warning("pushgateway_no_metrics_instance", task_name=self.name)
                return False

            if not self._metrics_instance.is_pushgateway_enabled():
                logger.debug("pushgateway_disabled", task_name=self.name)
                return True  # Not an error, just disabled

            success = bool(self._metrics_instance.push_to_gateway())

            if success:
                logger.debug("pushgateway_push_success", task_name=self.name)
            else:
                logger.warning("pushgateway_push_failed", task_name=self.name)

            return success

        except Exception as e:
            logger.error(
                "pushgateway_task_error",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False


class StatsPrintingTask(BaseScheduledTask):
    """Task for printing stats summary periodically."""

    def __init__(
        self,
        name: str,
        interval_seconds: float,
        enabled: bool = True,
    ):
        """
        Initialize stats printing task.

        Args:
            name: Task name
            interval_seconds: Interval between stats printing
            enabled: Whether task is enabled
        """
        super().__init__(
            name=name,
            interval_seconds=interval_seconds,
            enabled=enabled,
        )
        self._stats_collector_instance: Any | None = None
        self._metrics_instance: Any | None = None

    async def setup(self) -> None:
        """Initialize stats collector and metrics instances."""
        try:
            from ccproxy.config.settings import get_settings
            from ccproxy.observability.metrics import get_metrics
            from ccproxy.observability.stats_printer import get_stats_collector

            self._metrics_instance = get_metrics()
            settings = get_settings()
            self._stats_collector_instance = get_stats_collector(
                settings=settings.observability,
                metrics_instance=self._metrics_instance,
            )
            logger.debug("stats_printing_task_setup_complete", task_name=self.name)
        except Exception as e:
            logger.error(
                "stats_printing_task_setup_failed",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    async def run(self) -> bool:
        """Execute stats printing."""
        try:
            if not self._stats_collector_instance:
                logger.warning("stats_printing_no_collector", task_name=self.name)
                return False

            await self._stats_collector_instance.print_stats()
            logger.debug("stats_printing_success", task_name=self.name)
            return True

        except Exception as e:
            logger.error(
                "stats_printing_task_error",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False


class PricingCacheUpdateTask(BaseScheduledTask):
    """Task for updating pricing cache periodically."""

    def __init__(
        self,
        name: str,
        interval_seconds: float,
        enabled: bool = True,
        force_refresh_on_startup: bool = False,
        pricing_updater: Any | None = None,
    ):
        """
        Initialize pricing cache update task.

        Args:
            name: Task name
            interval_seconds: Interval between pricing updates
            enabled: Whether task is enabled
            force_refresh_on_startup: Whether to force refresh on first run
            pricing_updater: Injected pricing updater instance
        """
        super().__init__(
            name=name,
            interval_seconds=interval_seconds,
            enabled=enabled,
        )
        self.force_refresh_on_startup = force_refresh_on_startup
        self._pricing_updater = pricing_updater
        self._first_run = True

    async def setup(self) -> None:
        """Initialize pricing updater instance if not injected."""
        if self._pricing_updater is None:
            try:
                from ccproxy.config.pricing import PricingSettings
                from ccproxy.pricing.cache import PricingCache
                from ccproxy.pricing.updater import PricingUpdater

                # Create pricing components with dependency injection
                settings = PricingSettings()
                cache = PricingCache(settings)
                self._pricing_updater = PricingUpdater(cache, settings)
                logger.debug("pricing_update_task_setup_complete", task_name=self.name)
            except Exception as e:
                logger.error(
                    "pricing_update_task_setup_failed",
                    task_name=self.name,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise
        else:
            logger.debug(
                "pricing_update_task_using_injected_updater", task_name=self.name
            )

    async def run(self) -> bool:
        """Execute pricing cache update."""
        try:
            if not self._pricing_updater:
                logger.warning("pricing_update_no_updater", task_name=self.name)
                return False

            # Force refresh on first run if configured
            force_refresh = self._first_run and self.force_refresh_on_startup
            self._first_run = False

            if force_refresh:
                logger.info("pricing_update_force_refresh_startup", task_name=self.name)
                refresh_result = await self._pricing_updater.force_refresh()
                success = bool(refresh_result)
            else:
                # Regular update check
                pricing_data = await self._pricing_updater.get_current_pricing(
                    force_refresh=False
                )
                success = pricing_data is not None

            if success:
                logger.debug("pricing_update_success", task_name=self.name)
            else:
                logger.warning("pricing_update_failed", task_name=self.name)

            return success

        except Exception as e:
            logger.error(
                "pricing_update_task_error",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False


class PoolStatsTask(BaseScheduledTask):
    """Task for displaying pool statistics periodically."""

    def __init__(
        self,
        name: str,
        interval_seconds: float,
        enabled: bool = True,
        pool_manager: Any | None = None,
    ):
        """
        Initialize pool stats task.

        Args:
            name: Task name
            interval_seconds: Interval between stats display
            enabled: Whether task is enabled
            pool_manager: Injected pool manager instance
        """
        super().__init__(
            name=name,
            interval_seconds=interval_seconds,
            enabled=enabled,
        )
        self._pool_manager = pool_manager

    async def setup(self) -> None:
        """Initialize pool manager instance if not injected."""
        if self._pool_manager is None:
            logger.warning(
                "pool_stats_task_no_manager",
                task_name=self.name,
                message="Pool manager not injected, task will be disabled",
            )

    async def run(self) -> bool:
        """Display pool statistics."""
        try:
            if not self._pool_manager:
                return True  # Not an error, just no pool manager available

            # Get general pool stats (if available)
            general_pool = getattr(self._pool_manager, "_pool", None)
            general_stats = None
            if general_pool:
                general_stats = general_pool.get_stats()

            # Get session pool stats
            session_pool = getattr(self._pool_manager, "_session_pool", None)
            session_stats = None
            if session_pool:
                session_stats = await session_pool.get_stats()

            # Log pool statistics
            logger.debug(
                "pool_stats_report",
                task_name=self.name,
                general_pool={
                    "enabled": bool(general_pool),
                    "total_clients": general_stats.total_clients
                    if general_stats
                    else 0,
                    "available_clients": general_stats.available_clients
                    if general_stats
                    else 0,
                    "active_clients": general_stats.active_clients
                    if general_stats
                    else 0,
                    "connections_created": general_stats.connections_created
                    if general_stats
                    else 0,
                    "connections_closed": general_stats.connections_closed
                    if general_stats
                    else 0,
                    "acquire_count": general_stats.acquire_count
                    if general_stats
                    else 0,
                    "release_count": general_stats.release_count
                    if general_stats
                    else 0,
                    "health_check_failures": general_stats.health_check_failures
                    if general_stats
                    else 0,
                }
                if general_pool
                else None,
                session_pool={
                    "enabled": session_stats.get("enabled", False)
                    if session_stats
                    else False,
                    "total_sessions": session_stats.get("total_sessions", 0)
                    if session_stats
                    else 0,
                    "active_sessions": session_stats.get("active_sessions", 0)
                    if session_stats
                    else 0,
                    "max_sessions": session_stats.get("max_sessions", 0)
                    if session_stats
                    else 0,
                    "total_messages": session_stats.get("total_messages", 0)
                    if session_stats
                    else 0,
                    "session_ttl": session_stats.get("session_ttl", 0)
                    if session_stats
                    else 0,
                }
                if session_pool
                else None,
            )

            return True

        except Exception as e:
            logger.error(
                "pool_stats_task_error",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False


class VersionUpdateCheckTask(BaseScheduledTask):
    """Task for checking version updates periodically."""

    def __init__(
        self,
        name: str,
        interval_seconds: float,
        enabled: bool = True,
        startup_max_age_hours: float = 1.0,
    ):
        """
        Initialize version update check task.

        Args:
            name: Task name
            interval_seconds: Interval between version checks
            enabled: Whether task is enabled
            startup_max_age_hours: Maximum age in hours before running startup check
        """
        super().__init__(
            name=name,
            interval_seconds=interval_seconds,
            enabled=enabled,
        )
        self.startup_max_age_hours = startup_max_age_hours
        self._first_run = True

    async def run(self) -> bool:
        """Execute version update check."""
        try:
            from datetime import datetime

            from ccproxy.utils.version_checker import (
                VersionCheckState,
                compare_versions,
                fetch_latest_github_version,
                get_current_version,
                get_version_check_state_path,
                load_check_state,
                save_check_state,
            )

            state_path = get_version_check_state_path()
            current_time = datetime.now(UTC)

            # Check if we should run based on startup logic
            if self._first_run:
                self._first_run = False
                should_run_startup_check = False

                # Load existing state if available
                existing_state = await load_check_state(state_path)
                if existing_state:
                    # Check age of last check
                    time_diff = current_time - existing_state.last_check_at
                    age_hours = time_diff.total_seconds() / 3600

                    if age_hours > self.startup_max_age_hours:
                        should_run_startup_check = True
                        logger.debug(
                            "version_check_startup_needed",
                            task_name=self.name,
                            age_hours=age_hours,
                            max_age_hours=self.startup_max_age_hours,
                        )
                    else:
                        logger.debug(
                            "version_check_startup_skipped",
                            task_name=self.name,
                            age_hours=age_hours,
                            max_age_hours=self.startup_max_age_hours,
                        )
                        return True  # Skip this run
                else:
                    # No previous state, run check
                    should_run_startup_check = True
                    logger.debug("version_check_startup_no_state", task_name=self.name)

                if not should_run_startup_check:
                    return True

            # Fetch latest version from GitHub
            latest_version = await fetch_latest_github_version()
            if latest_version is None:
                logger.warning("version_check_fetch_failed", task_name=self.name)
                return False

            # Get current version
            current_version = get_current_version()

            # Save state
            new_state = VersionCheckState(
                last_check_at=current_time,
                latest_version_found=latest_version,
            )
            await save_check_state(state_path, new_state)

            # Compare versions
            if compare_versions(current_version, latest_version):
                logger.info(
                    "version_update_available",
                    task_name=self.name,
                    current_version=current_version,
                    latest_version=latest_version,
                    message=f"New version {latest_version} available! You are running {current_version}",
                )
            else:
                logger.debug(
                    "version_check_complete_no_update",
                    task_name=self.name,
                    current_version=current_version,
                    latest_version=latest_version,
                )

            return True

        except Exception as e:
            logger.error(
                "version_check_task_error",
                task_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False
