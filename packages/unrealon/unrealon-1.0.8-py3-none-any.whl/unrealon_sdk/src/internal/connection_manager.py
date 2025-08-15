"""
Connection management for UnrealOn SDK v1.0

Handles WebSocket and HTTP connections to the UnrealOn Adapter with:
- Automatic reconnection
- Health monitoring
- Session management
- Error recovery
"""

import asyncio
import logging
from typing import Optional, Callable, Union, Awaitable, Any
from datetime import datetime

from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.core.models import ConnectionHealthStatus

# Also import from DTO for new features
from unrealon_sdk.src.dto.health import ConnectionHealthStatus as DTOConnectionHealthStatus
from unrealon_sdk.src.core.exceptions import ConnectionError, AuthenticationError
from unrealon_sdk.src.core.metadata import LoggingContextMetadata, SDKMetadata

# Use auto-generated models only - no custom models!
from unrealon_sdk.src.clients.python_websocket.types import ParserCommandEvent
from unrealon_sdk.src.clients.python_http.models import (
    ParserRegistrationRequest,
    ParserRegistrationResponse,
    LogLevel,
    LoggingRequest,
    HealthResponse,
    SuccessResponse,
    ErrorResponse,
)

# Import the wrapper clients we need to create
from .websocket_client import WebSocketClientWrapper
from .http_client import HTTPClientWrapper

# Development logging
from unrealon_sdk.src.enterprise.logging.development import (
    get_development_logger,
    SDKEventType,
    SDKContext,
    track_development_operation,
)


