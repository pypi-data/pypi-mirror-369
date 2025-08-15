"""
Configuration management for UnrealOn SDK v1.0

Provides enterprise-grade configuration with:
- Minimal configuration philosophy (10 lines replaces 200+)
- Environment-specific settings
- Type-safe validation with Pydantic v2
- Feature toggles for enterprise capabilities
- Performance tuning options
"""

import os
import json
import yaml
from typing import Dict, Optional, List, Union
from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

from unrealon_sdk.src.clients.python_http.models import LogLevel, ParserType


class EnvironmentDefaults(BaseModel):
    """
    Type-safe environment-specific default values.

    Replaces Dict[str, Any] usage with properly typed configuration model.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    enable_monitoring: bool = Field(default=True, description="Enable monitoring")
    enable_logging: bool = Field(default=True, description="Enable logging")
    enable_error_recovery: bool = Field(default=True, description="Enable error recovery")
    request_timeout_ms: int = Field(default=30000, description="Request timeout in ms")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    connection_pool_size: int = Field(default=50, description="Connection pool size")
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    verbose_logging: bool = Field(default=False, description="Enable verbose logging")


class ProxyConfig(BaseModel):
    """Proxy management configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",  # Allow extra fields for backward compatibility
        frozen=False,  # Allow modifications for testing
    )

    rotation_strategy: str = Field(
        default="success_rate",
        description="Proxy rotation strategy",
        pattern=r"^(round_robin|success_rate|weighted_random|least_failures|least_used)$",
    )
    health_check_interval: int = Field(
        default=30, description="Health check interval in seconds", ge=10, le=300
    )
    failover_threshold: int = Field(
        default=3, description="Failures before proxy replacement", ge=1, le=10
    )
    session_persistence: bool = Field(
        default=True, description="Maintain proxy sessions across requests"
    )
    geographic_distribution: Optional[Dict[str, float]] = Field(
        default=None, description="Geographic proxy distribution weights"
    )

    # Legacy field names (for backward compatibility)
    enabled: Optional[bool] = Field(default=None, description="Legacy: Enable proxy management")
    providers: Optional[List[str]] = Field(
        default=None, description="Legacy: List of proxy providers"
    )
    max_failures_before_rotation: Optional[int] = Field(
        default=None, description="Legacy: Max failures before rotation"
    )

    @field_validator("geographic_distribution")
    @classmethod
    def validate_distribution(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        if v is not None:
            total = sum(v.values())
            if not (0.95 <= total <= 1.05):  # Allow small floating point errors
                raise ValueError("Geographic distribution weights must sum to 1.0")
        return v


class MultithreadingConfig(BaseModel):
    """Multithreading and concurrency configuration."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)

    max_workers: int = Field(default=10, description="Maximum concurrent workers", ge=1, le=100)
    distribution_strategy: str = Field(
        default="LOAD_BALANCING",
        description="Task distribution strategy",
        pattern=r"^(SEQUENTIAL|ROUND_ROBIN|LOAD_BALANCING|CUSTOM)$",
    )
    task_timeout: int = Field(default=300, description="Task timeout in seconds", ge=30, le=3600)
    queue_size: int = Field(default=1000, description="Task queue size", ge=10, le=10000)


class LoggingConfig(BaseModel):
    """Logging configuration for multi-destination logging."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",  # Allow extra fields for backward compatibility
        frozen=False,  # Allow modifications for testing
    )

    # New field names (preferred)
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Minimum log level")
    enable_file_logging: bool = Field(default=True, description="Enable file logging")
    enable_server_logging: bool = Field(
        default=True, description="Enable server logging via WebSocket"
    )
    enable_audit_logging: bool = Field(default=False, description="Enable audit trail logging")
    log_file_path: Optional[str] = Field(default=None, description="Custom log file path")

    # Legacy field names (for backward compatibility)
    level: Optional[LogLevel] = Field(default=None, description="Legacy: Minimum log level")
    console_enabled: Optional[bool] = Field(
        default=None, description="Legacy: Enable console logging"
    )
    file_enabled: Optional[bool] = Field(default=None, description="Legacy: Enable file logging")
    file_path: Optional[str] = Field(default=None, description="Legacy: Log file path")
    server_enabled: Optional[bool] = Field(
        default=None, description="Legacy: Enable server logging"
    )
    structured: Optional[bool] = Field(
        default=None, description="Legacy: Enable structured logging"
    )
    server_batch_size: Optional[int] = Field(default=None, description="Legacy: Server batch size")
    log_rotation_size_mb: int = Field(
        default=50, description="Log file rotation size in MB", ge=1, le=1000
    )
    log_rotation_count: int = Field(
        default=10, description="Number of rotated log files to keep", ge=1, le=100
    )
    structured_logging: bool = Field(default=True, description="Use structured JSON logging")

    # New enterprise fields for LoggingService
    enabled: bool = Field(default=True, description="Enable logging service")
    buffer_size: int = Field(
        default=100, description="Buffer size for batching logs", ge=10, le=10000
    )
    flush_interval_seconds: float = Field(
        default=5.0, description="Auto-flush interval in seconds", ge=0.1, le=60.0
    )
    destinations: List[str] = Field(
        default_factory=lambda: ["console", "websocket"], description="Log destinations"
    )


