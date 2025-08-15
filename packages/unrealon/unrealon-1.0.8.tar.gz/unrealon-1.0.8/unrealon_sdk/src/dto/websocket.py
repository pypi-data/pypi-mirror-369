"""
WebSocket-related Data Transfer Objects

Custom DTO models for WebSocket connection management and state tracking.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class WebSocketConnectionState(str, Enum):
    """
    WebSocket connection state constants.
    
    Compatible with WebSocket client events and internal state management.
    """
    
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class WebSocketStateInfo(BaseModel):
    """
    Type-safe WebSocket connection state model.

    Replaces Dict[str, str] usage to comply with CRITICAL_REQUIREMENTS.md.
    Provides structured state information for WebSocket connections.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Core connection state
    status: WebSocketConnectionState = Field(..., description="Connection status")
    session_id: Optional[str] = Field(None, description="Session identifier")
    last_ping: Optional[str] = Field(None, description="Last ping timestamp")
    connection_time: Optional[str] = Field(None, description="Connection establishment time")

    # Additional state fields
    connected: bool = Field(default=False, description="Connection established")
    connecting: bool = Field(default=False, description="Connection in progress")
    error: Optional[str] = Field(None, description="Last error message")
    last_connected: Optional[str] = Field(None, description="Last successful connection time")
    reconnect_count: int = Field(default=0, description="Number of reconnection attempts")


__all__ = [
    "WebSocketConnectionState",
    "WebSocketStateInfo",
]
