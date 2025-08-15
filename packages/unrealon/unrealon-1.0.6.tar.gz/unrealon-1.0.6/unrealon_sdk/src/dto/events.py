"""
Event-related Data Transfer Objects

Custom DTO models for enterprise event system functionality.
These models provide type-safe event handling with validation.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict

# Import auto-generated events for compatibility
from unrealon_sdk.src.clients.python_websocket.events import SocketEvent


class EventPriority(str, Enum):
    """Event priority levels for processing order."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventDeliveryStatus(str, Enum):
    """Event delivery status tracking."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    EXPIRED = "expired"


class EventSubscriptionFilter(BaseModel):
    """Type-safe event subscription filters."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    event_types: Optional[List[SocketEvent]] = Field(None, description="Filter by event types")
    source_pattern: Optional[str] = Field(None, description="Filter by source pattern")
    priority_min: Optional[EventPriority] = Field(None, description="Minimum priority level")
    correlation_id: Optional[str] = Field(None, description="Filter by correlation ID")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")


class EventMetadata(BaseModel):
    """Structured event metadata with full type safety."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    event_id: str = Field(..., description="Unique event identifier")
    correlation_id: str = Field(..., description="Request correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(..., description="Event source identifier")
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    tags: List[str] = Field(default_factory=list, description="Event tags for filtering")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    expires_at: Optional[datetime] = Field(None, description="Event expiration time")


class EventDeliveryResult(BaseModel):
    """Event delivery tracking and results."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    delivery_id: str = Field(..., description="Unique delivery identifier")
    event_id: str = Field(..., description="Event identifier")
    subscription_id: str = Field(..., description="Subscription identifier")
    status: EventDeliveryStatus = Field(..., description="Delivery status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(default=0, description="Retry attempts")
    delivery_time_ms: Optional[float] = Field(None, description="Delivery time in milliseconds")


@dataclass
class EventStatistics:
    """Event system performance statistics."""

    total_events_published: int = 0
    total_events_delivered: int = 0
    total_delivery_failures: int = 0
    active_subscriptions: int = 0
    average_delivery_time_ms: float = 0.0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_by_priority: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate delivery success rate."""
        total_attempted = self.total_events_delivered + self.total_delivery_failures
        if total_attempted == 0:
            return 100.0
        return (self.total_events_delivered / total_attempted) * 100.0


__all__ = [
    "EventPriority",
    "EventDeliveryStatus",
    "EventSubscriptionFilter",
    "EventMetadata",
    "EventDeliveryResult",
    "EventStatistics",
]
