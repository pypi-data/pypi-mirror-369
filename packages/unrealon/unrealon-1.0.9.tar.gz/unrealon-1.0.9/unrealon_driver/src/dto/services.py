"""
Service configuration models for UnrealOn Driver v3.0

Type-safe configuration for all services.
COMPLIANCE: 100% Pydantic v2 compliant, no Dict[str, Any] usage.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Union
from pathlib import Path
from enum import Enum

from .config import LogLevel
# 🔥 STEALTH ALWAYS ON - NO IMPORT NEEDED!


class DriverBrowserConfig(BaseModel):
    """Type-safe browser service configuration for UnrealOn Driver."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core browser settings
    headless: bool = Field(default=True, description="Run browser in headless mode")
    timeout: int = Field(
        default=30, ge=1, le=300, description="Page timeout in seconds"
    )
    user_data_dir: Optional[str] = Field(
        default=None, description="Browser user data directory"
    )
    parser_id: str = Field(..., description="Parser identifier")

    # 🔥 STEALTH ALWAYS ON - NO CONFIG NEEDED!

    # Performance settings
    page_load_strategy: str = Field(default="normal", pattern=r"^(normal|eager|none)$")
    wait_for_selector_timeout: int = Field(
        default=10, ge=1, le=60, description="Selector wait timeout"
    )
    network_idle_timeout: int = Field(
        default=3, ge=1, le=30, description="Network idle timeout"
    )

    # Features
    enable_javascript: bool = Field(
        default=True, description="Enable JavaScript execution"
    )
    enable_images: bool = Field(default=True, description="Load images")
    enable_css: bool = Field(default=True, description="Load CSS")

    # Debug settings
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    save_screenshots: bool = Field(default=False, description="Save debug screenshots")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Browser log level")


class LLMConfig(BaseModel):
    """Type-safe LLM service configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Provider settings
    provider: str = Field(default="openrouter", description="LLM provider")
    model: str = Field(
        default="anthropic/claude-3.5-sonnet", description="Model identifier"
    )
    api_key: Optional[str] = Field(default=None, description="API key")

    # Request settings
    max_tokens: int = Field(default=2048, ge=1, le=8192, description="Maximum tokens")
    temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description="Sampling temperature"
    )
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout")

    # Processing settings
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum retry attempts"
    )
    chunk_size: int = Field(
        default=4000, ge=100, le=10000, description="Text chunk size"
    )

    # Features
    enable_caching: bool = Field(default=True, description="Enable response caching")
    enable_cost_tracking: bool = Field(default=True, description="Enable cost tracking")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="LLM log level")


class WebSocketConfig(BaseModel):
    """Type-safe WebSocket service configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Connection settings
    server_url: Optional[str] = Field(default=None, description="WebSocket server URL")
    api_key: Optional[str] = Field(default=None, description="Authentication API key")
    parser_name: str = Field(..., description="Parser name for identification")

    # Reliability settings
    auto_reconnect: bool = Field(
        default=True, description="Auto-reconnect on disconnect"
    )
    max_reconnect_attempts: int = Field(
        default=10, ge=1, le=100, description="Max reconnection attempts"
    )
    reconnect_delay: float = Field(
        default=1.0, ge=0.1, le=60.0, description="Reconnect delay seconds"
    )

    # Health monitoring
    health_check_interval: int = Field(
        default=30, ge=5, le=300, description="Health check interval"
    )
    heartbeat_interval: int = Field(
        default=30, ge=5, le=300, description="Heartbeat interval"
    )
    connection_timeout: int = Field(
        default=10, ge=1, le=60, description="Connection timeout"
    )


