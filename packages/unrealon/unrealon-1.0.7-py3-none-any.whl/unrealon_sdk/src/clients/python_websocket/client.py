"""
UnrealServer Python WebSocket Client

Asyncio-based WebSocket client with automatic reconnection,
event routing, and full type safety.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

import socketio
from pydantic import BaseModel, Field

from .events import SocketEvent, EventType


logger = logging.getLogger(__name__)


@dataclass
class WebSocketConfig:
    """Configuration for WebSocket client."""
    
    url: str
    auto_connect: bool = True
    reconnection_attempts: int = 5
    reconnection_delay: float = 1
    timeout: float = 10
    namespace: str = "/"
    auth: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Socket.IO client expects HTTP URLs, not WebSocket URLs
        # Keep HTTP/HTTPS format for proper Socket.IO connection
        
        # Add default headers
        if "User-Agent" not in self.headers:
            self.headers["User-Agent"] = "UnrealServer-Python-WebSocket-Client/1.0"


@dataclass
class ConnectionState:
    """Current state of WebSocket connection."""
    
    connected: bool = False
    connecting: bool = False
    error: Optional[str] = None
    last_connected: Optional[datetime] = None
    reconnect_count: int = 0
    

class WebSocketClient:
    """
    UnrealServer WebSocket Client with automatic reconnection.
    
    Features:
    - Automatic reconnection with exponential backoff
    - Event-based message handling
    - Type-safe event emission
    - Connection state management
    - Async/await support
    
    Usage:
        client = WebSocketClient("ws://localhost:8080")
        await client.connect()
        
        @client.on(SocketEvent.MESSAGE_RECEIVED)
        async def handle_message(data):
            print(f"Received: {data}")
        
        await client.emit(SocketEvent.PING, {"timestamp": "now"})
    """
    
    def __init__(self, config: Union[str, WebSocketConfig]):
        if isinstance(config, str):
            config = WebSocketConfig(url=config)
        
        self.config = config
        self.state = ConnectionState()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Initialize Socket.IO client
        # Note: Heartbeat/ping settings are managed by the server, client just responds
        # FIXED: Enable auto-reconnection (default Socket.IO behavior)
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=self.config.reconnection_attempts,
            reconnection_delay=self.config.reconnection_delay,
            logger=self.logger.getChild("socketio"),
            engineio_logger=self.logger.getChild("engineio")
        )
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Setup internal event handlers
        self._setup_internal_handlers()
    
    async def connect(self) -> bool:
        """
        Connect to WebSocket server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.state.connected or self.state.connecting:
            self.logger.debug("Already connected or connecting")
            return self.state.connected
        
        try:
            self.state.connecting = True
            self.state.error = None
            
            self.logger.info(f"Connecting to {self.config.url}")
            
            await self.sio.connect(
                url=self.config.url,
                headers=self.config.headers,
                auth=self.config.auth,
                namespaces=[self.config.namespace],
                wait_timeout=self.config.timeout
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.state.error = str(e)
            return False
        finally:
            self.state.connecting = False
    
    async def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        try:
            if self.sio.connected:
                await self.sio.disconnect()
            
            self.state.connected = False
            self.state.connecting = False
            self.logger.info("Disconnected from WebSocket server")
            
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
    
    async def emit(self, event: SocketEvent, data: Any = None) -> bool:
        """
        Emit event to server.
        
        Args:
            event: SocketEvent to emit
            data: Data to send with the event
            
        Returns:
            bool: True if emission successful, False otherwise
        """
        if not self.state.connected:
            self.logger.warning(f"Cannot emit {event.value}: not connected")
            return False
        
        try:
            # Serialize data if it's a Pydantic model
            if isinstance(data, BaseModel):
                data = data.model_dump()
            
            await self.sio.emit(event.value, data, namespace=self.config.namespace)
            self.logger.debug(f"Emitted event: {event.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to emit {event.value}: {e}")
            return False
    
    def on(self, event: SocketEvent):
        """
        Decorator for event handlers.
        
        Usage:
            @client.on(SocketEvent.MESSAGE_RECEIVED)
            async def handle_message(data):
                print(data)
        """
        def decorator(func: Callable):
            self.add_event_handler(event, func)
            return func
        return decorator
    
    def add_event_handler(self, event: SocketEvent, handler: Callable) -> None:
        """
        Add event handler for specific event.
        
        Args:
            event: SocketEvent to handle
            handler: Async function to call when event occurs
        """
        event_name = event.value
        
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        
        self._event_handlers[event_name].append(handler)
        
        # Register with Socket.IO client
        @self.sio.on(event_name, namespace=self.config.namespace)
        async def wrapper(data=None):
            await self._handle_event(event_name, data)
        
        self.logger.debug(f"Added handler for {event_name}")
    
    def remove_event_handler(self, event: SocketEvent, handler: Callable) -> None:
        """
        Remove specific event handler.
        
        Args:
            event: SocketEvent to remove handler from
            handler: Handler function to remove
        """
        event_name = event.value
        
        if event_name in self._event_handlers:
            try:
                self._event_handlers[event_name].remove(handler)
                self.logger.debug(f"Removed handler for {event_name}")
            except ValueError:
                self.logger.warning(f"Handler not found for {event_name}")
    
    async def wait_for_event(self, event: SocketEvent, timeout: Optional[float] = None) -> Any:
        """
        Wait for a specific event to occur.
        
        Args:
            event: SocketEvent to wait for
            timeout: Maximum time to wait (seconds)
            
        Returns:
            Event data when received
            
        Raises:
            asyncio.TimeoutError: If timeout is reached
        """
        return await self.sio.wait(event.value, namespace=self.config.namespace, timeout=timeout)
    
    async def _handle_event(self, event_name: str, data: Any) -> None:
        """
        Handle incoming event by calling registered handlers.
        
        Args:
            event_name: Name of the event
            data: Event data
        """
        try:
            handlers = self._event_handlers.get(event_name, [])
            
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    self.logger.error(f"Error in handler for {event_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error handling event {event_name}: {e}")
    
    def _setup_internal_handlers(self) -> None:
        """Setup internal Socket.IO event handlers."""
        
        @self.sio.on('connect', namespace=self.config.namespace)
        async def on_connect():
            self.state.connected = True
            self.state.connecting = False
            self.state.last_connected = datetime.utcnow()
            self.state.reconnect_count = 0
            self.state.error = None
            self.logger.info("✅ Connected to WebSocket server")
        
        @self.sio.on('disconnect', namespace=self.config.namespace)
        async def on_disconnect():
            self.state.connected = False
            self.state.connecting = False
            self.logger.info("❌ Disconnected from WebSocket server")
        
        @self.sio.on('connect_error', namespace=self.config.namespace)
        async def on_connect_error(data):
            self.state.connecting = False
            self.state.error = str(data) if data else "Connection error"
            self.state.reconnect_count += 1
            self.logger.error(f"💥 Connection error: {data}")
        
        # Setup handlers for all known socket events
        @self.sio.on('connect', namespace=self.config.namespace)
        async def on_connect_handler(data=None):
            await self._handle_event('connect', data)
        @self.sio.on('disconnect', namespace=self.config.namespace)
        async def on_disconnect_handler(data=None):
            await self._handle_event('disconnect', data)
        @self.sio.on('ping', namespace=self.config.namespace)
        async def on_ping_handler(data=None):
            await self._handle_event('ping', data)
        @self.sio.on('pong', namespace=self.config.namespace)
        async def on_pong_handler(data=None):
            await self._handle_event('pong', data)
        @self.sio.on('parser_register', namespace=self.config.namespace)
        async def on_parser_register_handler(data=None):
            await self._handle_event('parser_register', data)
        @self.sio.on('parser_command', namespace=self.config.namespace)
        async def on_parser_command_handler(data=None):
            await self._handle_event('parser_command', data)
        @self.sio.on('parser_status', namespace=self.config.namespace)
        async def on_parser_status_handler(data=None):
            await self._handle_event('parser_status', data)
        @self.sio.on('parser_registered', namespace=self.config.namespace)
        async def on_parser_registered_handler(data=None):
            await self._handle_event('parser_registered', data)
        @self.sio.on('parser_disconnected', namespace=self.config.namespace)
        async def on_parser_disconnected_handler(data=None):
            await self._handle_event('parser_disconnected', data)
        @self.sio.on('command_request', namespace=self.config.namespace)
        async def on_command_request_handler(data=None):
            await self._handle_event('command_request', data)
        @self.sio.on('command_response', namespace=self.config.namespace)
        async def on_command_response_handler(data=None):
            await self._handle_event('command_response', data)
        @self.sio.on('command_status', namespace=self.config.namespace)
        async def on_command_status_handler(data=None):
            await self._handle_event('command_status', data)
        @self.sio.on('health_status', namespace=self.config.namespace)
        async def on_health_status_handler(data=None):
            await self._handle_event('health_status', data)
        @self.sio.on('health_check', namespace=self.config.namespace)
        async def on_health_check_handler(data=None):
            await self._handle_event('health_check', data)
        @self.sio.on('admin_subscribe', namespace=self.config.namespace)
        async def on_admin_subscribe_handler(data=None):
            await self._handle_event('admin_subscribe', data)
        @self.sio.on('admin_unsubscribe', namespace=self.config.namespace)
        async def on_admin_unsubscribe_handler(data=None):
            await self._handle_event('admin_unsubscribe', data)
        @self.sio.on('admin_broadcast', namespace=self.config.namespace)
        async def on_admin_broadcast_handler(data=None):
            await self._handle_event('admin_broadcast', data)
        @self.sio.on('admin_notification', namespace=self.config.namespace)
        async def on_admin_notification_handler(data=None):
            await self._handle_event('admin_notification', data)
        @self.sio.on('system_notification', namespace=self.config.namespace)
        async def on_system_notification_handler(data=None):
            await self._handle_event('system_notification', data)
        @self.sio.on('system_event', namespace=self.config.namespace)
        async def on_system_event_handler(data=None):
            await self._handle_event('system_event', data)
        @self.sio.on('maintenance_notification', namespace=self.config.namespace)
        async def on_maintenance_notification_handler(data=None):
            await self._handle_event('maintenance_notification', data)
        @self.sio.on('developer_message', namespace=self.config.namespace)
        async def on_developer_message_handler(data=None):
            await self._handle_event('developer_message', data)
        @self.sio.on('log_entry', namespace=self.config.namespace)
        async def on_log_entry_handler(data=None):
            await self._handle_event('log_entry', data)
        @self.sio.on('error', namespace=self.config.namespace)
        async def on_error_handler(data=None):
            await self._handle_event('error', data)
    
    @property
    def connected(self) -> bool:
        """Check if client is connected."""
        return self.state.connected
    
    @property
    def connecting(self) -> bool:
        """Check if client is connecting."""
        return self.state.connecting
    
    def get_state(self) -> ConnectionState:
        """Get current connection state."""
        return self.state
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# WebSocket event constants for easy access
class WS_EVENTS:
    """WebSocket event names for type safety and easy access."""
    
    # Socket.IO built-in events
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    
    # Custom events
    PING = 'ping'
    PONG = 'pong'
    PARSER_REGISTER = 'parser_register'
    PARSER_COMMAND = 'parser_command'
    PARSER_STATUS = 'parser_status'
    PARSER_REGISTERED = 'parser_registered'
    PARSER_DISCONNECTED = 'parser_disconnected'
    COMMAND_REQUEST = 'command_request'
    COMMAND_RESPONSE = 'command_response'
    COMMAND_STATUS = 'command_status'
    HEALTH_STATUS = 'health_status'
    HEALTH_CHECK = 'health_check'
    ADMIN_SUBSCRIBE = 'admin_subscribe'
    ADMIN_UNSUBSCRIBE = 'admin_unsubscribe'
    ADMIN_BROADCAST = 'admin_broadcast'
    ADMIN_NOTIFICATION = 'admin_notification'
    SYSTEM_NOTIFICATION = 'system_notification'
    SYSTEM_EVENT = 'system_event'
    MAINTENANCE_NOTIFICATION = 'maintenance_notification'
    DEVELOPER_MESSAGE = 'developer_message'
    LOG_ENTRY = 'log_entry'
    ERROR = 'error'


# WebSocket route constants for server communication
class WebSocketRoutes:
    """WebSocket endpoint routes for UnrealServer communication."""
    
    # Socket.IO endpoint for parser connections
    PARSER_CONNECTION_ENDPOINT = "/socket.io"
    # Socket.IO endpoint for developer dashboard connections
    CLIENT_CONNECTION_ENDPOINT = "/socket.io"
    
    @classmethod
    def get_parser_url(cls, base_url: str, parser_id: str) -> str:
        """
        Build parser WebSocket URL for server connection.
        
        Args:
            base_url: Server base URL (e.g., 'wss://api.unrealon.com')
            parser_id: Parser identifier
            
        Returns:
            Complete WebSocket URL for parser connection
            
        Example:
            >>> WebSocketRoutes.get_parser_url('wss://api.unrealon.com', 'amazon-parser')
            'wss://api.unrealon.com/socket.io'
        """
        base = base_url.rstrip('/')
        # For Socket.IO, parser_id is passed via auth, not URL path
        return f"{base}{cls.PARSER_CONNECTION_ENDPOINT}"
    
    @classmethod
    def get_client_url(cls, base_url: str, developer_id: str) -> str:
        """
        Build client/developer WebSocket URL for dashboard connection.
        
        Args:
            base_url: Server base URL
            developer_id: Developer identifier
            
        Returns:
            Complete WebSocket URL for client connection
        """
        base = base_url.rstrip('/')
        # For Socket.IO, developer_id is passed via auth, not URL path
        return f"{base}{cls.CLIENT_CONNECTION_ENDPOINT}"


# Convenience function for creating clients
def create_client(url: str, **kwargs) -> WebSocketClient:
    """
    Create a WebSocket client with the given URL.
    
    Args:
        url: WebSocket server URL
        **kwargs: Additional configuration options
        
    Returns:
        WebSocketClient: Configured client instance
    """
    config = WebSocketConfig(url=url, **kwargs)
    return WebSocketClient(config)