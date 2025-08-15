"""
Scheduled Mode implementation for UnrealOn Driver v3.0

Automated recurring execution with human-readable intervals.
Full implementation using enterprise SchedulerService.
"""

import asyncio
import signal
from typing import Any, Optional

from unrealon_driver.src.dto.execution import ScheduledModeConfig, ScheduledModeStatus
from unrealon_driver.src.dto.services import SchedulerConfig

from unrealon_driver.src.services.scheduler_service import SchedulerService


class ScheduledMode:
    """
    ⏰ Scheduled Mode - Automated Recurring Execution

    Full implementation with enterprise features:
    - Human-readable intervals ("30m", "1h", "daily")
    - Smart load balancing with jitter
    - Error recovery and retries
    - Health monitoring and alerting
    - Production-ready reliability
    """

    def __init__(self, parser: Any, config: ScheduledModeConfig):
        """Initialize scheduled mode."""
        self.parser = parser
        self.config = config
        self.logger = parser.logger
        self._is_running = False
        self._scheduler_service = None
        self._shutdown_event = asyncio.Event()

    async def start(self, every: str, at: Optional[str] = None, **kwargs):
        """Start scheduled execution with full enterprise features."""
        if self.logger:
            self.logger.info(
                f"⏰ Starting scheduled mode for: {self.parser.parser_name}"
            )
            self.logger.info(f"📅 Schedule: every {every}")
            if at:
                self.logger.info(f"🕘 At time: {at}")

        # Setup scheduler service with type safety
        scheduler_config = SchedulerConfig(
            parser_id=self.parser.parser_id,
            max_concurrent_tasks=kwargs.get(
                "max_concurrent", self.config.max_concurrent
            ),
            enable_jitter=kwargs.get("jitter", self.config.jitter),
            jitter_range=kwargs.get("jitter_range", self.config.jitter_range),
            default_timeout=kwargs.get("timeout", self.config.timeout),
            default_retries=kwargs.get("retry_attempts", self.config.retry_attempts),
            enable_task_monitoring=True,
            health_check_interval=60,
        )

        self._scheduler_service = SchedulerService(
            config=scheduler_config,
            logger=self.logger,
            metrics=self.parser.metrics if hasattr(self.parser, "metrics") else None,
        )

        # Create scheduled parse task with type safety
        self._scheduler_service.add_task(
            task_id=f"{self.parser.parser_id}_scheduled",
            name=f"Scheduled {self.parser.parser_name}",
            func=self._scheduled_parse_task,
            every=every,
            enabled=True,
            timeout=kwargs.get("timeout", 300),
            retry_attempts=kwargs.get("retry_attempts", 3),
            max_runs=kwargs.get("max_runs"),
        )

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

        self._is_running = True

        try:
            if self.logger:
                self.logger.info("✅ Scheduler configured successfully")
                self.logger.info("👂 Starting scheduled execution...")
                self.logger.info("   Press Ctrl+C to stop")

            # Start scheduler service
            await self._scheduler_service.start()

        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("⏹️  Scheduled mode interrupted")
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Scheduled mode error: {e}")
            raise
        finally:
            await self.stop()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            if self.logger:
                self.logger.info(f"\n🛑 Shutdown signal received (signal {signum})...")
            self._shutdown_event.set()

            # Stop scheduler
            if self._scheduler_service:
                asyncio.create_task(self._scheduler_service.stop())

        # Register signal handlers
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not register signal handlers: {e}")

    async def _scheduled_parse_task(self):
        """Scheduled parse task handler with full monitoring."""
        start_time = asyncio.get_event_loop().time()

        try:
            if self.logger:
                self.logger.info("🚀 Executing scheduled parse task")

            # Setup parser if needed
            if hasattr(self.parser, "setup"):
                await self.parser.setup()

            # Execute parse method
            result = await self.parser.parse()

            # Cleanup if needed
            if hasattr(self.parser, "cleanup"):
                await self.parser.cleanup()

            duration = asyncio.get_event_loop().time() - start_time
            items_count = len(result) if isinstance(result, (list, dict)) else 1

            if self.logger:
                self.logger.info(
                    f"✅ Scheduled task completed in {duration:.2f}s - {items_count} items"
                )

            return result

        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time

            if self.logger:
                self.logger.error(
                    f"❌ Scheduled task failed after {duration:.2f}s: {e}"
                )

            # Re-raise for scheduler error handling
            raise

    async def get_status(self) -> ScheduledModeStatus:
        """Get current scheduling status with type safety."""

        if not self._scheduler_service:
            return ScheduledModeStatus(
                status="not_started",
                is_running=False,
                parser_id=self.parser.parser_id,
                parser_name=self.parser.parser_name,
                scheduler_health=None,
            )

        health = await self._scheduler_service.health_check()
        return ScheduledModeStatus(
            status="running" if self._is_running else "stopped",
            is_running=self._is_running,
            parser_id=self.parser.parser_id,
            parser_name=self.parser.parser_name,
            scheduler_health=health,
        )

    async def stop(self):
        """Stop scheduled mode gracefully."""
        if self.logger:
            self.logger.info("🛑 Stopping scheduled mode...")

        self._is_running = False
        self._shutdown_event.set()

        # Stop scheduler service
        if self._scheduler_service:
            try:
                await self._scheduler_service.stop()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error stopping scheduler: {e}")

        if self.logger:
            self.logger.info("✅ Scheduled mode stopped")

    def __repr__(self) -> str:
        task_count = (
            len(self._scheduler_service._tasks) if self._scheduler_service else 0
        )
        return f"<ScheduledMode(running={self._is_running}, tasks={task_count})>"
