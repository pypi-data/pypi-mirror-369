"""Generated WebSocket Types for UnrealServer v3"""
"""Auto-generated from server models - DO NOT EDIT"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ParserStatus(str, Enum):
    """ParserStatus types."""
    REGISTERING = "registering"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class ParserType(str, Enum):
    """ParserType types."""
    ENCAR = "encar"
    MOBILE = "mobile"
    REALESTATE = "realestate"
    CUSTOM = "custom"
    GENERAL = "general"

class ProcessingPhase(str, Enum):
    """ProcessingPhase types."""
    INITIALIZING = "initializing"
    CONNECTING = "connecting"
    FETCHING_LISTINGS = "fetching_listings"
    PROCESSING_DETAILS = "processing_details"
    VALIDATING_DATA = "validating_data"
    FINALIZING = "finalizing"
    COMPLETED = "completed"

class CommandStatus(str, Enum):
    """CommandStatus types."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class CommandType(str, Enum):
    """CommandType types."""
    START_PARSING = "start_parsing"
    STOP_PARSING = "stop_parsing"
    PAUSE_PARSING = "pause_parsing"
    RESUME_PARSING = "resume_parsing"
    GET_STATUS = "get_status"
    UPDATE_CONFIG = "update_config"
    HEALTH_CHECK = "health_check"

class CommandPriority(str, Enum):
    """CommandPriority types."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ServiceStatus(str, Enum):
    """ServiceStatus types."""
    IDLE = "idle"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

class ServiceType(str, Enum):
    """ServiceType types."""
    SCRAPER = "scraper"
    CRAWLER = "crawler"
    MONITOR = "monitor"
    ANALYZER = "analyzer"
    EXTRACTOR = "extractor"

class AdminWebsocketChannel(str, Enum):
    """AdminWebsocketChannel types."""
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

class SubscriptionType(str, Enum):
    """SubscriptionType types."""
    REAL_TIME_METRICS = "real_time_metrics"
    SYSTEM_ALERTS = "system_alerts"
    OPERATION_PROGRESS = "operation_progress"
    USER_ACTIVITIES = "user_activities"
    PROXY_UPDATES = "proxy_updates"
    PARSER_UPDATES = "parser_updates"
    CUSTOM_ANALYTICS = "custom_analytics"

class AdminEventType(str, Enum):
    """AdminEventType types."""
    OPERATION_STARTED = "operation_started"
    OPERATION_PROGRESS = "operation_progress"
    OPERATION_COMPLETED = "operation_completed"
    OPERATION_ERROR = "operation_error"
    PROXY_STATUS_CHANGED = "proxy_status_changed"
    PROXY_INVENTORY_LOW = "proxy_inventory_low"
    PROXY_PROCUREMENT_COMPLETED = "proxy_procurement_completed"
    PROXY_VALIDATION_FAILED = "proxy_validation_failed"
    PARSER_CONNECTED = "parser_connected"
    PARSER_DISCONNECTED = "parser_disconnected"
    PARSER_ERROR = "parser_error"
    SYSTEM_THRESHOLD_BREACHED = "system_threshold_breached"
    SERVICE_ERROR = "service_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SYSTEM_DOWN = "system_down"
    ADMIN_ACTION_PERFORMED = "admin_action_performed"
    ADMIN_ACCESS_DENIED = "admin_access_denied"
    USER_MANAGEMENT = "user_management"

class SystemOperationType(str, Enum):
    """SystemOperationType types."""
    SERVICE_RESTART = "service_restart"
    SERVICE_STOP = "service_stop"
    SERVICE_START = "service_start"
    PARSER_RESTART = "parser_restart"
    PARSER_DISCONNECT = "parser_disconnect"
    SYSTEM_MAINTENANCE = "system_maintenance"
    CACHE_CLEAR = "cache_clear"
    LOG_ROTATION = "log_rotation"
    DATABASE_BACKUP = "database_backup"
    HEALTH_CHECK = "health_check"
    PERFORMANCE_TEST = "performance_test"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

class SystemComponentType(str, Enum):
    """SystemComponentType types."""
    PARSER = "parser"
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    WEBSOCKET = "websocket"
    PROXY_POOL = "proxy_pool"
    LOGGING = "logging"
    API_SERVER = "api_server"
    ENTIRE_SYSTEM = "entire_system"

class OperationPriority(str, Enum):
    """OperationPriority types."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class ProxyProvider(str, Enum):
    """ProxyProvider types."""
    PROXY6 = "proxy6"
    PROXY_CHEAP = "proxy_cheap"
    PROXY_SELLER = "proxy_seller"
    OXYLABS = "oxylabs"
    BRIGHT_DATA = "bright_data"

