"""
Python WebSocket Client for UnrealServer

Asyncio-based WebSocket client with automatic reconnection,
event routing, and full type safety.

Usage:
    from python_websocket import WebSocketClient, SocketEvent
    
    client = WebSocketClient("ws://localhost:8000")
    await client.connect()
    
    await client.emit(SocketEvent.PING, {"message": "hello"})
"""

__version__ = "1.0.0"

from .client import WebSocketClient, WebSocketConfig, ConnectionState, WebSocketRoutes
from .events import SocketEvent, EventType

__all__ = [
    "WebSocketClient",
    "WebSocketConfig", 
    "ConnectionState",
    "WebSocketRoutes",
    "SocketEvent",
    "EventType",
]