class MonitoringConfig(BaseModel):
    """Monitoring and analytics configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",  # Allow extra fields for backward compatibility
        frozen=False,  # Allow modifications for testing
    )

    # New field names (preferred)
    metrics_interval: int = Field(
        default=15, description="Metrics collection interval in seconds", ge=5, le=300
    )
    enable_health_checks: bool = Field(default=True, description="Enable health monitoring")
    enable_performance_profiling: bool = Field(
        default=False, description="Enable performance profiling"
    )
    enable_business_metrics: bool = Field(default=True, description="Enable business KPI tracking")
    enable_cost_tracking: bool = Field(
        default=True, description="Enable cost optimization tracking"
    )
    alert_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "error_rate": 0.05,
            "response_time_ms": 5000,
            "memory_usage_percent": 0.85,
            "success_rate": 0.95,
        },
        description="Alert threshold values",
    )

    # Legacy field names (for backward compatibility)
    enabled: Optional[bool] = Field(default=None, description="Legacy: Enable monitoring")
    health_check_interval: Optional[int] = Field(
        default=None, description="Legacy: Health check interval"
    )
    track_response_times: Optional[bool] = Field(
        default=None, description="Legacy: Track response times"
    )
    track_memory_usage: Optional[bool] = Field(
        default=None, description="Legacy: Track memory usage"
    )
    enable_alerts: Optional[bool] = Field(default=None, description="Legacy: Enable alerts")


class AdapterConfig(BaseSettings):
    """
    Main configuration class for UnrealOn Adapter Client.

    Minimal configuration philosophy - most settings have intelligent defaults.

    Example:
        config = AdapterConfig(
            api_key="up_dev_your_api_key",
            parser_id="my_parser",
            parser_name="My Parser",
            enable_proxy_rotation=True,
            enable_monitoring=True,
            enable_logging=True
        )
    """

    model_config = SettingsConfigDict(
        env_prefix="UNREALON_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="allow",  # Allow extra fields for backward compatibility
    )

    # Core connection settings
    server_url: str = Field(
        default="wss://api.unrealon.com", description="UnrealOn server WebSocket URL"
    )
    api_key: str = Field(
        ...,
        description="Developer API key",
        min_length=20,
        pattern=r"^up_(dev|prod)_[a-zA-Z0-9_]{16,}$",
    )
    parser_id: str = Field(
        ...,
        description="Unique parser identifier",
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    parser_name: str = Field(
        ..., description="Human-readable parser name", min_length=1, max_length=200
    )
    parser_type: ParserType = Field(default=ParserType.CUSTOM, description="Type of parser")

    # Environment and deployment
    environment: str = Field(
        default="development",
        description="Deployment environment",
        pattern=r"^(development|staging|production)$",
    )

    # Enterprise feature toggles
    enable_proxy_rotation: bool = Field(
        default=False, description="Enable intelligent proxy management"
    )
    enable_monitoring: bool = Field(default=True, description="Enable real-time monitoring")
    enable_logging: bool = Field(default=True, description="Enable multi-destination logging")
    enable_error_recovery: bool = Field(
        default=True, description="Enable production error handling"
    )
    enable_auto_scaling: bool = Field(
        default=False, description="Enable dynamic resource allocation"
    )

    # Performance and reliability settings
    request_timeout_ms: int = Field(
        default=30000, description="Request timeout in milliseconds", ge=5000, le=300000
    )
    max_retries: int = Field(default=3, description="Maximum retry attempts", ge=0, le=10)
    memory_limit_mb: Optional[int] = Field(
        default=None, description="Memory limit in MB", ge=128, le=32768
    )
    cpu_limit_percent: float = Field(
        default=0.8, description="CPU usage limit (0.0-1.0)", ge=0.1, le=1.0
    )
    connection_pool_size: int = Field(
        default=50, description="HTTP connection pool size", ge=1, le=1000
    )

    # Advanced configuration objects
    proxy_config: Optional[ProxyConfig] = Field(
        default=None, description="Proxy management configuration"
    )
    multithreading_config: Optional[MultithreadingConfig] = Field(
        default=None, description="Multithreading configuration"
    )
    logging_config: Optional[LoggingConfig] = Field(
        default=None, description="Logging configuration"
    )
    monitoring_config: Optional[MonitoringConfig] = Field(
        default=None, description="Monitoring configuration"
    )

    # Debug and development options
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    verbose_logging: bool = Field(default=False, description="Enable verbose logging")

    def __init__(self, **data) -> None:
        """Initialize configuration with intelligent defaults."""
        super().__init__(**data)

        # Auto-create sub-configurations if features are enabled
        if self.enable_proxy_rotation and self.proxy_config is None:
            self.proxy_config = ProxyConfig()

        if self.enable_monitoring and self.monitoring_config is None:
            self.monitoring_config = MonitoringConfig()

        if self.enable_logging and self.logging_config is None:
            self.logging_config = LoggingConfig()

        # Set multithreading config for production
        if self.environment == "production" and self.multithreading_config is None:
            self.multithreading_config = MultithreadingConfig(
                max_workers=20, distribution_strategy="LOAD_BALANCING"
            )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format and environment consistency."""
        if v.startswith("up_dev_"):
            # Development API key
            pass
        elif v.startswith("up_prod_"):
            # Production API key
            pass
        else:
            raise ValueError("API key must start with 'up_dev_' or 'up_prod_'")
        return v

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v: str) -> str:
        """Validate server URL format."""
        if not (v.startswith("ws://") or v.startswith("wss://")):
            raise ValueError("Server URL must be a WebSocket URL (ws:// or wss://)")
        return v

    def get_environment_specific_defaults(self) -> EnvironmentDefaults:
        """Get environment-specific default values."""
        if self.environment == "production":
            return EnvironmentDefaults(
                enable_monitoring=True,
                enable_logging=True,
                enable_error_recovery=True,
                request_timeout_ms=45000,
                max_retries=5,
                connection_pool_size=100,
                debug_mode=False,
                verbose_logging=False,
            )
        elif self.environment == "staging":
            return EnvironmentDefaults(
                enable_monitoring=True,
                enable_logging=True,
                enable_error_recovery=True,
                debug_mode=True,
                verbose_logging=False,
            )
        else:  # development
            return EnvironmentDefaults(
                enable_monitoring=True,
                enable_logging=True,
                enable_error_recovery=True,
                debug_mode=True,
                verbose_logging=True,
            )

    def to_dict(self) -> Dict[str, Union[str, int, bool, float, None]]:
        """Convert configuration to dictionary with type-safe values."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_env(cls) -> "AdapterConfig":
        """Create configuration from environment variables."""
        return cls()

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "AdapterConfig":
        """Load configuration from file."""
        file_path = Path(file_path)

        if not file_path.exists():
            from .exceptions import ConfigurationError

            raise ConfigurationError(f"Configuration file not found: {file_path}")

        if file_path.suffix == ".json":
            with file_path.open() as f:
                data = json.load(f)
        elif file_path.suffix in (".yaml", ".yml"):
            with file_path.open() as f:
                data = yaml.safe_load(f)
        else:
            from .exceptions import ConfigurationError

            raise ConfigurationError(f"Unsupported configuration file format: {file_path.suffix}")

        return cls(**data)

    def validate_for_environment(self) -> List[str]:
        """Validate configuration for current environment."""
        warnings = []

        if self.environment == "production":
            if not self.enable_monitoring:
                warnings.append("Monitoring should be enabled in production")
            if not self.enable_error_recovery:
                warnings.append("Error recovery should be enabled in production")
            if self.debug_mode:
                warnings.append("Debug mode should be disabled in production")
            if self.api_key.startswith("up_dev_"):
                warnings.append("Using development API key in production")

        return warnings


def create_development_config(
    api_key: str, parser_id: str, parser_name: str, **kwargs
) -> AdapterConfig:
    """Create a development configuration with sensible defaults."""
    return AdapterConfig(
        api_key=api_key,
        parser_id=parser_id,
        parser_name=parser_name,
        environment="development",
        debug_mode=True,
        verbose_logging=True,
        enable_monitoring=True,
        enable_logging=True,
        **kwargs,
    )


def create_production_config(
    api_key: str, parser_id: str, parser_name: str, **kwargs
) -> AdapterConfig:
    """Create a production configuration with enterprise features."""
    return AdapterConfig(
        api_key=api_key,
        parser_id=parser_id,
        parser_name=parser_name,
        environment="production",
        enable_proxy_rotation=True,
        enable_monitoring=True,
        enable_logging=True,
        enable_error_recovery=True,
        enable_auto_scaling=True,
        debug_mode=False,
        request_timeout_ms=45000,
        max_retries=5,
        connection_pool_size=100,
        **kwargs,
    )