class ProxyStatus(str, Enum):
    """ProxyStatus types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    BLOCKED = "blocked"
    ERROR = "error"

class ProxyProtocol(str, Enum):
    """ProxyProtocol types."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

class ProxyRotationStrategy(str, Enum):
    """ProxyRotationStrategy types."""
    ROUND_ROBIN = "round_robin"
    SUCCESS_RATE = "success_rate"
    WEIGHTED_RANDOM = "weighted_random"
    LEAST_FAILURES = "least_failures"
    LEAST_USED = "least_used"

class WebSocketEventBase(BaseModel):
    """Base model for all WebSocket events."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")

class ConnectionEvent(BaseModel):
    """WebSocket connection established event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: str = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type")
    connection_type: str = Field(..., description="Connection type (parser/client)")
    message: str = Field(..., description="Connection message")

class PongEvent(BaseModel):
    """WebSocket pong response event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Pong data")

class ErrorEvent(BaseModel):
    """WebSocket error event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type")
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Any = Field(..., description="Additional error details")

class ParserWebSocketRegistrationRequest(BaseModel):
    """Parser WebSocket session registration request - simple data model."""

    parser_id: str = Field(..., description="Parser identifier")
    developer_id: str = Field(..., description="Developer identifier")

class ParserRegisteredEvent(BaseModel):
    """Parser registration success event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type")
    parser_id: str = Field(..., description="Parser identifier")
    status: str = Field(..., description="Registration status")
    capabilities: List[str] = Field(..., description="Parser capabilities")
    message: str = Field(..., description="Success message")

class ParserCommandEvent(BaseModel):
    """Parser command execution event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type (command_execute/command_result)")
    command_id: str = Field(..., description="Command identifier")
    parser_id: str = Field(..., description="Target parser identifier")
    command_type: str = Field(..., description="Command type")
    payload: Dict[str, Any] = Field(..., description="Command payload")
    status: Any = Field(..., description="Command status")

class ParserStatusEvent(BaseModel):
    """Parser status update event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type")
    parser_id: str = Field(..., description="Parser identifier")
    status: str = Field(..., description="Parser status")
    last_seen: str = Field(..., description="Last seen timestamp")
    metrics: Any = Field(..., description="Performance metrics")

class NotificationEvent(BaseModel):
    """General notification event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type")
    notification_type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    priority: str = Field(..., description="Notification priority")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class SystemEvent(BaseModel):
    """System-wide event."""

    timestamp: str = Field(..., description="Event timestamp")
    session_id: Any = Field(..., description="Session identifier")
    event_type: str = Field(..., description="Event type")
    system_event_type: str = Field(..., description="System event type")
    data: Dict[str, Any] = Field(..., description="System event data")
    affected_components: List[str] = Field(..., description="Affected components")

class LogEntryMessage(BaseModel):
    """WebSocket message for log entry broadcast."""

    type: str = Field(..., description="Message type")
    session_id: str = Field(..., description="Session identifier")
    entry: Dict[str, Any] = Field(..., description="Log entry data")
    timestamp: str = Field(..., description="Timestamp in ISO format")

