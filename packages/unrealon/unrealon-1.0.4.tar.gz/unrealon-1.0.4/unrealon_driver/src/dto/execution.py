"""
Execution mode configuration models for UnrealOn Driver v3.0

Type-safe configuration for all execution modes.
COMPLIANCE: 100% Pydantic v2 compliant, no Dict[str, Any] usage.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum

from .config import LogLevel


class ExecutionEnvironment(str, Enum):
    """Execution environment enumeration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ParserTestConfig(BaseModel):
    """Type-safe configuration for test mode execution."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core settings
    environment: ExecutionEnvironment = Field(default=ExecutionEnvironment.TESTING)
    verbose: bool = Field(default=False, description="Enable verbose output")
    show_browser: bool = Field(default=False, description="Show browser window")
    save_screenshots: bool = Field(default=False, description="Save debug screenshots")

    # Performance settings
    timeout_seconds: int = Field(default=60, ge=1, le=3600, description="Test timeout")
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum retry attempts"
    )

    # Output settings
    output_format: str = Field(default="json", pattern=r"^(json|yaml|csv)$")
    save_results: bool = Field(default=False, description="Save results to file")
    results_file: Optional[str] = Field(default=None, description="Results file path")


class DaemonModeConfig(BaseModel):
    """Type-safe configuration for daemon mode execution."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # WebSocket settings
    server_url: Optional[str] = Field(default=None, description="WebSocket server URL")
    api_key: Optional[str] = Field(default=None, description="Authentication API key")
    auto_reconnect: bool = Field(
        default=True, description="Auto-reconnect on disconnect"
    )

    # Connection settings
    connection_timeout: int = Field(
        default=30, ge=1, le=300, description="Connection timeout"
    )
    heartbeat_interval: int = Field(
        default=30, ge=5, le=300, description="Heartbeat interval"
    )
    max_reconnect_attempts: int = Field(
        default=10, ge=1, le=100, description="Max reconnection attempts"
    )

    # Health monitoring
    health_check_interval: int = Field(
        default=60, ge=10, le=3600, description="Health check interval"
    )
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")


class ScheduledModeConfig(BaseModel):
    """Type-safe configuration for scheduled mode execution."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Scheduling settings
    every: str = Field(..., description="Schedule interval (30m, 1h, daily)")
    at: Optional[str] = Field(
        default=None, description="Specific time for daily schedules"
    )
    max_runs: Optional[int] = Field(
        default=None, ge=1, description="Maximum number of runs"
    )

    # Execution settings
    timeout: int = Field(default=300, ge=30, le=3600, description="Task timeout")
    retry_attempts: int = Field(
        default=3, ge=0, le=10, description="Retry attempts on failure"
    )
    max_concurrent: int = Field(
        default=1, ge=1, le=10, description="Max concurrent tasks"
    )

    # Advanced settings
    jitter: bool = Field(default=True, description="Enable jitter for load balancing")
    jitter_range: float = Field(
        default=0.1, ge=0.0, le=0.5, description="Jitter range (0.1 = ±10%)"
    )
    error_handling: str = Field(default="retry", pattern=r"^(retry|skip|stop)$")


class InteractiveModeConfig(BaseModel):
    """Type-safe configuration for interactive mode execution."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Interface settings
    enable_debugger: bool = Field(
        default=True, description="Enable interactive debugger"
    )
    show_browser: bool = Field(default=True, description="Show browser window")
    auto_reload: bool = Field(default=True, description="Auto-reload on code changes")

    # Development settings
    log_level: LogLevel = Field(default=LogLevel.DEBUG, description="Logging level")
    enable_profiling: bool = Field(
        default=False, description="Enable performance profiling"
    )
    save_session: bool = Field(default=True, description="Save interactive session")


