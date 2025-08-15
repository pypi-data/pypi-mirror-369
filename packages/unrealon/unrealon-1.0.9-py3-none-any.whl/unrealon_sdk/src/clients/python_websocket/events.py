"""
UnrealServer WebSocket Events and Types

Auto-generated from server models - DO NOT EDIT MANUALLY
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


class SocketEvent(str, Enum):
    """Socket.IO event names for WebSocket communication."""
    
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    PARSER_REGISTER = "parser_register"
    PARSER_COMMAND = "parser_command"
    PARSER_STATUS = "parser_status"
    PARSER_REGISTERED = "parser_registered"
    PARSER_DISCONNECTED = "parser_disconnected"
    COMMAND_REQUEST = "command_request"
    COMMAND_RESPONSE = "command_response"
    COMMAND_STATUS = "command_status"
    HEALTH_STATUS = "health_status"
    HEALTH_CHECK = "health_check"
    ADMIN_SUBSCRIBE = "admin_subscribe"
    ADMIN_UNSUBSCRIBE = "admin_unsubscribe"
    ADMIN_BROADCAST = "admin_broadcast"
    ADMIN_NOTIFICATION = "admin_notification"
    SYSTEM_NOTIFICATION = "system_notification"
    SYSTEM_EVENT = "system_event"
    MAINTENANCE_NOTIFICATION = "maintenance_notification"
    DEVELOPER_MESSAGE = "developer_message"
    LOG_ENTRY = "log_entry"
    ERROR = "error"
    
    def __str__(self) -> str:
        """String representation of the event."""
        return self.value


class EventType(str, Enum):
    """System event types."""
    
    START_PARSING = "start_parsing"
    STOP_PARSING = "stop_parsing"
    PAUSE_PARSING = "pause_parsing"
    RESUME_PARSING = "resume_parsing"
    GET_STATUS = "get_status"
    UPDATE_CONFIG = "update_config"
    HEALTH_CHECK = "health_check"
    
    def __str__(self) -> str:
        """String representation of the event type."""
        return self.value


class AdminWebSocketChannel(str, Enum):
    """Admin WebSocket channel types."""
    
    ADMIN_EVENTS = "admin_events"
    SYSTEM_METRICS = "admin_system_metrics"
    OPERATIONS = "admin_operations"
    ALERTS = "admin_alerts"
    CRITICAL_ALERTS = "admin_critical_alerts"
    WARNINGS = "admin_warnings"
    USER_ACTIVITY = "admin_user_activity"
    PROXY_STATUS = "admin_proxy_status"
    PARSER_STATUS = "admin_parser_status"
    REAL_TIME_ANALYTICS = "admin_real_time_analytics"
    
    def __str__(self) -> str:
        """String representation of the admin channel."""
        return self.value


class SubscriptionType(str, Enum):
    """WebSocket subscription types."""
    
    REAL_TIME_METRICS = "real_time_metrics"
    SYSTEM_ALERTS = "system_alerts"
    OPERATION_PROGRESS = "operation_progress"
    USER_ACTIVITIES = "user_activities"
    PROXY_UPDATES = "proxy_updates"
    PARSER_UPDATES = "parser_updates"
    CUSTOM_ANALYTICS = "custom_analytics"
    
    def __str__(self) -> str:
        """String representation of the subscription type."""
        return self.value


# ===============================================
# WebSocket Message Models
# ===============================================

class ConnectionInfo(BaseModel):
    """
    Pydantic model for WebSocket connection information.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ConnectionInfo",
        description="Pydantic model for WebSocket connection information."
    )

class ConnectionStats(BaseModel):
    """
    Pydantic model for WebSocket connection statistics.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ConnectionStats",
        description="Pydantic model for WebSocket connection statistics."
    )

class HealthStatus(BaseModel):
    """
    Pydantic model for WebSocket service health status.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="HealthStatus",
        description="Pydantic model for WebSocket service health status."
    )

class WebSocketMetrics(BaseModel):
    """
    Pydantic model for WebSocket performance metrics.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="WebSocketMetrics",
        description="Pydantic model for WebSocket performance metrics."
    )

class LogEntryMessage(BaseModel):
    """
    WebSocket message for log entry broadcast.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="LogEntryMessage",
        description="WebSocket message for log entry broadcast."
    )

