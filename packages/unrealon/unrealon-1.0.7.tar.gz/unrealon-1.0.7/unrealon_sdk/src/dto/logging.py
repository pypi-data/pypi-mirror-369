"""
Logging-related Data Transfer Objects

Custom DTO models for enterprise logging system functionality.
These models provide type-safe logging configuration and event tracking.
Includes models for both development logging and structured logging.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel, Field, ConfigDict

# Import LogEntryMessage at module level to avoid inline imports
try:
    from unrealon_sdk.src.enterprise.logging.service import LogEntryMessage
except ImportError:
    # Fallback for when logging service is not available
    LogEntryMessage = None


class LogDestination(str, Enum):
    """Available log destinations."""
    
    CONSOLE = "console"
    WEBSOCKET = "websocket"
    FILE = "file"
    HTTP = "http"
    BUFFER = "buffer"


class SDKEventType(str, Enum):
    """SDK development event types for process tracking."""

    # SDK Lifecycle Events
    SDK_INITIALIZED = "sdk_initialized"
    SDK_STARTED = "sdk_started"
    SDK_SHUTDOWN = "sdk_shutdown"
    SDK_ERROR = "sdk_error"

    # Layer Development Events (Skyscraper Architecture)
    LAYER_STARTED = "layer_started"
    LAYER_COMPLETED = "layer_completed"
    LAYER_VALIDATION = "layer_validation"
    LAYER_FAILED = "layer_failed"

    # Component Development Events
    COMPONENT_CREATED = "component_created"
    COMPONENT_TESTED = "component_tested"
    COMPONENT_INTEGRATED = "component_integrated"
    COMPONENT_DEPRECATED = "component_deprecated"

    # Connection Management Events
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_LOST = "connection_lost"
    CONNECTION_RETRY = "connection_retry"
    CONNECTION_HEALTH_CHECK = "connection_health_check"

    # Command Processing Events
    COMMAND_RECEIVED = "command_received"
    COMMAND_EXECUTED = "command_executed"
    COMMAND_COMPLETED = "command_completed"
    COMMAND_FAILED = "command_failed"
    COMMAND_TIMEOUT = "command_timeout"

    # Proxy Management Events
    PROXY_MANAGER_INITIALIZED = "proxy_manager_initialized"
    PROXY_ALLOCATED = "proxy_allocated"
    PROXY_ROTATION = "proxy_rotation"
    PROXY_HEALTH_CHECK = "proxy_health_check"
    PROXY_BLACKLISTED = "proxy_blacklisted"

    # Logging Service Events
    LOGGING_SERVICE_INITIALIZED = "logging_service_initialized"
    LOG_BUFFER_FLUSHED = "log_buffer_flushed"
    LOG_WEBSOCKET_SENT = "log_websocket_sent"
    LOG_WEBSOCKET_ERROR = "log_websocket_error"

    # Performance Monitoring Events
    PERFORMANCE_METRIC_COLLECTED = "performance_metric_collected"
    PERFORMANCE_THRESHOLD_EXCEEDED = "performance_threshold_exceeded"
    PERFORMANCE_OPTIMIZATION_APPLIED = "performance_optimization_applied"

    # Error Recovery Events
    ERROR_DETECTED = "error_detected"
    ERROR_RECOVERY_STARTED = "error_recovery_started"
    ERROR_RECOVERY_COMPLETED = "error_recovery_completed"
    ERROR_RECOVERY_FAILED = "error_recovery_failed"

    # API Integration Events
    API_CALL_STARTED = "api_call_started"
    API_CALL_COMPLETED = "api_call_completed"
    API_CALL_FAILED = "api_call_failed"
    API_RATE_LIMITED = "api_rate_limited"

    # Development Quality Events
    TYPE_SAFETY_VALIDATION = "type_safety_validation"
    PYDANTIC_MODEL_VALIDATION = "pydantic_model_validation"
    CODE_QUALITY_CHECK = "code_quality_check"
    LINT_CHECK = "lint_check"

    # Testing Events
    TEST_STARTED = "test_started"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"
    TEST_COVERAGE_MEASURED = "test_coverage_measured"

    # Integration Events
    CLIENT_INTEGRATION = "client_integration"
    WEBSOCKET_INTEGRATION = "websocket_integration"
    HTTP_INTEGRATION = "http_integration"

    # Debug Events
    DEBUG_CHECKPOINT = "debug_checkpoint"
    DEBUG_VARIABLE_DUMP = "debug_variable_dump"
    DEBUG_STACK_TRACE = "debug_stack_trace"


class SDKSeverity(str, Enum):
    """SDK development event severity levels."""

    TRACE = "trace"  # Detailed tracing information
    DEBUG = "debug"  # Debug information
    INFO = "info"  # General information
    WARNING = "warning"  # Warning conditions
    ERROR = "error"  # Error conditions
    CRITICAL = "critical"  # Critical conditions
    FATAL = "fatal"  # Fatal conditions causing shutdown


@dataclass
class SDKContext:
    """Context information for SDK development events."""

    # Development context
    layer_name: Optional[str] = None
    component_name: Optional[str] = None
    method_name: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    # Runtime context
    thread_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

    # Performance context
    execution_time_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

    # Connection context
    parser_id: Optional[str] = None
    adapter_url: Optional[str] = None
    websocket_connected: Optional[bool] = None
    http_client_active: Optional[bool] = None

    # Command context
    command_id: Optional[str] = None
    command_type: Optional[str] = None
    command_priority: Optional[str] = None

    # Additional metadata (use Any for flexible context data)
    metadata: Optional[Any] = None


class SDKDevelopmentEvent(BaseModel):
    """Structured development event model for SDK logging."""

    model_config = ConfigDict(extra="forbid")

    # Event identification
    event_type: SDKEventType = Field(..., description="Type of SDK development event")
    severity: SDKSeverity = Field(..., description="Event severity level")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp in UTC"
    )

    # Event details
    message: str = Field(..., description="Human-readable event description")
    details: Any = Field(
        default_factory=dict, description="Additional event details (flexible structure)"
    )

    # Context information
    context: SDKContext = Field(default_factory=SDKContext, description="Event context")

    # Result information
    success: bool = Field(..., description="Whether the operation was successful")
    error_code: Optional[str] = Field(None, description="Error code if operation failed")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")

    # Performance metrics
    duration_ms: Optional[float] = Field(None, description="Operation duration in milliseconds")

    def to_websocket_message(self, session_id: str) -> Any:
        """Convert to WebSocket LogEntryMessage for real-time streaming."""
        # Note: This method will use LogEntryMessage from enterprise logging service
        if LogEntryMessage is None:
            raise ImportError("LogEntryMessage not available - logging service not installed")
        
        return LogEntryMessage(
            type="sdk_development_log",
            session_id=session_id,
            entry={
                "event_type": self.event_type.value,
                "severity": self.severity.value,
                "message": self.message,
                "success": self.success,
                "details": self.details,
                "context": self.context.__dict__ if hasattr(self.context, "__dict__") else {},
                "error_code": self.error_code,
                "error_message": self.error_message,
                "duration_ms": self.duration_ms,
            },
            timestamp=self.timestamp.isoformat(),
        )


__all__ = [
    # Enums
    "LogDestination",
    "SDKEventType", 
    "SDKSeverity",
    # Models
    "SDKContext",
    "SDKDevelopmentEvent",
]
