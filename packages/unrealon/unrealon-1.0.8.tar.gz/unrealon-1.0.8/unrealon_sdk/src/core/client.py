"""
Main AdapterClient for UnrealOn SDK v1.0

Provides the primary interface for parser integration with:
- Zero-configuration setup
- Type-safe operations
- Real-time communication
- Enterprise features out of the box
"""

import asyncio
import logging
import os
import subprocess
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional, Callable, List, Awaitable, Union

from .config import AdapterConfig
from .types import ConnectionState
from .exceptions import (
    UnrealOnError,
    ConnectionError,
    ConfigurationError,
    CommandError,
    RegistrationError,
)

# Use auto-generated models only!
from unrealon_sdk.src.clients.python_websocket.types import ParserCommandEvent, ServiceType
from unrealon_sdk.src.clients.python_http.models import (
    ParserRegistrationRequest,
    ParserRegistrationResponse,
    ServiceRegistrationDto,
    LogLevel,
    SuccessResponse,
    ErrorResponse,
    LoggingRequest,
)

# Internal components that we'll create
from unrealon_sdk.src.internal.connection_manager import ConnectionManager
from unrealon_sdk.src.internal.command_router import CommandRouter

from unrealon_sdk.src.utils import generate_correlation_id, format_duration

# Development logging
from unrealon_sdk.src.enterprise.logging.development import (
    initialize_development_logger,
    get_development_logger,
    SDKEventType,
    SDKContext,
    SDKSeverity,
    track_development_operation,
)

# Metadata models
from unrealon_sdk.src.core.metadata import LoggingContextMetadata