class CommandMessage(BaseModel):
    """
    WebSocket message for command routing.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="CommandMessage",
        description="WebSocket message for command routing."
    )

class CommandCompletionMessage(BaseModel):
    """
    WebSocket message for command completion notification.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="CommandCompletionMessage",
        description="WebSocket message for command completion notification."
    )

class AdminBroadcastMessage(BaseModel):
    """
    WebSocket message for admin broadcast.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="AdminBroadcastMessage",
        description="WebSocket message for admin broadcast."
    )

class MaintenanceNotificationMessage(BaseModel):
    """
    WebSocket message for maintenance notifications.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="MaintenanceNotificationMessage",
        description="WebSocket message for maintenance notifications."
    )

class BroadcastResponse(BaseModel):
    """
    Response model for broadcast operations.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="BroadcastResponse",
        description="Response model for broadcast operations."
    )

class ParserMessageResponse(BaseModel):
    """
    Response model for parser message operations.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ParserMessageResponse",
        description="Response model for parser message operations."
    )

class DeveloperMessageResponse(BaseModel):
    """
    Response model for developer message operations.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="DeveloperMessageResponse",
        description="Response model for developer message operations."
    )

class ConnectionsResponse(BaseModel):
    """
    Response model for connections information.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ConnectionsResponse",
        description="Response model for connections information."
    )

class SystemNotificationResponse(BaseModel):
    """
    Response model for system notification broadcast.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="SystemNotificationResponse",
        description="Response model for system notification broadcast."
    )

class WebSocketEventBase(BaseModel):
    """
    Base model for all WebSocket events.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="WebSocketEventBase",
        description="Base model for all WebSocket events."
    )

class ConnectionEvent(BaseModel):
    """
    WebSocket connection established event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ConnectionEvent",
        description="WebSocket connection established event."
    )

class PongEvent(BaseModel):
    """
    WebSocket pong response event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="PongEvent",
        description="WebSocket pong response event."
    )

class ErrorEvent(BaseModel):
    """
    WebSocket error event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ErrorEvent",
        description="WebSocket error event."
    )

class ParserWebSocketRegistrationRequest(BaseModel):
    """
    Parser WebSocket session registration request - simple data model.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ParserWebSocketRegistrationRequest",
        description="Parser WebSocket session registration request - simple data model."
    )

class ParserRegisteredEvent(BaseModel):
    """
    Parser registration success event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ParserRegisteredEvent",
        description="Parser registration success event."
    )

class ParserCommandEvent(BaseModel):
    """
    Parser command execution event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ParserCommandEvent",
        description="Parser command execution event."
    )

class ParserStatusEvent(BaseModel):
    """
    Parser status update event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="ParserStatusEvent",
        description="Parser status update event."
    )

class NotificationEvent(BaseModel):
    """
    General notification event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="NotificationEvent",
        description="General notification event."
    )

class SystemEvent(BaseModel):
    """
    System-wide event.
    
    Auto-generated from server Pydantic model.
    """
    
    # Model fields will be defined based on server Pydantic model
    pass
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        title="SystemEvent",
        description="System-wide event."
    )


# ===============================================
# Utility Functions
# ===============================================

def get_event_by_name(name: str) -> Optional[SocketEvent]:
    """
    Get SocketEvent by name.
    
    Args:
        name: Event name
        
    Returns:
        SocketEvent if found, None otherwise
    """
    try:
        return SocketEvent(name)
    except ValueError:
        return None


def get_event_type_by_name(name: str) -> Optional[EventType]:
    """
    Get EventType by name.
    
    Args:
        name: Event type name
        
    Returns:
        EventType if found, None otherwise
    """
    try:
        return EventType(name)
    except ValueError:
        return None


def get_admin_channel_by_name(name: str) -> Optional[AdminWebSocketChannel]:
    """
    Get AdminWebSocketChannel by name.
    
    Args:
        name: Channel name
        
    Returns:
        AdminWebSocketChannel if found, None otherwise
    """
    try:
        return AdminWebSocketChannel(name)
    except ValueError:
        return None


def get_subscription_type_by_name(name: str) -> Optional[SubscriptionType]:
    """
    Get SubscriptionType by name.
    
    Args:
        name: Subscription type name
        
    Returns:
        SubscriptionType if found, None otherwise
    """
    try:
        return SubscriptionType(name)
    except ValueError:
        return None


