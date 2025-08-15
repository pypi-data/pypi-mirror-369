"""
Driver Event Types - UnrealOn Driver v3.0

Specialized event types for driver operations with full SDK integration.
Provides structured logging for browser automation, parsing, and system monitoring.

COMPLIANCE: 100% Pydantic v2 compliant, no Dict[str, Any] usage.
"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DriverEventType(str, Enum):
    """
    🎯 Driver-specific event types for comprehensive operation tracking.

    Each event has a unique string value for proper enum behavior and naming.
    Provides driver-specific semantics for better monitoring and debugging.
    """

    # ==========================================
    # SERVICE LIFECYCLE EVENTS
    # ==========================================
    SERVICE_INITIALIZED = "service_initialized"
    SERVICE_CONFIGURED = "service_configured"
    SERVICE_STARTED = "service_started"
    SERVICE_STOPPED = "service_stopped"
    SERVICE_ERROR = "service_error"
    SERVICE_HEALTH_CHECK = "service_health_check"

    # ==========================================
    # DRIVER-SPECIFIC BROWSER EVENTS (not covered by unrealon_browser)
    # ==========================================
    BROWSER_CONTENT_EXTRACTED = (
        "browser_content_extracted"  # Driver's structured extraction
    )
    BROWSER_SCREENSHOT_TAKEN = "browser_screenshot_taken"  # Driver's screenshot feature

    # ==========================================
    # PARSER OPERATION EVENTS
    # ==========================================
    PARSER_STARTED = "parser_started"
    PARSER_COMPLETED = "parser_completed"
    PARSER_FAILED = "parser_failed"
    PARSER_DATA_EXTRACTED = "parser_data_extracted"
    PARSER_VALIDATION_PASSED = "parser_validation_passed"
    PARSER_VALIDATION_FAILED = "parser_validation_failed"
    PARSER_SCHEMA_APPLIED = "parser_schema_applied"
    PARSER_RETRY_ATTEMPTED = "parser_retry_attempted"
    PARSER_TIMEOUT = "parser_timeout"

    # ==========================================
    # DRIVER-SPECIFIC LLM EVENTS (not covered by unrealon_llm)
    # ==========================================
    LLM_EXTRACTION_WITH_BROWSER = (
        "llm_extraction_with_browser"  # Driver's browser+LLM integration
    )
    LLM_BATCH_PROCESSING = "llm_batch_processing"  # Driver's batch processing

    # ==========================================
    # SCHEDULER EVENTS
    # ==========================================
    SCHEDULER_TASK_QUEUED = "scheduler_task_queued"
    SCHEDULER_TASK_STARTED = "scheduler_task_started"
    SCHEDULER_TASK_COMPLETED = "scheduler_task_completed"
    SCHEDULER_TASK_FAILED = "scheduler_task_failed"
    SCHEDULER_TASK_RETRY = "scheduler_task_retry"
    SCHEDULER_CRON_TRIGGERED = "scheduler_cron_triggered"
    SCHEDULER_QUEUE_FULL = "scheduler_queue_full"

    # ==========================================
    # WEBSOCKET SERVICE EVENTS (driver-specific only, SDK handles connection events)
    # ==========================================
    WEBSOCKET_COMMAND_HANDLER_REGISTERED = "websocket_command_handler_registered"

    # ==========================================
    # METRICS SERVICE EVENTS (driver-specific metrics collection)
    # ==========================================
    METRICS_COLLECTION_STARTED = "metrics_collection_started"
    METRICS_COLLECTION_COMPLETED = "metrics_collection_completed"
    METRICS_DATA_AGGREGATED = "metrics_data_aggregated"


# Convenience mappings for common event scenarios
BROWSER_EVENTS = [
    DriverEventType.BROWSER_CONTENT_EXTRACTED,  # Driver-specific structured extraction
    DriverEventType.BROWSER_SCREENSHOT_TAKEN,  # Driver-specific screenshot feature
]

PARSER_EVENTS = [
    DriverEventType.PARSER_STARTED,
    DriverEventType.PARSER_DATA_EXTRACTED,
    DriverEventType.PARSER_VALIDATION_PASSED,
    DriverEventType.PARSER_COMPLETED,
]

LLM_EVENTS = [
    DriverEventType.LLM_EXTRACTION_WITH_BROWSER,  # Driver-specific browser+LLM integration
    DriverEventType.LLM_BATCH_PROCESSING,  # Driver-specific batch processing
]

SCHEDULER_EVENTS = [
    DriverEventType.SCHEDULER_TASK_QUEUED,
    DriverEventType.SCHEDULER_TASK_STARTED,
    DriverEventType.SCHEDULER_TASK_COMPLETED,
    DriverEventType.SCHEDULER_CRON_TRIGGERED,
]

WEBSOCKET_EVENTS = [
    DriverEventType.WEBSOCKET_COMMAND_HANDLER_REGISTERED,  # Driver-specific handler registration
]

METRICS_EVENTS = [
    DriverEventType.METRICS_COLLECTION_STARTED,
    DriverEventType.METRICS_COLLECTION_COMPLETED,
    DriverEventType.METRICS_DATA_AGGREGATED,
]

ERROR_EVENTS = [
    DriverEventType.SERVICE_ERROR,
    DriverEventType.PARSER_FAILED,
    DriverEventType.PARSER_VALIDATION_FAILED,
    DriverEventType.PARSER_TIMEOUT,
    DriverEventType.SCHEDULER_TASK_FAILED,
    DriverEventType.SCHEDULER_QUEUE_FULL,
]


class DriverEventContext(BaseModel):
    """
    🎯 Structured context for driver events with full type safety.

    Provides rich context information for driver operations
    with automatic validation and serialization.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core identification
    parser_id: str = Field(..., description="Parser identifier")
    parser_name: str = Field(..., description="Human-readable parser name")

    # Event details
    event_type: DriverEventType = Field(..., description="Type of driver event")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )

    # Operation context
    operation_id: Optional[str] = Field(
        default=None, description="Unique operation identifier"
    )
    session_id: Optional[str] = Field(default=None, description="Session identifier")

    # Performance metrics
    duration_ms: Optional[float] = Field(
        default=None, ge=0, description="Operation duration in milliseconds"
    )
    memory_usage_mb: Optional[float] = Field(
        default=None, ge=0, description="Memory usage in MB"
    )

    # Browser context
    page_url: Optional[str] = Field(default=None, description="Current page URL")
    page_title: Optional[str] = Field(default=None, description="Page title")
    browser_version: Optional[str] = Field(default=None, description="Browser version")

    # LLM context
    llm_model: Optional[str] = Field(default=None, description="LLM model used")
    tokens_used: Optional[int] = Field(
        default=None, ge=0, description="Tokens consumed"
    )
    cost_usd: Optional[float] = Field(
        default=None, ge=0, description="Operation cost in USD"
    )

    # Data context
    items_processed: Optional[int] = Field(
        default=None, ge=0, description="Number of items processed"
    )
    data_size_bytes: Optional[int] = Field(
        default=None, ge=0, description="Data size in bytes"
    )

    # Error context
    error_type: Optional[str] = Field(default=None, description="Error type if failed")
    error_message: Optional[str] = Field(default=None, description="Error message")
    stack_trace: Optional[str] = Field(
        default=None, description="Stack trace for debugging"
    )

    # Additional metadata
    environment: str = Field(default="development", description="Runtime environment")
    service_name: Optional[str] = Field(
        default=None, description="Service that generated the event"
    )
    tags: List[str] = Field(
        default_factory=list, description="Event tags for filtering"
    )


class DriverEventMetrics(BaseModel):
    """Performance metrics for driver events."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Timing metrics
    start_time: datetime = Field(..., description="Event start time")
    end_time: Optional[datetime] = Field(default=None, description="Event end time")
    duration_seconds: Optional[float] = Field(
        default=None, ge=0, description="Duration in seconds"
    )

    # Resource metrics
    cpu_percent: Optional[float] = Field(
        default=None, ge=0, le=100, description="CPU usage percentage"
    )
    memory_mb: Optional[float] = Field(
        default=None, ge=0, description="Memory usage in MB"
    )
    network_bytes: Optional[int] = Field(
        default=None, ge=0, description="Network bytes transferred"
    )

    # Success metrics
    success_rate: Optional[float] = Field(
        default=None, ge=0, le=1, description="Success rate (0-1)"
    )
    retry_count: int = Field(default=0, ge=0, description="Number of retries")
    error_count: int = Field(default=0, ge=0, description="Number of errors")