class AdapterClient:
    """
    Main client for UnrealOn Adapter integration.

    Provides enterprise-grade parsing orchestration with:
    - Zero-configuration setup
    - Type-safe operations
    - Real-time communication
    - Production monitoring

    Example:
        ```python
        from unrealon_sdk import AdapterClient, AdapterConfig

        config = AdapterConfig(
            api_key="up_dev_your_key",
            parser_id="my_parser",
            parser_name="My Parser"
        )
        adapter = AdapterClient(config)

        @adapter.on_command("parse_listing")
        async def handle_parsing(command: ParserCommandEvent) -> SuccessResponse:
            # Use type-safe Pydantic models
            result = MyListingData(
                title="Extracted data",
                price=15000000
            )
            return SuccessResponse(
                success=True,
                data=result.model_dump()
            )

        await adapter.start()
        ```
    """

    def __init__(self, config: AdapterConfig):
        """
        Initialize the AdapterClient.

        Args:
            config: Configuration for the adapter client
        """
        self.config = config
        self.parser_id = config.parser_id
        self.logger = self._setup_logging()

        # Internal components
        self._connection_manager: Optional[ConnectionManager] = None
        self._command_router = CommandRouter()
        self._command_handlers: Dict[
            str, Callable[[ParserCommandEvent], Awaitable[Union[SuccessResponse, ErrorResponse]]]
        ] = {}
        self._services: List[ServiceRegistrationDto] = []

        # State tracking
        self._connection_state = ConnectionState()
        self._running = False
        self._startup_complete = False

        self.logger.info(f"AdapterClient initialized for parser {self.parser_id}")

    def on_command(self, command_type: str) -> Callable[
        [Callable[[ParserCommandEvent], Awaitable[Union[SuccessResponse, ErrorResponse]]]],
        Callable[[ParserCommandEvent], Awaitable[Union[SuccessResponse, ErrorResponse]]],
    ]:
        """
        Decorator for registering command handlers.

        Args:
            command_type: Type of command to handle

        Returns:
            Decorator function

        Example:
            @adapter.on_command("parse_listing")
            async def handle_parsing(command: ParserCommandEvent) -> SuccessResponse:
                # Use type-safe parsing with Pydantic models
                result = ExtractedData(extracted="data")
                return SuccessResponse(success=True, data=result.model_dump())
        """

        def decorator(
            func: Callable[[ParserCommandEvent], Awaitable[Union[SuccessResponse, ErrorResponse]]]
        ) -> Callable:
            self._command_handlers[command_type] = func
            self._command_router.register_handler(command_type, func)
            self.logger.info(f"Registered handler for command type: {command_type}")
            return func

        return decorator

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the client with automatic log cleanup."""
        # Use standard logger - cleanup handled at module initialization
        logger = logging.getLogger(f"unrealon_sdk.{self.parser_id}")

        # Set log level based on configuration
        log_level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        log_level = LogLevel.INFO
        if self.config.logging_config:
            log_level = self.config.logging_config.log_level
        logger.setLevel(log_level_map.get(log_level, logging.INFO))

        # Add handlers if not exists
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # File handler - create logs directory if needed
            if self.config.logging_config and self.config.logging_config.log_file_path:
                log_path = self.config.logging_config.log_file_path
            else:
                # Create log path at SDK root level (one level up from unrealon_sdk/)
                sdk_root = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                log_path = os.path.join(sdk_root, "logs", "unrealon_sdk.log")

            os.makedirs(os.path.dirname(log_path), exist_ok=True)

            file_handler = RotatingFileHandler(
                log_path, maxBytes=50 * 1024 * 1024, backupCount=10  # 50MB
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"SDK logging configured - Console: ✅ File: {log_path}")

        return logger

    async def register_services(self, services: List[ServiceRegistrationDto]) -> None:
        """
        Register services that this parser provides.

        Args:
            services: List of services to register
        """
        self._services = services
        self.logger.info(f"Registered {len(services)} services")

    async def connect(self) -> None:
        """
        Establish connection to the UnrealOn Adapter.

        Raises:
            ConnectionError: If connection fails
            ConfigurationError: If configuration is invalid
        """
        try:
            self.logger.info("Connecting to UnrealOn Adapter...")

            # Initialize connection manager
            self._connection_manager = ConnectionManager(
                config=self.config, parser_id=self.parser_id, logger=self.logger
            )

            # Connect to adapter
            await self._connection_manager.connect()

            # Register parser and services
            await self._register_parser()

            # Setup command handling
            self._connection_manager.set_command_handler(self._handle_command)

            self._connection_state.mark_connected(self._connection_manager.get_session_id())

            self.logger.info("Successfully connected to UnrealOn Adapter")

        except Exception as e:
            self._connection_state.mark_disconnected(str(e))
            self.logger.error(f"Failed to connect to adapter: {e}")
            raise ConnectionError(f"Connection failed: {e}")

    def _ensure_default_service(self) -> None:
        """Ensure there's at least one service registered based on command handlers."""
        if not self._services:
            # Extract registered commands from handlers
            registered_commands = list(self._command_handlers.keys())

            # Create default service based on registered commands using proper Pydantic v2 model
            default_service = ServiceRegistrationDto(
                service_id=f"{self.parser_id}_service",
                service_name=f"{self.config.parser_name} Service",
                service_type=ServiceType.SCRAPER.value,  # Use valid ServiceType
                capabilities={
                    "commands": registered_commands if registered_commands else ["status"],
                    "features": self._get_enabled_features(),
                },
                config={
                    "timeout": self.config.request_timeout_ms,
                    "max_retries": self.config.max_retries,
                    "environment": self.config.environment,
                },
            )

            self._services = [default_service]
            self.logger.info(f"Created default service with commands: {registered_commands}")

    def _get_enabled_features(self) -> List[str]:
        """Get list of enabled features for service capabilities."""
        features = ["monitoring", "logging"]
        if self.config.enable_proxy_rotation:
            features.append("proxy_rotation")
        if self.config.enable_error_recovery:
            features.append("error_recovery")
        return features

    async def _register_parser(self) -> None:
        """Register this parser with the adapter using auto-generated client."""
        try:
            # Ensure we have at least one service before registration
            self._ensure_default_service()

            # Create typed registration request using auto-generated model
            registration_request = ParserRegistrationRequest(
                parser_id=self.parser_id,
                parser_name=self.config.parser_name,
                parser_type=self.config.parser_type,
                api_key=self.config.api_key,
                services=self._services,
                metadata={
                    "sdk_version": "1.0.0",
                    "environment": self.config.environment,
                    "features": {
                        "proxy_rotation": self.config.enable_proxy_rotation,
                        "monitoring": self.config.enable_monitoring,
                        "logging": self.config.enable_logging,
                    },
                },
            )

            if self._connection_manager is None:
                raise ConfigurationError("Connection manager not initialized")

            # Use auto-generated client for registration
            response = await self._connection_manager.register_parser(registration_request)

            if not response.success:
                raise RegistrationError(
                    f"Parser registration failed: {response.error or 'Unknown error'}"
                )

            self.logger.info(
                f"Parser registered successfully. Services: {response.registered_services or []}"
            )

        except Exception as e:
            self.logger.error(f"Parser registration failed: {e}")
            raise

    async def _handle_command(self, command: ParserCommandEvent) -> None:
        """
        Handle incoming commands from the adapter using command router.

        Args:
            command: Command event to handle
        """
        start_time = datetime.now()
        correlation_id = command.correlation_id or str(uuid.uuid4())

        self.logger.info(
            f"Received command {command.command_id} of type {command.command_type}",
            extra={"correlation_id": correlation_id},
        )

        try:
            # Use command router to handle the command
            response = await self._command_router.route_command(command)

            # Send response back to adapter
            await self._send_response(response)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(
                f"Command {command.command_id} completed in {execution_time:.2f}ms",
                extra={"correlation_id": correlation_id},
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Send error response
            response = ErrorResponse(
                success=False, message=str(e), error_code=getattr(e, "error_code", "UNKNOWN_ERROR")
            )

            await self._send_response(response)

            self.logger.error(
                f"Command {command.command_id} failed after {execution_time:.2f}ms: {e}",
                extra={"correlation_id": correlation_id},
            )

    async def _send_response(self, response: Union[SuccessResponse, ErrorResponse]) -> None:
        """Send command response back to adapter."""
        if self._connection_manager is None:
            raise ConnectionError("Not connected to adapter")

        await self._connection_manager.send_response(response)

    def _kill_existing_parser_processes(self) -> None:
        """Kill existing parser processes to avoid port conflicts."""
        try:
            # Simple approach: kill processes by script name + parser_id in process name
            script_name = f"{self.config.parser_id}.py"
            current_pid = os.getpid()

            # Find processes running the same parser script
            result = subprocess.run(
                ["pgrep", "-f", script_name], capture_output=True, text=True, timeout=3
            )

            if result.returncode == 0 and result.stdout.strip():
                pids = [int(p.strip()) for p in result.stdout.strip().split("\n") if p.strip()]
                for pid in pids:
                    if pid != current_pid:  # Don't kill ourselves
                        try:
                            subprocess.run(["kill", "-TERM", str(pid)], timeout=1)
                            self.logger.info(f"🔄 Killed existing parser: PID {pid}")
                        except:
                            pass  # Ignore errors, process might be already dead

        except Exception:
            # Ignore all errors - this is just cleanup, not critical
            pass

    async def start(self) -> None:
        """
        Start the adapter client and begin processing commands.

        This method will:
        0. Kill existing parser processes to avoid conflicts
        1. Connect to the adapter
        2. Register the parser and services
        3. Start listening for commands
        """
        if self._running:
            self.logger.warning("AdapterClient is already running")
            return

        try:
            # Kill existing parser processes first
            self._kill_existing_parser_processes()

            await self.connect()
            self._running = True
            self._startup_complete = True

            self.logger.info("AdapterClient started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start AdapterClient: {e}")
            raise

    async def stop(self) -> None:
        """
        Stop the adapter client and disconnect from the adapter.
        """
        if not self._running:
            self.logger.warning("AdapterClient is not running")
            return

        try:
            self._running = False

            # Stop command router
            await self._command_router.shutdown()

            if self._connection_manager:
                await self._connection_manager.disconnect()

            self._connection_state.mark_disconnected()
            self.logger.info("AdapterClient stopped successfully")

        except Exception as e:
            self.logger.error(f"Error stopping AdapterClient: {e}")
            raise

    async def run_forever(self) -> None:
        """
        Keep the adapter client running indefinitely.

        This method will block until the client is stopped.
        """
        if not self._startup_complete:
            await self.start()

        try:
            self.logger.info("AdapterClient running indefinitely. Press Ctrl+C to stop.")

            while self._running:
                await asyncio.sleep(1)

                # Health check and reconnection logic
                if self._connection_manager:
                    is_connected = self._connection_manager.is_connected()
                    if not is_connected:
                        # Debug: Check detailed connection status
                        websocket_client = getattr(self._connection_manager, '_websocket_client', None)
                        if websocket_client:
                            connection_established = getattr(websocket_client, '_connection_established', False)
                            client_connected = getattr(websocket_client._client, 'connected', False) if hasattr(websocket_client, '_client') else False
                            manager_connected = getattr(self._connection_manager, '_connected', False)
                            
                            self.logger.warning(f"🔍 Connection check details:")
                            self.logger.warning(f"   manager._connected: {manager_connected}")
                            self.logger.warning(f"   websocket._connection_established: {connection_established}")
                            self.logger.warning(f"   socketio_client.connected: {client_connected}")
                        
                        self.logger.warning("Connection lost, attempting to reconnect...")
                        try:
                            await self._connection_manager.reconnect()
                            self.logger.info("Reconnected successfully")
                        except Exception as e:
                            self.logger.error(f"Reconnection failed: {e}")
                            await asyncio.sleep(5)  # Wait before next attempt

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")

        finally:
            await self.stop()

    async def send_log(
        self, level: LogLevel, message: str, context: Optional[LoggingContextMetadata] = None
    ) -> None:
        """
        Send a log entry to the adapter.

        Args:
            level: Log level
            message: Log message
            context: Additional context
        """
        if self._connection_manager and self.config.enable_logging:
            await self._connection_manager.send_log(level, message, context or {})

    async def log_info(
        self, message: str, context: Optional[LoggingContextMetadata] = None
    ) -> None:
        """Send info level log."""
        await self.send_log(LogLevel.INFO, message, context)

    async def log_warning(
        self, message: str, context: Optional[LoggingContextMetadata] = None
    ) -> None:
        """Send warning level log."""
        await self.send_log(LogLevel.WARNING, message, context)

    async def log_error(
        self, message: str, context: Optional[LoggingContextMetadata] = None
    ) -> None:
        """Send error level log."""
        await self.send_log(LogLevel.ERROR, message, context)

    def get_connection_status(self) -> ConnectionState:
        """Get current connection status."""
        return self._connection_state

    def is_connected(self) -> bool:
        """Check if connected to adapter."""
        return self._connection_state.connected and (
            self._connection_manager is not None and self._connection_manager.is_connected()
        )

    def get_registered_commands(self) -> List[str]:
        """Get list of registered command types."""
        return list(self._command_handlers.keys())

    def get_registered_services(self) -> List[ServiceRegistrationDto]:
        """Get list of registered services."""
        return self._services.copy()

    # Context manager support
    async def __aenter__(self) -> "AdapterClient":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop()