def serialize_message(data: Any) -> Dict[str, Any]:
    """
    Serialize message data for WebSocket transmission.
    
    Args:
        data: Data to serialize
        
    Returns:
        Dict representation of the data
    """
    if isinstance(data, BaseModel):
        return data.model_dump()
    elif isinstance(data, dict):
        return data
    elif hasattr(data, '__dict__'):
        return data.__dict__
    else:
        return {"data": data}


def deserialize_message(data: Dict[str, Any], model_class: type) -> BaseModel:
    """
    Deserialize message data from WebSocket.
    
    Args:
        data: Raw message data
        model_class: Pydantic model class to deserialize to
        
    Returns:
        Deserialized model instance
        
    Raises:
        ValidationError: If data doesn't match model schema
    """
    if issubclass(model_class, BaseModel):
        return model_class.model_validate(data)
    else:
        raise ValueError(f"Model class {model_class} is not a Pydantic model")


# ===============================================
# Event Mapping
# ===============================================

# Map events to their typical message models (if applicable)
EVENT_MODEL_MAPPING = {
    SocketEvent.CONNECT: None,  # TODO: Map to appropriate model
    SocketEvent.DISCONNECT: None,  # TODO: Map to appropriate model
    SocketEvent.PING: None,  # TODO: Map to appropriate model
    SocketEvent.PONG: None,  # TODO: Map to appropriate model
    SocketEvent.PARSER_REGISTER: None,  # TODO: Map to appropriate model
    SocketEvent.PARSER_COMMAND: None,  # TODO: Map to appropriate model
    SocketEvent.PARSER_STATUS: None,  # TODO: Map to appropriate model
    SocketEvent.PARSER_REGISTERED: None,  # TODO: Map to appropriate model
    SocketEvent.PARSER_DISCONNECTED: None,  # TODO: Map to appropriate model
    SocketEvent.COMMAND_REQUEST: None,  # TODO: Map to appropriate model
    SocketEvent.COMMAND_RESPONSE: None,  # TODO: Map to appropriate model
    SocketEvent.COMMAND_STATUS: None,  # TODO: Map to appropriate model
    SocketEvent.HEALTH_STATUS: None,  # TODO: Map to appropriate model
    SocketEvent.HEALTH_CHECK: None,  # TODO: Map to appropriate model
    SocketEvent.ADMIN_SUBSCRIBE: None,  # TODO: Map to appropriate model
    SocketEvent.ADMIN_UNSUBSCRIBE: None,  # TODO: Map to appropriate model
    SocketEvent.ADMIN_BROADCAST: None,  # TODO: Map to appropriate model
    SocketEvent.ADMIN_NOTIFICATION: None,  # TODO: Map to appropriate model
    SocketEvent.SYSTEM_NOTIFICATION: None,  # TODO: Map to appropriate model
    SocketEvent.SYSTEM_EVENT: None,  # TODO: Map to appropriate model
    SocketEvent.MAINTENANCE_NOTIFICATION: None,  # TODO: Map to appropriate model
    SocketEvent.DEVELOPER_MESSAGE: None,  # TODO: Map to appropriate model
    SocketEvent.LOG_ENTRY: None,  # TODO: Map to appropriate model
    SocketEvent.ERROR: None,  # TODO: Map to appropriate model
}


# All available events as a list
ALL_EVENTS = list(SocketEvent)

# All available event types as a list  
ALL_EVENT_TYPES = list(EventType)

# All available admin channels as a list
ALL_ADMIN_CHANNELS = list(AdminWebSocketChannel)

# All available subscription types as a list
ALL_SUBSCRIPTION_TYPES = list(SubscriptionType)


# ===============================================
# Admin WebSocket Utilities
# ===============================================

def create_admin_subscription_request(
    channel: AdminWebSocketChannel,
    subscription_type: SubscriptionType,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create admin subscription request.
    
    Args:
        channel: Admin channel to subscribe to
        subscription_type: Type of subscription
        filters: Optional filters for subscription
        
    Returns:
        Dict containing subscription request data
    """
    return {
        "channel": channel.value,
        "subscription_type": subscription_type.value,
        "filters": filters or {},
        "timestamp": datetime.utcnow().isoformat(),
    }


def create_admin_unsubscribe_request(
    channel: AdminWebSocketChannel
) -> Dict[str, Any]:
    """
    Create admin unsubscribe request.
    
    Args:
        channel: Admin channel to unsubscribe from
        
    Returns:
        Dict containing unsubscribe request data
    """
    return {
        "channel": channel.value,
        "timestamp": datetime.utcnow().isoformat(),
    }