class CommandMessage(BaseModel):
    """WebSocket message for command routing."""

    type: str = Field(..., description="Message type")
    command_id: str = Field(..., description="Command identifier")
    command: str = Field(..., description="Command to execute")
    parameters: Dict[str, Any] = Field(..., description="Command parameters")
    timeout: int = Field(..., description="Command timeout")
    priority: str = Field(..., description="Command priority")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")
    developer_id: str = Field(..., description="Developer identifier")
    timestamp: str = Field(..., description="Timestamp in ISO format")

class CommandCompletionMessage(BaseModel):
    """WebSocket message for command completion notification."""

    type: str = Field(..., description="Message type")
    command_id: str = Field(..., description="Command identifier")
    status: str = Field(..., description="Command completion status")
    parser_id: str = Field(..., description="Parser identifier")
    execution_time_ms: Any = Field(..., description="Execution time in milliseconds")
    completed_at: Any = Field(..., description="Completion timestamp in ISO format")
    has_result: bool = Field(..., description="Whether command has result data")
    has_error: bool = Field(..., description="Whether command has error")
    timestamp: str = Field(..., description="Timestamp in ISO format")

class AdminBroadcastMessage(BaseModel):
    """WebSocket message for admin broadcast."""

    message_id: str = Field(..., description="Unique broadcast message identifier")
    type: str = Field(..., description="Message type (admin_broadcast, etc.)")
    content: str = Field(..., description="Broadcast message content")
    priority: str = Field(..., description="Message priority level")
    timestamp: str = Field(..., description="Timestamp in ISO format")
    persistent: bool = Field(..., description="Whether message is persistent")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class MaintenanceNotificationMessage(BaseModel):
    """WebSocket message for maintenance notifications."""

    type: str = Field(..., description="Message type")
    message: str = Field(..., description="Maintenance notification message")
    maintenance_active: bool = Field(..., description="Whether maintenance is active")
    timestamp: str = Field(..., description="Timestamp in ISO format")
    grace_period_minutes: Any = Field(..., description="Grace period in minutes")
    affected_services: List[str] = Field(..., description="Affected services")

class ConnectionInfo(BaseModel):
    """Pydantic model for WebSocket connection information."""

    connected_at: str = Field(..., description="Connection establishment time")
    last_seen: str = Field(..., description="Last activity timestamp")
    auth: Any = Field(..., description="Authentication data")
    environ: Any = Field(..., description="ASGI environ data")
    parser_id: Any = Field(..., description="Associated parser ID")
    developer_id: Any = Field(..., description="Associated developer ID")
    connection_type: str = Field(..., description="Connection type")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class ConnectionStats(BaseModel):
    """Pydantic model for WebSocket connection statistics."""

    total_connections: int = Field(..., description="Total active connections")
    parser_connections: int = Field(..., description="Parser connections")
    client_connections: int = Field(..., description="Client connections")
    active_rooms: int = Field(..., description="Number of active rooms")
    max_connections: int = Field(..., description="Maximum allowed connections")
    metrics: Any = Field(..., description="Performance metrics")

class HealthStatus(BaseModel):
    """Pydantic model for WebSocket service health status."""

    status: str = Field(..., description="Health status")
    websocket_server: str = Field(..., description="WebSocket server type")
    active_connections: int = Field(..., description="Number of active connections")
    connected_parsers: int = Field(..., description="Number of connected parsers")
    connected_developers: int = Field(..., description="Number of connected developers")
    active_rooms: int = Field(..., description="Number of active rooms")
    max_connections: int = Field(..., description="Maximum allowed connections")
    metrics: Any = Field(..., description="Performance metrics")
    error: Any = Field(..., description="Error message if unhealthy")

class WebSocketMetrics(BaseModel):
    """Pydantic model for WebSocket performance metrics."""

    connections_opened: int = Field(..., description="Total connections opened")
    connections_closed: int = Field(..., description="Total connections closed")
    messages_sent: int = Field(..., description="Total messages sent")
    messages_received: int = Field(..., description="Total messages received")

class BroadcastResponse(BaseModel):
    """Response model for broadcast operations."""

    success: bool = Field(..., description="Whether broadcast was successful")
    room: str = Field(..., description="Target room")
    event: str = Field(..., description="Event type")
    message_sent: bool = Field(..., description="Whether message was sent")