class ExecutionResult(BaseModel):
    """Type-safe execution result model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    # Status
    success: bool = Field(..., description="Execution success status")
    execution_id: str = Field(..., description="Unique execution identifier")

    # Timing
    start_time: str = Field(default="", description="Execution start time (ISO format)")
    end_time: str = Field(default="", description="Execution end time (ISO format)")
    duration_seconds: float = Field(default=0.0, ge=0.0, description="Execution duration")

    # Data
    data: Optional[dict] = Field(default=None, description="Parsed data result")
    items_processed: int = Field(
        default=0, ge=0, description="Number of items processed"
    )

    # Error information
    error: Optional["ErrorInfo"] = Field(
        default=None, description="Error details if failed"
    )

    # Performance metrics
    performance_metrics: Optional["PerformanceMetrics"] = Field(
        default=None, description="Performance metrics if available"
    )

    # Metadata
    parser_id: str = Field(default="", description="Parser identifier")
    execution_mode: str = Field(default="test", description="Execution mode used")
    environment: ExecutionEnvironment = Field(default=ExecutionEnvironment.TESTING, description="Execution environment")


class ErrorInfo(BaseModel):
    """Type-safe error information model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
    )

    message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type/class")
    error_code: Optional[str] = Field(
        default=None, description="Application error code"
    )
    traceback: Optional[str] = Field(default=None, description="Error traceback")
    context: Optional[dict] = Field(
        default=None, description="Error context information"
    )


class PerformanceMetrics(BaseModel):
    """Type-safe performance metrics model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    # Basic metrics
    execution_time_seconds: float = Field(
        default=0.0, ge=0.0, description="Total execution time"
    )
    memory_usage_mb: float = Field(default=0.0, ge=0.0, description="Peak memory usage")
    cpu_usage_percent: float = Field(
        default=0.0, ge=0.0, le=100.0, description="CPU usage percentage"
    )

    # Operation metrics
    operations_count: int = Field(
        default=0, ge=0, description="Number of operations performed"
    )
    operations_per_second: float = Field(
        default=0.0, ge=0.0, description="Operations per second"
    )

    # Service metrics
    browser_operations: int = Field(
        default=0, ge=0, description="Browser operations count"
    )
    llm_operations: int = Field(default=0, ge=0, description="LLM operations count")
    websocket_messages: int = Field(
        default=0, ge=0, description="WebSocket messages count"
    )


class ScheduledModeStatus(BaseModel):
    """Type-safe scheduled mode status model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    status: str = Field(..., pattern=r"^(not_started|running|stopped|error)$")
    is_running: bool = Field(..., description="Whether scheduler is running")
    parser_id: str = Field(..., description="Parser identifier")
    parser_name: str = Field(..., description="Parser name")
    scheduler_health: Optional[dict] = Field(
        default=None, description="Scheduler health data"
    )


class DaemonCommandResult(BaseModel):
    """Type-safe daemon command result model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    status: str = Field(..., pattern=r"^(success|error)$")
    data: Optional[dict] = Field(default=None, description="Command result data")
    items_processed: int = Field(default=0, ge=0, description="Items processed")
    duration_seconds: float = Field(..., ge=0.0, description="Command duration")
    parser_id: str = Field(..., description="Parser identifier")
    timestamp: str = Field(..., description="Command timestamp")
    error: Optional[ErrorInfo] = Field(
        default=None, description="Error details if failed"
    )


class DaemonStatusResult(BaseModel):
    """Type-safe daemon status result model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    status: str = Field(..., pattern=r"^(success|error)$")
    parser_id: str = Field(..., description="Parser identifier")
    parser_name: str = Field(..., description="Parser name")
    daemon_running: bool = Field(..., description="Whether daemon is running")
    health: Optional[dict] = Field(default=None, description="Parser health data")
    timestamp: str = Field(..., description="Status timestamp")
    error: Optional[ErrorInfo] = Field(
        default=None, description="Error details if failed"
    )


class DaemonHealthResult(BaseModel):
    """Type-safe daemon health result model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    status: str = Field(..., pattern=r"^(healthy|unhealthy)$")
    data: Optional[dict] = Field(default=None, description="Health check data")
    parser_id: str = Field(..., description="Parser identifier")
    timestamp: str = Field(..., description="Health check timestamp")
    error: Optional[ErrorInfo] = Field(
        default=None, description="Error details if failed"
    )


# Update forward references
ExecutionResult.model_rebuild()
DaemonCommandResult.model_rebuild()
DaemonStatusResult.model_rebuild()
DaemonHealthResult.model_rebuild()