class ConnectionManager:
    """
    Manages connections to the UnrealOn Adapter.

    Provides:
    - WebSocket connection for real-time commands
    - HTTP connection for registration and status
    - Automatic reconnection with exponential backoff
    - Health monitoring and error recovery
    """

    def __init__(self, config: AdapterConfig, parser_id: str, logger: logging.Logger):
        """
        Initialize connection manager.

        Args:
            config: Adapter configuration
            parser_id: Unique parser identifier
            logger: Logger instance
        """
        self.config = config
        self.parser_id = parser_id
        self.logger = logger

        # Connection clients
        self._http_client: Optional[HTTPClientWrapper] = None
        self._websocket_client: Optional[WebSocketClientWrapper] = None

        # State tracking
        self._connected = False
        self._connecting = False
        self._reconnect_count = 0
        self._session_id: Optional[str] = None

        # Command handling
        self._command_handler: Optional[
            Callable[[ParserCommandEvent], Union[None, Awaitable[None]]]
        ] = None

        self.logger.debug(f"ConnectionManager initialized for parser {parser_id}")

    async def _call_handler(self, handler: Optional[Callable[..., Any]], *args: Any) -> None:
        """
        Safely call handler, supporting both sync and async handlers.

        Args:
            handler: Handler function (sync or async)
            *args: Arguments to pass to handler
        """
        if handler is None:
            return

        try:
            result = handler(*args)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            self.logger.error(f"Error in handler: {e}")

    async def connect(self) -> None:
        """
        Establish connections to the adapter.

        Raises:
            ConnectionError: If connection fails
        """
        if self._connected:
            self.logger.warning("Already connected to adapter")
            return

        if self._connecting:
            self.logger.warning("Connection already in progress")
            return

        self._connecting = True

        try:
            self.logger.info("Establishing connection to UnrealOn Adapter...")

            # Initialize HTTP client for registration
            self._http_client = HTTPClientWrapper(config=self.config, logger=self.logger)
            await self._http_client.connect()

            # Initialize WebSocket client for real-time communication
            self._websocket_client = WebSocketClientWrapper(
                config=self.config, parser_id=self.parser_id, logger=self.logger
            )

            # Set up event handlers
            self._websocket_client.set_command_handler(self._handle_websocket_command)
            self._websocket_client.set_connection_handler(self._handle_connection_event)

            # Connect WebSocket
            await self._websocket_client.connect()

            self._connected = True
            self._connecting = False
            self._reconnect_count = 0

            self.logger.info("Successfully connected to UnrealOn Adapter")

        except Exception as e:
            self._connecting = False
            self._connected = False
            self.logger.error(f"Failed to connect to adapter: {e}")
            raise ConnectionError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the adapter."""
        if not self._connected:
            self.logger.warning("Not connected to adapter")
            return

        try:
            self.logger.info("Disconnecting from UnrealOn Adapter...")

            if self._websocket_client:
                await self._websocket_client.disconnect()

            if self._http_client:
                await self._http_client.disconnect()

            self._connected = False
            self._session_id = None

            self.logger.info("Disconnected from UnrealOn Adapter")

        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
            raise

    async def reconnect(self) -> None:
        """
        Attempt to reconnect to the adapter.

        Uses exponential backoff for retry attempts.
        """
        if self._connecting:
            self.logger.warning("Reconnection already in progress")
            return

        self._reconnect_count += 1

        # Calculate backoff delay
        backoff_delay = min(2**self._reconnect_count, 60)  # Max 60 seconds

        self.logger.info(f"Attempting reconnection #{self._reconnect_count} in {backoff_delay}s...")
        await asyncio.sleep(backoff_delay)

        try:
            # Cleanup existing connections
            if self._connected:
                await self.disconnect()

            # Attempt new connection
            await self.connect()

            self.logger.info(f"Reconnection #{self._reconnect_count} successful")

        except Exception as e:
            self.logger.error(f"Reconnection #{self._reconnect_count} failed: {e}")
            raise

    async def register_parser(
        self, request: ParserRegistrationRequest
    ) -> ParserRegistrationResponse:
        """
        Register the parser with the adapter.

        Args:
            request: Registration request data

        Returns:
            Registration response

        Raises:
            ConnectionError: If not connected
            AuthenticationError: If authentication fails
        """
        if not self._http_client:
            raise ConnectionError("HTTP client not initialized")

        try:
            self.logger.info(f"Registering parser {request.parser_id} with adapter...")

            response = await self._http_client.register_parser(request)

            if response.success:
                self._session_id = response.parser_id
                self.logger.info(f"Parser {request.parser_id} registered successfully")
            else:
                self.logger.error(f"Parser registration failed: {response.error}")
                if response.error and "AUTH" in response.error.upper():
                    raise AuthenticationError(response.error or "Authentication failed")

            return response

        except Exception as e:
            self.logger.error(f"Parser registration failed: {e}")
            raise

    async def send_response(self, response: Union[SuccessResponse, ErrorResponse]) -> None:
        """
        Send command response back to adapter.

        Args:
            response: Command response to send

        Raises:
            ConnectionError: If not connected
        """
        if not self._websocket_client:
            raise ConnectionError("WebSocket client not initialized")

        try:
            await self._websocket_client.send_response(response)
            self.logger.debug(f"Sent response: {response.success}")

        except Exception as e:
            self.logger.error(f"Failed to send response: {e}")
            raise

    async def send_log(
        self, level: LogLevel, message: str, context: Optional[LoggingContextMetadata]
    ) -> None:
        """
        Send log entry to adapter.

        Args:
            level: Log level
            message: Log message
            context: Additional context
        """
        if not self.config.enable_logging or not self._websocket_client:
            return

        try:
            # Use proper Pydantic model for logging
            log_request = LoggingRequest(
                level=level,
                message=message,
                source=f"parser.{self.parser_id}",
                context=context.model_dump() if context else None,
                session_id=self._session_id,
                tags=[self.parser_id],  # Add parser_id as tag
            )

            await self._websocket_client.send_log(log_request)

        except Exception as e:
            self.logger.error(f"Failed to send log entry: {e}")

    def set_command_handler(
        self, handler: Callable[[ParserCommandEvent], Union[None, Awaitable[None]]]
    ) -> None:
        """
        Set the command handler function.

        Args:
            handler: Function to handle incoming commands
        """
        self._command_handler = handler
        self.logger.debug("Command handler registered")

    def is_connected(self) -> bool:
        """Check if connected to adapter."""
        return (
            self._connected
            and self._websocket_client is not None
            and self._websocket_client.is_connected()
        )

    def get_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self._session_id

    def get_reconnect_count(self) -> int:
        """Get number of reconnection attempts."""
        return self._reconnect_count

    async def _handle_websocket_command(self, command: ParserCommandEvent) -> None:
        """
        Handle incoming command from WebSocket.

        Args:
            command: Command event received
        """
        self.logger.debug(f"Received WebSocket command: {command.command_id}")

        await self._call_handler(self._command_handler, command)

        if self._command_handler is None:
            self.logger.warning(f"No command handler registered for command {command.command_id}")

    async def _handle_connection_event(
        self, event: str, data: Optional[SDKMetadata] = None
    ) -> None:
        """
        Handle WebSocket connection events.

        Args:
            event: Event type (connected, disconnected, error)
            data: Event data
        """
        self.logger.debug(f"WebSocket connection event: {event}")

        if event == "connected":
            self.logger.info("WebSocket connection established")
            self._connected = True  # Set connected on actual connection
        elif event == "disconnected":
            self.logger.warning("WebSocket connection lost")
            # Check if this is a real disconnection or normal cleanup
            if self._websocket_client and not self._websocket_client.is_connected():
                self._connected = False
                self.logger.info("Confirmed disconnection - will attempt reconnect")
            else:
                self.logger.debug("Disconnect event received but connection may still be active")
        elif event == "error":
            error_msg = getattr(data, "error", "Unknown error") if data else "Unknown error"
            self.logger.error(f"WebSocket connection error: {error_msg}")
            self._connected = False

    async def health_check(self) -> ConnectionHealthStatus:
        """
        Perform health check of all connections using Pydantic model.

        Returns:
            ConnectionHealthStatus model - no raw JSON!
        """
        components = {}

        # Check HTTP client - returns Pydantic model
        if self._http_client:
            http_health = await self._http_client.health_check()
            components["http"] = http_health.model_dump()

        # Check WebSocket client - returns Pydantic model
        if self._websocket_client:
            ws_health = await self._websocket_client.health_check()
            components["websocket"] = ws_health.model_dump()

        # Return Pydantic model - no raw JSON!
        return ConnectionHealthStatus(
            is_healthy=self.is_connected(),
            connection_quality=1.0 if self.is_connected() else 0.0,
            latency_ms=50.0,  # Could be measured dynamically
            uptime_seconds=0.0,  # Could track actual uptime
            last_heartbeat=datetime.now().isoformat(),
        )