class ParserMessageResponse(BaseModel):
    """Response model for parser message operations."""

    success: bool = Field(..., description="Whether message was sent")
    parser_id: str = Field(..., description="Target parser ID")
    event: str = Field(..., description="Event type")
    message_sent: bool = Field(..., description="Whether message was sent")

class DeveloperMessageResponse(BaseModel):
    """Response model for developer message operations."""

    success: bool = Field(..., description="Whether message was sent")
    developer_id: str = Field(..., description="Target developer ID")
    event: str = Field(..., description="Event type")
    sessions_reached: int = Field(..., description="Number of sessions reached")
    message_sent: bool = Field(..., description="Whether message was sent")

class ConnectionsResponse(BaseModel):
    """Response model for connections information."""

    connected_parsers: List[str] = Field(..., description="List of connected parser IDs")
    connected_developers: List[str] = Field(..., description="List of connected developer IDs")
    total_parsers: int = Field(..., description="Total number of connected parsers")
    total_developers: int = Field(..., description="Total number of connected developers")

class SystemNotificationResponse(BaseModel):
    """Response model for system notification broadcast."""

    success: bool = Field(..., description="Whether notification was sent")
    title: str = Field(..., description="Notification title")
    content: str = Field(..., description="Notification content")
    priority: str = Field(..., description="Notification priority")
    broadcasted: bool = Field(..., description="Whether notification was broadcasted")

class DomainEvent(BaseModel):
    """Base class for all domain events."""

    event_id: str
    event_type: str
    aggregate_id: str
    occurred_at: str
    version: int
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class ParserRegisteredEvent(BaseModel):
    """Event fired when parser is registered."""

    event_id: str
    event_type: str
    aggregate_id: str
    occurred_at: str
    version: int
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class ParserDisconnectedEvent(BaseModel):
    """Event fired when parser disconnects."""

    event_id: str
    event_type: str
    aggregate_id: str
    occurred_at: str
    version: int
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class ParserStatusChangedEvent(BaseModel):
    """Event fired when parser status changes."""

    event_id: str
    event_type: str
    aggregate_id: str
    occurred_at: str
    version: int
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class AdminWebSocketEvent(BaseModel):
    """Base class for admin WebSocket events."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable event message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Event timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    type: str = Field(..., description="Event type identifier")
    event_id: str = Field(..., description="Unique event identifier")
    severity: Any = Field(..., description="Event severity")
    component: str = Field(..., description="Component generating event")
    details: Dict[str, Any] = Field(..., description="Event details")
    requires_action: bool = Field(..., description="Whether admin action needed")
    auto_resolve: bool = Field(..., description="Whether event auto-resolves")

class OperationProgressWebSocketEvent(BaseModel):
    """Operation progress WebSocket event."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable event message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Event timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    type: str = Field(..., description="Event type")
    event_id: str = Field(..., description="Unique event identifier")
    severity: Any = Field(..., description="Event severity")
    component: str = Field(..., description="Component generating event")
    details: Dict[str, Any] = Field(..., description="Event details")
    requires_action: bool = Field(..., description="Whether admin action needed")
    auto_resolve: bool = Field(..., description="Whether event auto-resolves")
    operation_id: str = Field(..., description="Operation identifier")
    operation_type: Any = Field(..., description="Operation type")
    status: Any = Field(..., description="Current status")
    progress: int = Field(..., description="Progress percentage")
    current_step: str = Field(..., description="Current operation step")
    steps_completed: int = Field(..., description="Steps completed")
    total_steps: int = Field(..., description="Total steps")
    started_at: str = Field(..., description="Operation start time")
    estimated_completion: Any = Field(..., description="Estimated completion")
    success_count: int = Field(..., description="Successful operations")
    error_count: int = Field(..., description="Failed operations")
    last_error: Any = Field(..., description="Most recent error message")