class LoggerConfig(BaseModel):
    """Type-safe logger service configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Default log level")
    console_output: bool = Field(default=True, description="Enable console output")
    file_output: bool = Field(default=True, description="Enable file output")

    # File settings
    log_file: str = Field(default="parser.log", description="Log file name")
    log_dir: Optional[str] = Field(default=None, description="Log directory")
    max_file_size: str = Field(default="10MB", description="Max log file size")
    backup_count: int = Field(
        default=5, ge=1, le=50, description="Number of backup files"
    )

    # Format settings
    log_format: str = Field(
        default="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        description="Log format string",
    )
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S", description="Date format")

    # Performance
    buffer_size: int = Field(
        default=1024, ge=256, le=8192, description="Log buffer size"
    )
    flush_interval: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Flush interval seconds"
    )


class MetricsConfig(BaseModel):
    """Type-safe metrics service configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core settings
    parser_id: str = Field(..., description="Parser identifier")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")

    # Collection settings
    collect_performance: bool = Field(
        default=True, description="Collect performance metrics"
    )
    collect_errors: bool = Field(default=True, description="Collect error metrics")
    collect_usage: bool = Field(default=True, description="Collect usage metrics")

    # Storage settings
    retention_days: int = Field(
        default=30, ge=1, le=365, description="Metrics retention period"
    )
    export_format: str = Field(default="json", pattern=r"^(json|csv|prometheus)$")

    # Performance
    batch_size: int = Field(
        default=100, ge=1, le=1000, description="Metrics batch size"
    )
    flush_interval: int = Field(
        default=60, ge=1, le=3600, description="Flush interval seconds"
    )


class SchedulerConfig(BaseModel):
    """Type-safe scheduler service configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core settings
    parser_id: str = Field(..., description="Parser identifier")
    max_concurrent_tasks: int = Field(
        default=10, ge=1, le=100, description="Max concurrent tasks"
    )
    enable_jitter: bool = Field(
        default=True, description="Enable jitter for load balancing"
    )
    jitter_range: float = Field(default=0.1, ge=0.0, le=0.5, description="Jitter range")

    # Task management
    default_timeout: int = Field(
        default=300, ge=30, le=3600, description="Default task timeout"
    )
    default_retries: int = Field(
        default=3, ge=0, le=10, description="Default retry attempts"
    )
    cleanup_interval: int = Field(
        default=3600, ge=60, le=86400, description="Cleanup interval"
    )

    # Monitoring
    enable_task_monitoring: bool = Field(
        default=True, description="Enable task monitoring"
    )
    health_check_interval: int = Field(
        default=60, ge=10, le=3600, description="Health check interval"
    )


class ServiceHealthStatus(BaseModel):
    """Type-safe service health status."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    status: str = Field(..., pattern=r"^(healthy|unhealthy|degraded|unknown)$")
    service_name: str = Field(..., description="Service name")
    last_check: str = Field(..., description="Last health check timestamp")

    # Health details
    response_time_ms: Optional[float] = Field(
        default=None, ge=0.0, description="Response time"
    )
    error_rate: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Error rate"
    )
    uptime_seconds: Optional[int] = Field(
        default=None, ge=0, description="Service uptime"
    )

    # Error information
    last_error: Optional[str] = Field(default=None, description="Last error message")
    error_count: int = Field(default=0, ge=0, description="Total error count")


class ServiceOperationResult(BaseModel):
    """Type-safe service operation result."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    success: bool = Field(..., description="Operation success status")
    service_name: str = Field(..., description="Service name")
    operation: str = Field(..., description="Operation name")

    # Timing
    start_time: str = Field(..., description="Operation start time")
    duration_seconds: float = Field(..., ge=0.0, description="Operation duration")

    # Result data
    result: Optional[dict] = Field(default=None, description="Operation result data")
    items_processed: int = Field(default=0, ge=0, description="Items processed")

    # Error information
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    error_code: Optional[str] = Field(default=None, description="Error code if failed")


# Export all models
__all__ = [
    "DriverBrowserConfig",
    "LLMConfig",
    "WebSocketConfig",
    "LoggerConfig",
    "MetricsConfig",
    "SchedulerConfig",
    "ServiceHealthStatus",
    "ServiceOperationResult",
]
