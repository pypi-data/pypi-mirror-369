"""
Core type definitions for UnrealOn SDK v1.0

Contains basic types and enums used throughout the SDK.
For API-specific types, use auto-generated models from clients.
"""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass

from unrealon_sdk.src.core.metadata import SDKMetadata


@dataclass
class ConnectionState:
    """
    Tracks the connection state of the SDK.

    This is for internal SDK state management only.
    For API communication, use auto-generated models.
    """

    connected: bool = False
    connecting: bool = False
    last_connected: Optional[datetime] = None
    last_disconnected: Optional[datetime] = None
    reconnect_count: int = 0
    error: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[SDKMetadata] = None

    def reset(self) -> None:
        """Reset connection state to initial values."""
        self.connected = False
        self.connecting = False
        self.reconnect_count = 0
        self.error = None
        self.session_id = None
        self.metadata = None

    def mark_connected(self, session_id: Optional[str] = None) -> None:
        """Mark as connected."""
        self.connected = True
        self.connecting = False
        self.last_connected = datetime.utcnow()
        self.error = None
        if session_id:
            self.session_id = session_id

    def mark_disconnected(self, error: Optional[str] = None) -> None:
        """Mark as disconnected."""
        self.connected = False
        self.connecting = False
        self.last_disconnected = datetime.utcnow()
        if error:
            self.error = error

    def mark_connecting(self) -> None:
        """Mark as connecting."""
        self.connecting = True
        self.error = None

    def mark_reconnecting(self) -> None:
        """Mark as reconnecting."""
        self.reconnect_count += 1
        self.connecting = True
        self.connected = False