class Proxy(BaseModel):
    """
    Proxy domain entity.

    Represents a proxy resource with connection details, usage statistics,
    and management metadata following Clean Architecture principles.
    """

    proxy_id: Any = Field(..., description="Unique proxy identifier")
    provider: Any = Field(..., description="Proxy provider")
    provider_proxy_id: Any = Field(..., description="Provider's internal proxy ID")
    endpoint: Any = Field(..., description="Proxy connection endpoint")
    credentials: Any = Field(..., description="Authentication credentials")
    country: str = Field(..., description="Proxy country code")
    region: Any = Field(..., description="Proxy region/state")
    city: Any = Field(..., description="Proxy city")
    status: Any = Field(..., description="Current proxy status")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Any = Field(..., description="Expiration timestamp")
    last_validated_at: Any = Field(..., description="Last validation timestamp")
    usage_stats: Any = Field(..., description="Usage statistics")
    shared: bool = Field(..., description="Whether this is a shared proxy")
    tags: List[str] = Field(..., description="Proxy tags for categorization")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class ProxyEndpoint(BaseModel):
    """Proxy connection endpoint."""

    host: str = Field(..., description="Proxy host/IP address")
    port: int = Field(..., description="Proxy port")
    protocol: Any = Field(..., description="Proxy protocol")

class ProxyCredentials(BaseModel):
    """Proxy authentication credentials."""

    username: str = Field(..., description="Proxy username")
    password: str = Field(..., description="Proxy password")

class ProxyUsageStats(BaseModel):
    """Proxy usage statistics."""

    total_requests: int = Field(..., description="Total requests made")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    consecutive_failures: int = Field(..., description="Consecutive failures")
    avg_response_time_ms: float = Field(..., description="Average response time")
    last_used_at: Any = Field(..., description="Last usage timestamp")
    blocked_count: int = Field(..., description="Number of times blocked")

class ProxyAllocation(BaseModel):
    """Proxy allocation to a parser."""

    parser_id: str = Field(..., description="Parser identifier")
    proxy: Dict[str, Any] = Field(..., description="Allocated proxy details")
    allocated_at: str = Field(..., description="Allocation timestamp")
    last_used_at: str = Field(..., description="Last usage timestamp")
    request_count: int = Field(..., description="Number of requests made")
    success_count: int = Field(..., description="Number of successful requests")
    failure_count: int = Field(..., description="Number of failed requests")

class ProxySummary(BaseModel):
    """Summary information about a proxy."""

    proxy_id: str = Field(..., description="Proxy ID")
    provider: Any = Field(..., description="Proxy provider")
    status: Any = Field(..., description="Current status")
    country: str = Field(..., description="Proxy country")
    protocol: Any = Field(..., description="Proxy protocol")
    host: str = Field(..., description="Proxy host")
    port: int = Field(..., description="Proxy port")
    health_status: Any = Field(..., description="Health status")
    success_rate: float = Field(..., description="Success rate %")
    total_requests: int = Field(..., description="Total requests made")
    consecutive_failures: int = Field(..., description="Consecutive failures")
    created_at: str = Field(..., description="Creation timestamp")
    last_used_at: Any = Field(..., description="Last usage")
    expires_at: Any = Field(..., description="Expiration date")
    assigned_parsers: List[str] = Field(..., description="Assigned parser IDs")
    tags: List[str] = Field(..., description="Proxy tags")

