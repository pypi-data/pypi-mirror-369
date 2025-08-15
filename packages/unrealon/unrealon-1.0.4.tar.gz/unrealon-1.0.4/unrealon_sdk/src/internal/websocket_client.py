"""
WebSocket client wrapper for UnrealOn SDK v1.0

Wraps the auto-generated WebSocket client with SDK-specific functionality:
- Type-safe event handling
- Automatic reconnection with exponential backoff
- Command routing integration
- Health monitoring
- Error recovery
"""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any, Union, Awaitable
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.core.exceptions import WebSocketError, ConnectionError
from unrealon_sdk.src.clients.python_http.models import ConnectionStats
from unrealon_sdk.src.clients.python_websocket.client import WebSocketClient, WebSocketConfig
from unrealon_sdk.src.clients.python_websocket.events import SocketEvent
from unrealon_sdk.src.clients.python_websocket import WebSocketRoutes
from unrealon_sdk.src.clients.python_websocket.types import (
    ParserCommandEvent,
    ParserWebSocketRegistrationRequest,
)
from unrealon_sdk.src.clients.python_http.models import SuccessResponse, ErrorResponse

# Import from centralized logging service
from unrealon_sdk.src.enterprise.logging.service import LoggingRequest

# Use DTO models for type-safe data structures
from unrealon_sdk.src.dto.websocket import WebSocketConnectionState, WebSocketStateInfo
from unrealon_sdk.src.utils import generate_correlation_id


# WebSocketConnectionState moved to unrealon_sdk.dto.websocket


