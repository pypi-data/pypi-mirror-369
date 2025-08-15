"""
Health Monitoring DTOs - Data Transfer Objects for health monitoring system.

This module contains all Pydantic models and enums related to system health monitoring,
separated from business logic for clean architecture and reusability.

Components:
- Health status and alert severity models
- Component health and system metrics models
- Health check configuration and diagnostics
- Monitoring and alerting data structures
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class ComponentStatus(str, Enum):
    """Component health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class HealthCheckType(str, Enum):
    """Types of health checks."""

    CONNECTION = "connection"
    DATABASE = "database"
    API = "api"
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    NETWORK = "network"
    CUSTOM = "custom"


class AlertSeverity(str, Enum):
    """Health alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class HealthCheckFrequency(str, Enum):
    """Health check frequency settings."""

    CONTINUOUS = "continuous"  # Real-time monitoring
    HIGH = "high"  # Every 5 seconds
    NORMAL = "normal"  # Every 30 seconds
    LOW = "low"  # Every 5 minutes
    CUSTOM = "custom"  # User-defined interval


class ConnectionHealthStatus(BaseModel):
    """Connection health status model."""

    model_config = ConfigDict(extra="forbid")

    # Connection info
    is_connected: bool = Field(..., description="Whether connection is active")
    last_ping_ms: Optional[float] = Field(default=None, description="Last ping time in ms")
    connection_uptime_seconds: float = Field(default=0.0, description="Connection uptime")

    # Quality metrics
    success_rate_percent: float = Field(default=100.0, description="Success rate percentage")
    error_count: int = Field(default=0, description="Number of errors")
    retry_count: int = Field(default=0, description="Number of retries")

    # Timestamps
    last_successful_request: Optional[datetime] = Field(
        default=None, description="Last successful request"
    )
    last_error: Optional[datetime] = Field(default=None, description="Last error time")
    status_changed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Status
    status: ComponentStatus = Field(default=ComponentStatus.UNKNOWN, description="Overall status")
    status_message: str = Field(default="", description="Status description")


class ComponentHealth(BaseModel):
    """Individual component health model."""

    model_config = ConfigDict(extra="forbid")

    # Component identification
    component_id: str = Field(..., description="Unique component identifier")
    component_name: str = Field(..., description="Human-readable component name")
    component_type: str = Field(..., description="Component type/category")

    # Health status
    status: ComponentStatus = Field(..., description="Current health status")
    status_message: str = Field(default="", description="Status description")
    last_check_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Metrics
    response_time_ms: Optional[float] = Field(
        default=None, description="Response time in milliseconds"
    )
    cpu_usage_percent: Optional[float] = Field(default=None, description="CPU usage percentage")
    memory_usage_percent: Optional[float] = Field(
        default=None, description="Memory usage percentage"
    )
    disk_usage_percent: Optional[float] = Field(default=None, description="Disk usage percentage")

    # Connection metrics (if applicable)
    connection_count: Optional[int] = Field(default=None, description="Active connections")
    error_rate_percent: Optional[float] = Field(default=None, description="Error rate percentage")

    # History
    uptime_seconds: float = Field(default=0.0, description="Component uptime")
    last_restart: Optional[datetime] = Field(default=None, description="Last restart time")
    restart_count: int = Field(default=0, description="Number of restarts")

    # Dependencies
    dependencies: List[str] = Field(default_factory=list, description="Component dependencies")
    dependent_components: List[str] = Field(
        default_factory=list, description="Dependent components"
    )

    # Metadata
    version: Optional[str] = Field(default=None, description="Component version")
    environment: Optional[str] = Field(default=None, description="Environment (dev/prod/etc)")
    tags: Dict[str, str] = Field(default_factory=dict, description="Component tags")


class HealthCheckConfig(BaseModel):
    """Health check configuration model."""

    model_config = ConfigDict(extra="forbid")

    # Basic settings
    enabled: bool = Field(default=True, description="Enable health checks")
    check_type: HealthCheckType = Field(..., description="Type of health check")
    frequency: HealthCheckFrequency = Field(
        default=HealthCheckFrequency.NORMAL, description="Check frequency"
    )
    custom_interval_seconds: Optional[float] = Field(
        default=None, description="Custom check interval"
    )

    # Timeout settings
    timeout_seconds: float = Field(default=30.0, description="Health check timeout")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay_seconds: float = Field(default=5.0, description="Delay between retries")

    # Thresholds
    warning_threshold: Optional[float] = Field(default=None, description="Warning threshold")
    error_threshold: Optional[float] = Field(default=None, description="Error threshold")
    critical_threshold: Optional[float] = Field(default=None, description="Critical threshold")

    # Alerting
    enable_alerts: bool = Field(default=True, description="Enable alerting")
    alert_on_status_change: bool = Field(default=True, description="Alert on status changes")
    alert_on_threshold_breach: bool = Field(default=True, description="Alert on threshold breaches")

    # Custom check settings
    custom_check_endpoint: Optional[str] = Field(default=None, description="Custom check endpoint")
    expected_response: Optional[str] = Field(default=None, description="Expected response")
    custom_headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")


class HealthAlert(BaseModel):
    """Health monitoring alert model."""

    model_config = ConfigDict(extra="forbid")

    # Alert identification
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component_id: str = Field(..., description="Component that triggered alert")
    alert_type: HealthCheckType = Field(..., description="Type of alert")

    # Alert details
    severity: AlertSeverity = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    description: Optional[str] = Field(default=None, description="Detailed description")

    # Timing
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(default=None, description="When alert was resolved")
    acknowledged_at: Optional[datetime] = Field(
        default=None, description="When alert was acknowledged"
    )

    # Status tracking
    is_active: bool = Field(default=True, description="Whether alert is still active")
    is_acknowledged: bool = Field(default=False, description="Whether alert was acknowledged")
    is_resolved: bool = Field(default=False, description="Whether alert was resolved")

    # Context
    current_value: Optional[float] = Field(default=None, description="Current metric value")
    threshold_value: Optional[float] = Field(
        default=None, description="Threshold that was breached"
    )
    previous_status: Optional[ComponentStatus] = Field(
        default=None, description="Previous component status"
    )
    current_status: ComponentStatus = Field(..., description="Current component status")

    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict, description="Alert tags")
    additional_data: Dict[str, Any] = Field(
        default_factory=dict, description="Additional alert data"
    )


class SystemHealthSummary(BaseModel):
    """Overall system health summary model."""

    model_config = ConfigDict(extra="forbid")

    # Overall status
    overall_status: ComponentStatus = Field(..., description="Overall system status")
    healthy_components: int = Field(default=0, description="Number of healthy components")
    degraded_components: int = Field(default=0, description="Number of degraded components")
    unhealthy_components: int = Field(default=0, description="Number of unhealthy components")
    total_components: int = Field(default=0, description="Total number of components")

    # System metrics
    system_uptime_seconds: float = Field(default=0.0, description="System uptime")
    avg_response_time_ms: float = Field(default=0.0, description="Average response time")
    total_requests: int = Field(default=0, description="Total requests processed")
    error_rate_percent: float = Field(default=0.0, description="Overall error rate")

    # Resource utilization
    avg_cpu_usage_percent: float = Field(default=0.0, description="Average CPU usage")
    avg_memory_usage_percent: float = Field(default=0.0, description="Average memory usage")
    avg_disk_usage_percent: float = Field(default=0.0, description="Average disk usage")

    # Alert summary
    active_alerts: int = Field(default=0, description="Number of active alerts")
    critical_alerts: int = Field(default=0, description="Number of critical alerts")
    warning_alerts: int = Field(default=0, description="Number of warning alerts")

    # Timestamps
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    monitoring_since: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthCheckResult(BaseModel):
    """Health check execution result model."""

    model_config = ConfigDict(extra="forbid")

    # Check identification
    check_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component_id: str = Field(..., description="Component being checked")
    check_type: HealthCheckType = Field(..., description="Type of check")

    # Result
    status: ComponentStatus = Field(..., description="Check result status")
    success: bool = Field(..., description="Whether check was successful")
    response_time_ms: float = Field(..., description="Check response time")

    # Details
    message: str = Field(default="", description="Check result message")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional check details")

    # Metrics collected during check
    cpu_usage: Optional[float] = Field(default=None, description="CPU usage at check time")
    memory_usage: Optional[float] = Field(default=None, description="Memory usage at check time")
    disk_usage: Optional[float] = Field(default=None, description="Disk usage at check time")
    network_latency_ms: Optional[float] = Field(default=None, description="Network latency")

    # Timing
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Context
    retry_attempt: int = Field(default=0, description="Retry attempt number")
    is_retry: bool = Field(default=False, description="Whether this was a retry")


class HealthTrend(BaseModel):
    """Health trend analysis model."""

    model_config = ConfigDict(extra="forbid")

    # Component identification
    component_id: str = Field(..., description="Component ID")
    metric_name: str = Field(..., description="Metric being analyzed")

    # Trend analysis
    trend_direction: str = Field(..., description="Trend direction (up/down/stable)")
    trend_strength: float = Field(..., description="Trend strength (0.0-1.0)")
    change_percentage: float = Field(..., description="Percentage change")

    # Time periods
    analysis_period_hours: int = Field(..., description="Analysis period in hours")
    data_points: int = Field(..., description="Number of data points analyzed")

    # Statistical measures
    current_value: float = Field(..., description="Current metric value")
    average_value: float = Field(..., description="Average value in period")
    min_value: float = Field(..., description="Minimum value in period")
    max_value: float = Field(..., description="Maximum value in period")
    standard_deviation: float = Field(..., description="Standard deviation")

    # Predictions
    predicted_value_1h: Optional[float] = Field(
        default=None, description="Predicted value in 1 hour"
    )
    predicted_value_24h: Optional[float] = Field(
        default=None, description="Predicted value in 24 hours"
    )
    confidence_level: float = Field(default=0.0, description="Prediction confidence (0.0-1.0)")

    # Analysis timestamp
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    # Enums
    "ComponentStatus",
    "HealthCheckType",
    "AlertSeverity",
    "HealthCheckFrequency",
    # Core models
    "ConnectionHealthStatus",
    "ComponentHealth",
    "HealthCheckConfig",
    "HealthAlert",
    "SystemHealthSummary",
    "HealthCheckResult",
    "HealthTrend",
]