class ProxyDetails(BaseModel):
    """Detailed proxy information."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    proxy_id: str = Field(..., description="Proxy ID")
    provider: Any = Field(..., description="Provider")
    provider_proxy_id: Any = Field(..., description="Provider's internal ID")
    status: Any = Field(..., description="Current status")
    host: str = Field(..., description="Proxy host")
    port: int = Field(..., description="Proxy port")
    protocol: Any = Field(..., description="Protocol")
    credentials: Any = Field(..., description="Login credentials")
    connection_url: Any = Field(..., description="Full connection URL")
    country: str = Field(..., description="Country code")
    region: Any = Field(..., description="Region/state")
    city: Any = Field(..., description="City")
    health_status: Any = Field(..., description="Health status")
    success_rate: float = Field(..., description="Success rate %")
    failure_rate: float = Field(..., description="Failure rate %")
    avg_response_time_ms: float = Field(..., description="Average response time")
    total_requests: int = Field(..., description="Total requests")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    consecutive_failures: int = Field(..., description="Consecutive failures")
    blocked_count: int = Field(..., description="Times blocked")
    created_at: str = Field(..., description="Creation timestamp")
    last_used_at: Any = Field(..., description="Last usage")
    last_validated_at: Any = Field(..., description="Last validation")
    expires_at: Any = Field(..., description="Expiration date")
    assigned_parsers: List[str] = Field(..., description="Assigned parsers")
    rotation_strategy: Any = Field(..., description="Rotation strategy")
    tags: List[str] = Field(..., description="Proxy tags")
    recent_failures: List[Dict[str, Any]] = Field(..., description="Recent failure details")
    created_by_admin: Any = Field(..., description="Admin who added proxy")
    last_updated_by: Any = Field(..., description="Admin who last updated")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class ProxyStatistics(BaseModel):
    """System-wide proxy statistics."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    total_proxies: int = Field(..., description="Total proxies")
    active_proxies: int = Field(..., description="Active proxies")
    inactive_proxies: int = Field(..., description="Inactive proxies")
    blocked_proxies: int = Field(..., description="Blocked proxies")
    expired_proxies: int = Field(..., description="Expired proxies")
    error_proxies: int = Field(..., description="Error state proxies")
    healthy_proxies: int = Field(..., description="Healthy proxies")
    degraded_proxies: int = Field(..., description="Degraded proxies")
    critical_proxies: int = Field(..., description="Critical proxies")
    provider_breakdown: Dict[str, Any] = Field(..., description="Detailed provider statistics")
    country_breakdown: Dict[str, Any] = Field(..., description="Proxy count by country")
    overall_success_rate: float = Field(..., description="Overall success rate %")
    avg_response_time_ms: float = Field(..., description="Average response time")
    total_requests_last_24h: int = Field(..., description="Total requests in last 24h")
    successful_requests_last_24h: int = Field(..., description="Successful requests in last 24h")
    expiring_in_24h: int = Field(..., description="Proxies expiring in 24 hours")
    expiring_in_7d: int = Field(..., description="Proxies expiring in 7 days")
    expiring_in_30d: int = Field(..., description="Proxies expiring in 30 days")
    most_used_providers: List[Dict[str, Any]] = Field(..., description="Most used providers")
    most_active_countries: List[Dict[str, Any]] = Field(..., description="Most active proxy countries")
    proxies_added_last_24h: int = Field(..., description="Proxies added in last 24h")
    proxies_blocked_last_24h: int = Field(..., description="Proxies blocked in last 24h")
    generated_at: str = Field(..., description="Statistics generation time")

class HealthStatsResponse(BaseModel):
    """Health service statistics."""

    service_start_time: str = Field(..., description="Service start timestamp in ISO format")
    uptime: str = Field(..., description="Human-readable uptime")
    health_check_count: int = Field(..., description="Total health checks performed")
    last_health_check: Any = Field(..., description="Last health check timestamp in ISO format")
    component_timeout: float = Field(..., description="Component timeout in seconds")
    overall_timeout: float = Field(..., description="Overall timeout in seconds")

class ComponentHealth(BaseModel):
    """Health status for individual system component."""

    status: str = Field(..., description="Component health status")
    response_time_ms: Any = Field(..., description="Response time in milliseconds")
    error: Any = Field(..., description="Error message if unhealthy")
    details: Dict[str, Any] = Field(..., description="Additional health details")
    last_checked: str = Field(..., description="Last health check time in ISO format")

class SystemMetrics(BaseModel):
    """System performance metrics."""

    cpu_usage: Any = Field(..., description="CPU usage percentage")
    memory_usage: Any = Field(..., description="Memory usage in GB")
    memory_percent: Any = Field(..., description="Memory usage percentage")
    disk_usage: Any = Field(..., description="Disk usage percentage")
    load_average: Any = Field(..., description="System load average")
    note: Any = Field(..., description="Additional notes")
    error: Any = Field(..., description="Error message if metrics unavailable")

