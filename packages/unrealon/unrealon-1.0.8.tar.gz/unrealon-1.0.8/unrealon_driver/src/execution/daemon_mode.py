"""
Daemon Mode implementation for UnrealOn Driver v3.0

Production WebSocket service mode with full unrealon_sdk integration.
Provides real-time parser execution via WebSocket commands.
"""

import asyncio
import signal
from typing import Any, Optional
from datetime import datetime

from unrealon_driver.src.dto.execution import (
    DaemonModeConfig,
    DaemonCommandResult,
    DaemonStatusResult,
    DaemonHealthResult,
    ErrorInfo,
)
from unrealon_driver.src.dto.services import WebSocketConfig


class DaemonMode:
    """
    🔌 Daemon Mode - Production WebSocket Service

    Full implementation with unrealon_sdk integration:
    - WebSocket connection via AdapterClient
    - Command handling and response
    - Graceful shutdown with signal handling
    - Health monitoring and status reporting
    - Automatic reconnection and error recovery
    """

    def __init__(self, parser: Any, config: DaemonModeConfig):
        """Initialize daemon mode."""
        self.parser = parser
        self.config = config
        self.logger = parser.logger
        self._is_running = False
        self._shutdown_event = asyncio.Event()

    async def start(
        self, server: Optional[str] = None, api_key: Optional[str] = None, **kwargs
    ):
        """Start daemon mode with full WebSocket integration."""
        if self.logger:
            self.logger.info(f"🔌 Starting daemon mode for: {self.parser.parser_name}")

        # Get connection parameters
        server_url = server or self.config.server_url or kwargs.get("server_url")
        api_key = (
            api_key or self.config.api_key or kwargs.get("api_key")
        )

        if not server_url:
            if self.logger:
                self.logger.error(
                    "❌ WebSocket server URL not configured for daemon mode!"
                )
                self.logger.info("   Set server URL in config or pass as parameter")
            return

        if not api_key:
            if self.logger:
                self.logger.error(
                    "❌ WebSocket API key not configured for daemon mode!"
                )
                self.logger.info("   Set API key in config or pass as parameter")
            return

        if self.logger:
            self.logger.info(f"🔌 Starting WebSocket daemon mode")
            self.logger.info(f"   Server: {server_url}")
            self.logger.info(f"   Parser: {self.parser.parser_id}")
            self.logger.info(
                f"   API Key: {'***' + api_key[-4:] if len(api_key) > 4 else '***'}"
            )

        # Setup WebSocket service configuration with type safety
        websocket_config = WebSocketConfig(
            server_url=server_url,
            api_key=api_key,
            parser_name=self.parser.parser_name,
            auto_reconnect=self.config.auto_reconnect,
            health_check_interval=self.config.health_check_interval,
            max_reconnect_attempts=self.config.max_reconnect_attempts,
            connection_timeout=self.config.connection_timeout,
        )

        # Configure WebSocket service
        self.parser.websocket.config = websocket_config

        # Register command handlers
        self.parser.websocket.register_handler(
            "parse_command", self._handle_parse_command
        )
        self.parser.websocket.register_handler(
            "status_request", self._handle_status_request
        )
        self.parser.websocket.register_handler(
            "health_check", self._handle_health_check
        )

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

        try:
            await self.parser.setup() if hasattr(self.parser, "setup") else None

            # Connect to WebSocket server
            success = await self.parser.websocket.connect(
                server_url=server_url, api_key=api_key
            )

            if not success:
                if self.logger:
                    self.logger.error("❌ Failed to connect to WebSocket server")
                return

            if self.logger:
                self.logger.info("✅ Connected to WebSocket server")
                self.logger.info("👂 Listening for parse commands...")
                self.logger.info(
                    "   Commands: 'parse_command', 'status_request', 'health_check'"
                )
                self.logger.info("   Press Ctrl+C to stop")

            self._is_running = True

            # Start listening for commands with graceful shutdown
            await self.parser.websocket.listen(shutdown_event=self._shutdown_event)

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Daemon mode error: {e}")
            raise
        finally:
            await self.stop()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            if self.logger:
                self.logger.info(f"\n🛑 Shutdown signal received (signal {signum})...")
            self._shutdown_event.set()

        # Register signal handlers
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not register signal handlers: {e}")

    async def _handle_parse_command(self, command: dict) -> DaemonCommandResult:
        """Handle parse command from WebSocket with type safety."""

        start_time = datetime.now()

        try:
            if self.logger:
                self.logger.info("🚀 Received parse command via WebSocket")

            # Setup parser if needed
            if hasattr(self.parser, "setup"):
                await self.parser.setup()

            # Execute parse method
            result = await self.parser.parse()

            # Cleanup if needed
            if hasattr(self.parser, "cleanup"):
                await self.parser.cleanup()

            duration = (datetime.now() - start_time).total_seconds()
            items_count = len(result) if isinstance(result, (list, dict)) else 1

            if self.logger:
                self.logger.info(
                    f"✅ Parse command completed in {duration:.2f}s - {items_count} items"
                )

            return DaemonCommandResult(
                status="success",
                data=result if isinstance(result, dict) else {"result": result},
                items_processed=items_count,
                duration_seconds=duration,
                parser_id=self.parser.parser_id,
                timestamp=datetime.now().isoformat(),
                error=None,
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            if self.logger:
                self.logger.error(f"❌ Parse command failed after {duration:.2f}s: {e}")

            error_info = ErrorInfo(
                message=str(e),
                error_type=type(e).__name__,
                error_code=getattr(e, "error_code", None),
                traceback=None,
                context={"command": "parse", "parser_id": self.parser.parser_id},
            )

            return DaemonCommandResult(
                status="error",
                data=None,
                items_processed=0,
                duration_seconds=duration,
                parser_id=self.parser.parser_id,
                timestamp=datetime.now().isoformat(),
                error=error_info,
            )

    async def _handle_status_request(self, command: dict) -> DaemonStatusResult:
        """Handle status request from WebSocket with type safety."""

        try:
            health = await self.parser.health_check()

            return DaemonStatusResult(
                status="success",
                parser_id=self.parser.parser_id,
                parser_name=self.parser.parser_name,
                daemon_running=self._is_running,
                health=health,
                timestamp=datetime.now().isoformat(),
                error=None,
            )

        except Exception as e:
            error_info = ErrorInfo(
                message=str(e),
                error_type=type(e).__name__,
                error_code=getattr(e, "error_code", None),
                traceback=None,
                context={"command": "status", "parser_id": self.parser.parser_id},
            )

            return DaemonStatusResult(
                status="error",
                parser_id=self.parser.parser_id,
                parser_name=self.parser.parser_name,
                daemon_running=self._is_running,
                health=None,
                timestamp=datetime.now().isoformat(),
                error=error_info,
            )

    async def _handle_health_check(self, command: dict) -> DaemonHealthResult:
        """Handle health check from WebSocket with type safety."""

        try:
            health = await self.parser.health_check()

            # Type-safe health check - assume health is dict
            status = "healthy" if health.get("status") == "healthy" else "unhealthy"

            return DaemonHealthResult(
                status=status,
                data=health,
                parser_id=self.parser.parser_id,
                timestamp=datetime.now().isoformat(),
                error=None,
            )

        except Exception as e:
            error_info = ErrorInfo(
                message=str(e),
                error_type=type(e).__name__,
                error_code=getattr(e, "error_code", None),
                traceback=None,
                context={"command": "health_check", "parser_id": self.parser.parser_id},
            )

            return DaemonHealthResult(
                status="unhealthy",
                data=None,
                parser_id=self.parser.parser_id,
                timestamp=datetime.now().isoformat(),
                error=error_info,
            )

    async def stop(self):
        """Stop daemon mode gracefully."""
        if self.logger:
            self.logger.info("🛑 Stopping daemon mode...")

        self._is_running = False
        self._shutdown_event.set()

        # Disconnect WebSocket
        try:
            await self.parser.websocket.disconnect()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error disconnecting WebSocket: {e}")

        # Cleanup parser
        try:
            if hasattr(self.parser, "cleanup"):
                await self.parser.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during parser cleanup: {e}")

        if self.logger:
            self.logger.info("✅ Daemon mode stopped")

    def __repr__(self) -> str:
        return (
            f"<DaemonMode(running={self._is_running}, parser={self.parser.parser_id})>"
        )
