"""
Performance Monitoring Data Transfer Objects

DTO models for enterprise performance monitoring system functionality.
These models provide type-safe performance metrics, alerts, and reporting.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict

from unrealon_sdk.src.utils import generate_correlation_id


class MetricType(str, Enum):
    """Types of performance metrics."""
    
    COUNTER = "counter"           # Incrementing values (requests, errors)
    GAUGE = "gauge"              # Point-in-time values (memory, CPU)
    HISTOGRAM = "histogram"       # Distribution of values (response times)
    TIMER = "timer"              # Elapsed time measurements
    RATE = "rate"                # Events per time unit


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricUnit(str, Enum):
    """Metric measurement units."""
    
    # Time units
    MILLISECONDS = "ms"
    SECONDS = "s"
    MINUTES = "min"
    
    # Size units
    BYTES = "bytes"
    KILOBYTES = "kb"
    MEGABYTES = "mb"
    
    # Rate units
    PER_SECOND = "/s"
    PER_MINUTE = "/min"
    
    # Percentage
    PERCENT = "%"
    
    # Count
    COUNT = "count"


@dataclass
class MetricValue:
    """Individual metric measurement."""
    
    timestamp: datetime
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricThreshold:
    """Threshold configuration for alerting."""
    
    warning_threshold: Optional[float] = None
    error_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    
    # For rate-based alerts (e.g., error rate)
    time_window_seconds: float = 60.0
    min_samples: int = 5


class PerformanceMetric(BaseModel):
    """Performance metric model with metadata."""
    
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Metric name")
    metric_type: MetricType = Field(..., description="Type of metric")
    unit: MetricUnit = Field(..., description="Measurement unit")
    description: str = Field(..., description="Metric description")
    
    # Current values
    current_value: Optional[float] = Field(default=None, description="Latest value")
    total_samples: int = Field(default=0, description="Total number of samples")
    
    # Statistical data
    min_value: Optional[float] = Field(default=None, description="Minimum recorded value")
    max_value: Optional[float] = Field(default=None, description="Maximum recorded value")
    avg_value: Optional[float] = Field(default=None, description="Average value")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags")


class PerformanceAlert(BaseModel):
    """Performance alert model."""
    
    model_config = ConfigDict(extra="forbid")
    
    alert_id: str = Field(default_factory=generate_correlation_id)
    metric_name: str = Field(..., description="Name of metric that triggered alert")
    severity: AlertSeverity = Field(..., description="Alert severity")
    threshold_value: float = Field(..., description="Threshold that was exceeded")
    current_value: float = Field(..., description="Current metric value")
    message: str = Field(..., description="Alert message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = Field(default=False, description="Whether alert was acknowledged")
    resolved: bool = Field(default=False, description="Whether alert was resolved")


class PerformanceReport(BaseModel):
    """Comprehensive performance report."""
    
    model_config = ConfigDict(extra="forbid")
    
    report_id: str = Field(default_factory=generate_correlation_id)
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    
    # System metrics
    avg_cpu_percent: float = Field(..., description="Average CPU usage")
    avg_memory_mb: float = Field(..., description="Average memory usage in MB")
    peak_memory_mb: float = Field(..., description="Peak memory usage in MB")
    
    # Operation metrics
    total_operations: int = Field(..., description="Total operations performed")
    avg_operation_time_ms: float = Field(..., description="Average operation time")
    error_rate_percent: float = Field(..., description="Error rate percentage")
    
    # Network metrics
    total_requests: int = Field(..., description="Total network requests")
    avg_response_time_ms: float = Field(..., description="Average response time")
    timeout_count: int = Field(..., description="Number of timeouts")
    
    # Alerts
    total_alerts: int = Field(..., description="Total alerts generated")
    critical_alerts: int = Field(..., description="Critical alerts")
    unresolved_alerts: int = Field(..., description="Unresolved alerts")


__all__ = [
    # Enums
    "MetricType",
    "AlertSeverity", 
    "MetricUnit",
    # Models
    "MetricValue",
    "MetricThreshold",
    "PerformanceMetric",
    "PerformanceAlert",
    "PerformanceReport",
]