class SystemHealthReport(BaseModel):
    """Complete system health report."""

    status: str = Field(..., description="Overall system status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Report timestamp in ISO format")
    uptime: Any = Field(..., description="System uptime")
    components: Dict[str, Any] = Field(..., description="Component health status")
    system: Any = Field(..., description="System metrics")
    message: str = Field(..., description="Status message")
    error: Any = Field(..., description="Error message if unhealthy")

class BroadcastDeliveryStats(BaseModel):
    """Broadcast delivery statistics."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    total_targeted: int = Field(..., description="Total users targeted")
    delivered: int = Field(..., description="Successfully delivered count")
    failed: int = Field(..., description="Failed delivery count")
    pending: int = Field(..., description="Pending delivery count")
    delivery_rate: float = Field(..., description="Delivery success rate percentage")

class SystemMetricsPoint(BaseModel):
    """Single system metrics data point."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Measurement timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_in: Any = Field(..., description="Network input (MB/s)")
    network_out: Any = Field(..., description="Network output (MB/s)")
    active_connections: int = Field(..., description="Active connections")
    requests_per_minute: int = Field(..., description="Requests per minute")
    error_rate: float = Field(..., description="Error rate (0-1)")
    response_time_avg: float = Field(..., description="Average response time (ms)")
    active_proxies: int = Field(..., description="Active proxy count")
    active_parsers: int = Field(..., description="Active parser count")
    queue_size: int = Field(..., description="Processing queue size")

class SystemMetricsResponse(BaseModel):
    """System metrics response."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    timeframe: str = Field(..., description="Requested timeframe")
    resolution: str = Field(..., description="Data resolution used")
    metrics: List[Any] = Field(..., description="Time series metrics data")
    summary: Dict[str, Any] = Field(..., description="Summary statistics for the period")
    alerts: List[Dict[str, Any]] = Field(..., description="Active metric alerts")
    predictions: Any = Field(..., description="Trend predictions if requested")

class SystemMetricsWebSocketEvent(BaseModel):
    """Real-time system metrics WebSocket event."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable event message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Event timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    type: str = Field(..., description="Event type")
    event_id: str = Field(..., description="Unique event identifier")
    severity: Any = Field(..., description="Event severity")
    component: str = Field(..., description="Component generating event")
    details: Dict[str, Any] = Field(..., description="Event details")
    requires_action: bool = Field(..., description="Whether admin action needed")
    auto_resolve: bool = Field(..., description="Whether event auto-resolves")
    metrics_data: Any = Field(..., description="Current metrics")
    trend_direction: str = Field(..., description="Overall trend direction")
    alerts_triggered: List[str] = Field(..., description="Alerts triggered by current metrics")