class WebSocketClientWrapper:
    """
    Wrapper for auto-generated WebSocket client.

    Provides SDK-specific functionality while using the generated client
    for actual WebSocket communication.

    Features:
    - Automatic reconnection with exponential backoff
    - Type-safe event handling with Pydantic validation
    - Command routing integration
    - Health monitoring and diagnostics
    - Error recovery and circuit breaker pattern
    """

    def __init__(self, config: AdapterConfig, parser_id: str, logger: logging.Logger):
        """
        Initialize WebSocket client wrapper.

        Args:
            config: Adapter configuration
            parser_id: Unique parser identifier
            logger: Logger instance
        """
        self.config = config
        self.parser_id = parser_id
        self.logger = logger

        # Create WebSocket configuration from adapter config
        # Build parser-specific WebSocket URL using generated routes
        parser_ws_url = WebSocketRoutes.get_parser_url(config.server_url, parser_id)

        ws_config = WebSocketConfig(
            url=parser_ws_url,  # Use parser-specific endpoint from generated routes
            auto_connect=False,  # We handle connection manually
            reconnection_attempts=5,
            reconnection_delay=1,
            timeout=config.request_timeout_ms / 1000,  # Convert to seconds
            auth={"api_key": config.api_key, "parser_id": parser_id},
            headers={"User-Agent": f"UnrealOn-SDK/1.0 Parser/{parser_id}"},
        )

        # Initialize the generated WebSocket client
        self._client = WebSocketClient(ws_config)

        # Event handlers (can be sync or async)
        self._command_handler: Optional[
            Callable[[ParserCommandEvent], Union[None, Awaitable[None]]]
        ] = None
        self._connection_handler: Optional[Callable[[str, Any], Union[None, Awaitable[None]]]] = (
            None
        )

        # State tracking
        self._reconnect_count = 0
        self._last_ping: Optional[datetime] = None
        self._connection_established = False

        # Setup internal event handlers
        self._setup_event_handlers()

        self.logger.debug(f"WebSocketClientWrapper initialized for parser {parser_id}")

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

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for the generated WebSocket client."""

        @self._client.on(SocketEvent.CONNECT)  # type: ignore[misc]
        async def on_connect(data: Any) -> None:
            """Handle WebSocket connection established."""
            self._connection_established = True
            self._reconnect_count = 0
            self._last_ping = datetime.utcnow()

            self.logger.info("WebSocket connection established")

            # Small delay to ensure Socket.IO client is fully ready to emit
            await asyncio.sleep(0.1)

            # Send parser registration to server using auto-generated Pydantic v2 model
            try:
                developer_id = "dev_integration_test"  # Extract from API key if needed

                registration_request = ParserWebSocketRegistrationRequest(
                    parser_id=self.parser_id, developer_id=developer_id
                )

                # Use the underlying Socket.IO client directly for proper event emission
                self.logger.debug(f"🔍 Emitting parser_register: event={SocketEvent.PARSER_REGISTER.value}, data={registration_request.model_dump()}")
                await self._client.sio.emit(
                    SocketEvent.PARSER_REGISTER.value, 
                    registration_request.model_dump(),
                    namespace='/'
                )
                self.logger.debug(f"🔍 Emit completed successfully")
                self.logger.info(f"🚀 Sent parser registration: {self.parser_id}")
            except Exception as e:
                self.logger.error(f"Failed to send parser registration: {e}")

            await self._call_handler(
                self._connection_handler, "connected", {"timestamp": datetime.utcnow().isoformat()}
            )

        @self._client.on(SocketEvent.DISCONNECT)  # type: ignore[misc]
        async def on_disconnect(data: Any) -> None:
            """Handle WebSocket disconnection."""
            self._connection_established = False

            self.logger.warning("WebSocket connection lost")

            await self._call_handler(
                self._connection_handler, "disconnected", {"reason": data or "unknown"}
            )

        @self._client.on(SocketEvent.PARSER_COMMAND)  # type: ignore[misc]
        async def on_parser_command(data: Any) -> None:
            """Handle incoming parser command."""
            try:
                # Validate and parse command using Pydantic
                command_event = ParserCommandEvent.model_validate(data)

                self.logger.debug(f"Received command: {command_event.command_id}")

                await self._call_handler(self._command_handler, command_event)

                if self._command_handler is None:
                    self.logger.warning(
                        f"No command handler registered for command {command_event.command_id}"
                    )

            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
                await self._call_handler(
                    self._connection_handler,
                    "error",
                    {"error": str(e), "context": "command_processing"},
                )

        @self._client.on(SocketEvent.PING)  # type: ignore[misc]
        async def on_ping(data: Any) -> None:
            """Handle ping from server."""
            self._last_ping = datetime.utcnow()

            # Respond with pong
            await self._client.emit(
                SocketEvent.PONG,
                {"timestamp": self._last_ping.isoformat(), "parser_id": self.parser_id},
            )

        @self._client.on(SocketEvent.ERROR)  # type: ignore[misc]
        async def on_error(data: Any) -> None:
            """Handle WebSocket errors."""
            error_msg = (
                data.get("message", "Unknown WebSocket error")
                if isinstance(data, dict)
                else str(data)
            )

            self.logger.error(f"WebSocket error: {error_msg}")

            await self._call_handler(
                self._connection_handler, "error", {"error": error_msg, "context": "websocket"}
            )

    async def connect(self) -> None:
        """
        Connect to WebSocket server.

        Raises:
            WebSocketError: If connection fails
        """
        try:
            self.logger.info(f"Connecting to WebSocket server: {self.config.server_url}")

            success = await self._client.connect()
            if not success:
                raise WebSocketError("Failed to establish WebSocket connection")

            # Wait for connection to be fully established
            timeout = self.config.request_timeout_ms / 1000
            start_time = datetime.utcnow()

            while not self._connection_established:
                if (datetime.utcnow() - start_time).total_seconds() > timeout:
                    raise WebSocketError("Connection timeout")
                await asyncio.sleep(0.1)

            self.logger.info("WebSocket connection established successfully")

        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            raise WebSocketError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        try:
            self.logger.info("Disconnecting from WebSocket server")

            await self._client.disconnect()
            self._connection_established = False

            self.logger.info("WebSocket disconnected successfully")

        except Exception as e:
            self.logger.error(f"Error during WebSocket disconnect: {e}")
            raise WebSocketError(f"Disconnect failed: {e}")

    async def reconnect(self) -> None:
        """
        Reconnect to WebSocket server with exponential backoff.

        Raises:
            WebSocketError: If reconnection fails
        """
        self._reconnect_count += 1

        # Calculate backoff delay (exponential with jitter)
        base_delay = min(2**self._reconnect_count, 60)  # Max 60 seconds
        jitter = base_delay * 0.1  # 10% jitter
        delay = base_delay + (jitter * (0.5 - asyncio.get_event_loop().time() % 1))

        self.logger.info(
            f"Attempting WebSocket reconnection #{self._reconnect_count} in {delay:.2f}s"
        )

        await asyncio.sleep(delay)

        try:
            # Disconnect first if needed
            if self._connection_established:
                await self.disconnect()

            # Attempt new connection
            await self.connect()

            self.logger.info(f"WebSocket reconnection #{self._reconnect_count} successful")

        except Exception as e:
            self.logger.error(f"WebSocket reconnection #{self._reconnect_count} failed: {e}")
            raise WebSocketError(f"Reconnection failed: {e}")

    async def send_response(self, response: Union[SuccessResponse, ErrorResponse]) -> None:
        """
        Send command response back to server.

        Args:
            response: Command response to send

        Raises:
            WebSocketError: If sending fails
        """
        if not self.is_connected():
            raise WebSocketError("Not connected to WebSocket server")

        try:
            # Convert response to dict for transmission
            response_data = response.model_dump()

            await self._client.emit(SocketEvent.COMMAND_RESPONSE, response_data)

            self.logger.debug(f"Sent response: {response.success}")

        except Exception as e:
            self.logger.error(f"Failed to send response: {e}")
            raise WebSocketError(f"Failed to send response: {e}")

    async def send_log(self, log_request: LoggingRequest) -> None:
        """
        Send log entry to server.

        Args:
            log_request: Log entry to send

        Raises:
            WebSocketError: If sending fails
        """
        if not self.is_connected():
            # Don't raise error for logging - just skip
            self.logger.debug("Skipping log transmission - not connected")
            return

        try:
            # Convert log request to dict for transmission
            log_data = log_request.model_dump()

            await self._client.emit(SocketEvent.LOG_ENTRY, log_data)

            self.logger.debug(f"Sent log entry: {log_request.level}")

        except Exception as e:
            self.logger.error(f"Failed to send log entry: {e}")
            # Don't raise error for logging failures

    def set_command_handler(
        self, handler: Callable[[ParserCommandEvent], Union[None, Awaitable[None]]]
    ) -> None:
        """
        Set command handler function.

        Args:
            handler: Function to handle incoming commands
        """
        self._command_handler = handler
        self.logger.debug("Command handler registered")

    def set_connection_handler(
        self, handler: Callable[[str, Any], Union[None, Awaitable[None]]]
    ) -> None:
        """
        Set connection event handler function.

        Args:
            handler: Function to handle connection events
        """
        self._connection_handler = handler
        self.logger.debug("Connection handler registered")

    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        # TEMPORARY FIX: Only check our internal flag, not auto-generated client flag
        # The auto-generated client's .connected flag becomes False incorrectly
        return self._connection_established

    def get_connection_state(self) -> WebSocketStateInfo:
        """Get current connection state as type-safe Pydantic model."""
        # Build state from our internal tracking (no raw dict usage)
        return WebSocketStateInfo(
            status=WebSocketConnectionState.CONNECTED if self.is_connected() else WebSocketConnectionState.DISCONNECTED,
            session_id=self.parser_id,
            last_ping=self._last_ping.isoformat() if self._last_ping else None,
            connection_time=getattr(self, "_connection_time", None),
            connected=self.is_connected(),
            connecting=getattr(self, "_connecting", False),
            error=None,  # Could be extended to track last error
            last_connected=self._last_ping.isoformat() if self._last_ping else None,
            reconnect_count=self._reconnect_count,
        )

    async def health_check(self) -> WebSocketStateInfo:
        """
        Perform health check of WebSocket connection.

        Returns:
            Type-safe WebSocketStateInfo model (NO raw Dict usage!)
        """
        return self.get_connection_state()

    def get_statistics(self) -> ConnectionStats:
        """
        Get WebSocket connection statistics.

        Returns:
            ConnectionStats with typed connection statistics
        """
        return ConnectionStats(
            total_connections=1 if self.is_connected() else 0,
            parser_connections=1 if self.is_connected() else 0,
            client_connections=1 if self.is_connected() else 0,
            active_rooms=0,  # Client doesn't track rooms
            max_connections=1,  # Single client connection
            metrics=None,  # Can be extended later
        )
