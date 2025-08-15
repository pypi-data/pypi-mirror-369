"""
Enterprise Event System for UnrealOn SDK v1.0

Layer 2: Enterprise Services - Type-safe event handling with:
- Pydantic v2 validation for all events
- Event correlation and tracking
- Performance monitoring and metrics
- Event replay and audit capabilities 
- Real-time event streaming via WebSocket
- Circuit breaker and error recovery

Enterprise Features:
- Type-safe event dispatching with Pydantic validation
- Event correlation tracking across requests
- Performance metrics and analytics
- Audit trails and compliance logging
- Real-time subscription management
- Circuit breaker for fault tolerance
- Event replay for debugging and analytics
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any, Union, Awaitable
from collections import defaultdict, deque

# Pydantic v2 for all data models
from pydantic import BaseModel, Field, ConfigDict

# Auto-generated models - use these for WebSocket communication
from unrealon_sdk.src.clients.python_websocket.events import SocketEvent, EventType
from unrealon_sdk.src.clients.python_websocket.types import LogEntryMessage

# DTO models for type-safe data structures
from unrealon_sdk.src.dto.events import (
    EventPriority,
    EventDeliveryStatus,
    EventSubscriptionFilter,
    EventMetadata,
    EventDeliveryResult,
    EventStatistics,
)

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.core.exceptions import ConnectionError  # Use existing exception type
from unrealon_sdk.src.utils import generate_correlation_id

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logging.development import DevelopmentLogger

logger = logging.getLogger(__name__)


# EventPriority and EventDeliveryStatus moved to unrealon_sdk.dto.events


# EventSubscriptionFilter and EventMetadata moved to unrealon_sdk.dto.events


class EnterpriseEvent(BaseModel):
    """
    Enterprise-grade event model with full type safety.

    Wraps auto-generated events with enterprise features while
    maintaining compatibility with WebSocket communication.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    event_type: SocketEvent = Field(..., description="Socket event type")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    metadata: EventMetadata = Field(..., description="Event metadata")

    def to_websocket_message(self) -> LogEntryMessage:
        """Convert to WebSocket message format for transmission."""
        return LogEntryMessage(
            type="event",
            session_id=self.metadata.correlation_id,
            entry={
                "event_type": self.event_type.value,
                "data": self.data,
                "metadata": self.metadata.model_dump(),
                "timestamp": self.metadata.timestamp.isoformat(),
            },
            timestamp=self.metadata.timestamp.isoformat(),
        )