class UserStatistics(BaseModel):
    """System-wide user statistics."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    total_users: int = Field(..., description="Total users in system")
    active_users: int = Field(..., description="Active users")
    suspended_users: int = Field(..., description="Suspended users")
    pending_users: int = Field(..., description="Pending activation users")
    developers: int = Field(..., description="Developer role users")
    admins: int = Field(..., description="Admin role users")
    guests: int = Field(..., description="Guest role users")
    users_active_last_24h: int = Field(..., description="Users active in last 24 hours")
    users_active_last_7d: int = Field(..., description="Users active in last 7 days")
    users_active_last_30d: int = Field(..., description="Users active in last 30 days")
    users_with_parsers: int = Field(..., description="Users who own parsers")
    users_without_parsers: int = Field(..., description="Users without parsers")
    avg_parsers_per_user: float = Field(..., description="Average parsers per user")
    new_users_last_24h: int = Field(..., description="New users in last 24 hours")
    new_users_last_7d: int = Field(..., description="New users in last 7 days")
    new_users_last_30d: int = Field(..., description="New users in last 30 days")
    total_api_calls_today: int = Field(..., description="Total API calls today")
    unique_api_users_today: int = Field(..., description="Unique API users today")
    avg_api_calls_per_user: float = Field(..., description="Average API calls per user")
    generated_at: str = Field(..., description="Statistics generation time")
    top_active_users: List[Dict[str, Any]] = Field(..., description="Top 10 most active users")
    top_parser_owners: List[Dict[str, Any]] = Field(..., description="Top 10 users by parser count")

class SystemStatistics(BaseModel):
    """Comprehensive system statistics."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Any = Field(..., description="Optional response data")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: Any = Field(..., description="Original request tracking ID")
    total_parsers: int = Field(..., description="Total parsers")
    active_parsers: int = Field(..., description="Active parsers")
    total_developers: int = Field(..., description="Total developers")
    active_developers: int = Field(..., description="Active developers")
    total_services: int = Field(..., description="Total services")
    running_services: int = Field(..., description="Running services")
    idle_services: int = Field(..., description="Idle services")
    error_services: int = Field(..., description="Services in error state")
    commands_pending: int = Field(..., description="Pending commands")
    commands_running: int = Field(..., description="Running commands")
    commands_completed_today: int = Field(..., description="Commands completed today")
    avg_system_response_time_ms: float = Field(..., description="Average system response time")
    system_cpu_usage_percent: float = Field(..., description="System CPU usage")
    system_memory_usage_percent: float = Field(..., description="System memory usage")
    active_websocket_connections: int = Field(..., description="Active WebSocket connections")
    total_api_calls_today: int = Field(..., description="Total API calls today")
    database_size_mb: float = Field(..., description="Database size in MB")
    cache_hit_rate_percent: float = Field(..., description="Cache hit rate")
    total_proxies: int = Field(..., description="Total proxies")
    healthy_proxies: int = Field(..., description="Healthy proxies")
    operations_last_24h: int = Field(..., description="Admin operations in last 24h")
    errors_last_24h: int = Field(..., description="System errors in last 24h")
    generated_at: str = Field(..., description="Statistics generation time")
    system_health_score: float = Field(..., description="Overall system health score (0-100)")
    health_factors: Dict[str, Any] = Field(..., description="Individual health factor scores")
    performance_trend_7d: str = Field(..., description="7-day performance trend")
    capacity_utilization_percent: float = Field(..., description="Overall capacity utilization")

class RealTimeMetrics(BaseModel):
    """Real-time system metrics."""

    timestamp: str = Field(..., description="Metrics timestamp")
    cpu_usage_percent: float = Field(..., description="Current CPU usage")
    memory_usage_percent: float = Field(..., description="Current memory usage")
    disk_usage_percent: float = Field(..., description="Current disk usage")
    network_in_mbps: float = Field(..., description="Network input rate")
    network_out_mbps: float = Field(..., description="Network output rate")
    active_connections: int = Field(..., description="Active connections")
    requests_per_second: float = Field(..., description="Current RPS")
    avg_response_time_ms: float = Field(..., description="Average response time")
    error_rate_percent: float = Field(..., description="Current error rate")
    active_parsers: int = Field(..., description="Active parsers")
    total_parsers: int = Field(..., description="Total parsers")
    commands_queued: int = Field(..., description="Queued commands")
    commands_executing: int = Field(..., description="Executing commands")
    healthy_proxies: int = Field(..., description="Healthy proxies")
    total_proxies: int = Field(..., description="Total proxies")
    proxy_success_rate_percent: float = Field(..., description="Proxy success rate")
    cache_hit_rate_percent: float = Field(..., description="Cache hit rate")
    cache_memory_usage_mb: float = Field(..., description="Cache memory usage")
    db_connections_active: int = Field(..., description="Active DB connections")
    db_query_avg_time_ms: float = Field(..., description="Average query time")
    api_calls_last_minute: int = Field(..., description="API calls in last minute")
    unique_users_online: int = Field(..., description="Unique users online")
    overall_health_score: float = Field(..., description="Overall system health score")
    alerts_active: int = Field(..., description="Active alerts count")