class EventSubscription(BaseModel):
    """Type-safe event subscription configuration."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    subscription_id: str = Field(..., description="Unique subscription identifier")
    subscriber_id: str = Field(..., description="Subscriber identifier")
    event_types: List[SocketEvent] = Field(..., description="Subscribed event types")
    filters: Optional[EventSubscriptionFilter] = Field(None, description="Event filters")
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    active: bool = Field(default=True, description="Subscription status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_event_received: Optional[datetime] = Field(None, description="Last event timestamp")
    events_received: int = Field(default=0, description="Total events received")


# EventDeliveryResult and EventStatistics moved to unrealon_sdk.dto.events


class EventHandler:
    """Type-safe event handler wrapper."""

    def __init__(
        self,
        handler: Callable[[EnterpriseEvent], Union[None, Awaitable[None]]],
        subscription: EventSubscription,
    ):
        self.handler = handler
        self.subscription = subscription
        self.call_count = 0
        self.last_called: Optional[datetime] = None
        self.errors: List[str] = []

    async def __call__(self, event: EnterpriseEvent) -> bool:
        """Execute handler with error handling and tracking."""
        try:
            self.call_count += 1
            self.last_called = datetime.now(timezone.utc)

            result = self.handler(event)
            if asyncio.iscoroutine(result):
                await result

            return True

        except Exception as e:
            error_msg = f"Handler error: {e}"
            self.errors.append(error_msg)
            logger.error(f"Event handler failed: {error_msg}")
            return False


class EnterpriseEventSystem:
    """
    Enterprise-grade event system for UnrealOn SDK.

    Features:
    - Type-safe event handling with Pydantic validation
    - Event correlation and tracking
    - Performance monitoring and metrics
    - Event replay and audit capabilities
    - Real-time subscription management
    - Circuit breaker pattern for fault tolerance
    """

    def __init__(self, config: AdapterConfig):
        """
        Initialize Enterprise Event System.

        Args:
            config: Adapter configuration
        """
        self.config = config
        self.logger = logger

        # Event management
        self._subscriptions: Dict[str, EventSubscription] = {}
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._event_history: deque[EnterpriseEvent] = deque(maxlen=1000)
        self._delivery_results: deque[EventDeliveryResult] = deque(maxlen=500)

        # Performance tracking
        self._statistics = EventStatistics()
        self._delivery_times: deque[float] = deque(maxlen=100)

        # Circuit breaker
        self._circuit_open = False
        self._circuit_failures = 0
        self._circuit_reset_time: Optional[datetime] = None
        self._max_failures = 5
        self._circuit_timeout = 60  # seconds

        # Background tasks
        self._background_tasks: List[asyncio.Task[Any]] = []
        self._shutdown_event = asyncio.Event()

        self.logger.info("Enterprise Event System initialized")

    async def subscribe(
        self,
        subscriber_id: str,
        event_types: List[SocketEvent],
        handler: Callable[[EnterpriseEvent], Union[None, Awaitable[None]]],
        filters: Optional[EventSubscriptionFilter] = None,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> str:
        """
        Subscribe to events with type-safe handler.

        Args:
            subscriber_id: Unique subscriber identifier
            event_types: List of event types to subscribe to
            handler: Event handler function (sync or async)
            filters: Optional event filters
            priority: Subscription priority

        Returns:
            Subscription ID
        """
        subscription_id = generate_correlation_id()

        subscription = EventSubscription(
            subscription_id=subscription_id,
            subscriber_id=subscriber_id,
            event_types=event_types,
            filters=filters,
            priority=priority,
            last_event_received=None,
        )

        self._subscriptions[subscription_id] = subscription

        # Create handler wrapper
        event_handler = EventHandler(handler, subscription)

        # Register handler for each event type
        for event_type in event_types:
            self._handlers[event_type.value].append(event_handler)

        self._statistics.active_subscriptions = len(self._subscriptions)

        self.logger.info(
            f"Subscription created: {subscription_id} for {subscriber_id}, "
            f"events: {[e.value for e in event_types]}"
        )

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: Subscription to remove

        Returns:
            True if unsubscribed successfully
        """
        if subscription_id not in self._subscriptions:
            return False

        subscription = self._subscriptions[subscription_id]

        # Remove handlers
        for event_type in subscription.event_types:
            handlers = self._handlers[event_type.value]
            self._handlers[event_type.value] = [
                h for h in handlers if h.subscription.subscription_id != subscription_id
            ]

        # Remove subscription
        del self._subscriptions[subscription_id]
        self._statistics.active_subscriptions = len(self._subscriptions)

        self.logger.info(f"Subscription removed: {subscription_id}")
        return True

    async def publish(
        self,
        event_type: SocketEvent,
        data: Dict[str, Any],
        source: str,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Publish event to all matching subscribers.

        Args:
            event_type: Type of event to publish
            data: Event payload data
            source: Event source identifier
            priority: Event priority level
            correlation_id: Optional correlation ID
            tags: Optional event tags

        Returns:
            Event ID
        """
        if self._circuit_open:
            if self._circuit_reset_time and datetime.now(timezone.utc) < self._circuit_reset_time:
                self.logger.warning("Circuit breaker open - event publishing suspended")
                raise ConnectionError("Event system circuit breaker is open")
            else:
                self._circuit_open = False
                self._circuit_failures = 0
                self.logger.info("Circuit breaker reset")

        # Create event metadata
        metadata = EventMetadata(
            event_id=generate_correlation_id(),
            correlation_id=correlation_id or generate_correlation_id(),
            source=source,
            priority=priority,
            tags=tags or [],
            expires_at=None,
        )

        # Create enterprise event
        event = EnterpriseEvent(event_type=event_type, data=data, metadata=metadata)

        # Add to history
        self._event_history.append(event)

        # Update statistics
        self._statistics.total_events_published += 1
        self._statistics.events_by_type[event_type.value] = (
            self._statistics.events_by_type.get(event_type.value, 0) + 1
        )
        self._statistics.events_by_priority[priority.value] = (
            self._statistics.events_by_priority.get(priority.value, 0) + 1
        )

        # Route event to subscribers
        await self._route_event(event)

        self.logger.debug(
            f"Event published: {event.metadata.event_id}, "
            f"type: {event_type.value}, source: {source}"
        )

        return event.metadata.event_id

    async def _route_event(self, event: EnterpriseEvent) -> None:
        """Route event to matching subscribers with error handling."""
        handlers = self._handlers.get(event.event_type.value, [])

        if not handlers:
            return

        delivery_tasks = []

        for handler in handlers:
            # Check if subscription matches filters
            if self._matches_filters(event, handler.subscription.filters):
                task = asyncio.create_task(self._deliver_event(event, handler))
                delivery_tasks.append(task)

        # Wait for all deliveries
        if delivery_tasks:
            results = await asyncio.gather(*delivery_tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self._handle_circuit_breaker_failure()
                    self.logger.error(f"Event delivery failed: {result}")

    def _matches_filters(
        self, event: EnterpriseEvent, filters: Optional[EventSubscriptionFilter]
    ) -> bool:
        """Check if event matches subscription filters."""
        if not filters:
            return True

        # Check event types
        if filters.event_types and event.event_type not in filters.event_types:
            return False

        # Check source pattern
        if filters.source_pattern and filters.source_pattern not in event.metadata.source:
            return False

        # Check priority minimum
        if filters.priority_min:
            priority_order = {
                EventPriority.LOW: 0,
                EventPriority.NORMAL: 1,
                EventPriority.HIGH: 2,
                EventPriority.CRITICAL: 3,
            }
            if priority_order[event.metadata.priority] < priority_order[filters.priority_min]:
                return False

        # Check correlation ID
        if filters.correlation_id and event.metadata.correlation_id != filters.correlation_id:
            return False

        # Check tags
        if filters.tags:
            if not any(tag in event.metadata.tags for tag in filters.tags):
                return False

        return True

    async def _deliver_event(self, event: EnterpriseEvent, handler: EventHandler) -> bool:
        """Deliver event to specific handler with tracking."""
        start_time = datetime.now(timezone.utc)
        delivery_id = generate_correlation_id()

        try:
            success = await handler(event)

            delivery_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self._delivery_times.append(delivery_time)

            # Update statistics
            if success:
                self._statistics.total_events_delivered += 1
                handler.subscription.events_received += 1
                handler.subscription.last_event_received = datetime.now(timezone.utc)
            else:
                self._statistics.total_delivery_failures += 1
                self._handle_circuit_breaker_failure()

            # Record delivery result
            result = EventDeliveryResult(
                delivery_id=delivery_id,
                event_id=event.metadata.event_id,
                subscription_id=handler.subscription.subscription_id,
                status=EventDeliveryStatus.DELIVERED if success else EventDeliveryStatus.FAILED,
                delivery_time_ms=delivery_time,
                error_message=None if success else "Handler returned False",
            )

            self._delivery_results.append(result)

            # Update average delivery time
            if self._delivery_times:
                self._statistics.average_delivery_time_ms = sum(self._delivery_times) / len(
                    self._delivery_times
                )

            return success

        except Exception as e:
            self._statistics.total_delivery_failures += 1
            self._handle_circuit_breaker_failure()

            # Record failed delivery
            result = EventDeliveryResult(
                delivery_id=delivery_id,
                event_id=event.metadata.event_id,
                subscription_id=handler.subscription.subscription_id,
                status=EventDeliveryStatus.FAILED,
                error_message=str(e),
                delivery_time_ms=None,
            )

            self._delivery_results.append(result)

            self.logger.error(f"Event delivery failed: {e}")
            return False

    def _handle_circuit_breaker_failure(self) -> None:
        """Handle circuit breaker logic for failure tracking."""
        self._circuit_failures += 1

        if self._circuit_failures >= self._max_failures:
            self._circuit_open = True
            self._circuit_reset_time = datetime.now(timezone.utc).replace(
                second=datetime.now(timezone.utc).second + self._circuit_timeout
            )
            self.logger.warning(
                f"Circuit breaker opened after {self._circuit_failures} failures. "
                f"Reset in {self._circuit_timeout} seconds."
            )

    def get_statistics(self) -> EventStatistics:
        """Get current event system statistics."""
        return self._statistics

    def get_subscription(self, subscription_id: str) -> Optional[EventSubscription]:
        """Get subscription by ID."""
        return self._subscriptions.get(subscription_id)

    def list_subscriptions(self, subscriber_id: Optional[str] = None) -> List[EventSubscription]:
        """List all subscriptions or filter by subscriber."""
        if subscriber_id:
            return [
                sub for sub in self._subscriptions.values() if sub.subscriber_id == subscriber_id
            ]
        return list(self._subscriptions.values())

    def get_event_history(
        self, event_types: Optional[List[SocketEvent]] = None, limit: int = 100
    ) -> List[EnterpriseEvent]:
        """Get recent event history with optional filtering."""
        events = list(self._event_history)

        if event_types:
            events = [e for e in events if e.event_type in event_types]

        return events[-limit:]

    async def shutdown(self) -> None:
        """Shutdown event system gracefully."""
        self.logger.info("Shutting down Enterprise Event System...")

        # Signal shutdown
        self._shutdown_event.set()

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self.logger.info("Enterprise Event System shutdown complete")


# Convenience function for creating event system
def create_event_system(config: AdapterConfig) -> EnterpriseEventSystem:
    """
    Create and configure Enterprise Event System.

    Args:
        config: Adapter configuration

    Returns:
        Configured event system instance
    """
    return EnterpriseEventSystem(config)


# Export all public components
__all__ = [
    # Core system
    "EnterpriseEventSystem",
    "create_event_system",
    # Models
    "EnterpriseEvent",
    "EventMetadata",
    "EventSubscription",
    "EventSubscriptionFilter",
    "EventDeliveryResult",
    "EventStatistics",
    # Enums
    "EventPriority",
    "EventDeliveryStatus",
    # Handler
    "EventHandler",
]
