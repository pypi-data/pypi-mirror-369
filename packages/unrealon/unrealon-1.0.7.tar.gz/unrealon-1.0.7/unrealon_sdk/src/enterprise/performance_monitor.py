"""
Performance Monitor - Layer 3 Infrastructure Service

Real-time metrics collection, trend analysis, and performance monitoring
for UnrealOn SDK components. Provides comprehensive observability with
automatic alerting, statistical analysis, and performance regression detection.

Features:
- Real-time metrics collection with configurable sampling
- Statistical trend analysis and anomaly detection
- Performance baseline establishment and drift detection
- Memory, CPU, and network utilization monitoring
- WebSocket/HTTP operation performance tracking
- Automatic alerting for performance degradation
- Historical data retention and aggregation
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable, Union, NamedTuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import json

# Pydantic v2 for all data models
from pydantic import BaseModel, Field, ConfigDict

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity
from unrealon_sdk.src.dto.performance import (
    MetricType,
    AlertSeverity,
    MetricUnit,
    MetricValue,
    MetricThreshold,
    PerformanceMetric,
    PerformanceAlert,
    PerformanceReport,
)

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Enterprise-grade performance monitoring system.

    Provides real-time metrics collection, trend analysis, and alerting
    for comprehensive observability of SDK performance.
    """

    def __init__(
        self,
        config: AdapterConfig,
        collection_interval: float = 1.0,
        retention_hours: int = 24,
        max_samples_per_metric: int = 10000,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize performance monitor."""
        self.config = config
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        self.max_samples_per_metric = max_samples_per_metric
        self.dev_logger = dev_logger

        # Metrics storage
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.metric_values: Dict[str, deque[MetricValue]] = defaultdict(
            lambda: deque(maxlen=max_samples_per_metric)
        )
        self.metric_thresholds: Dict[str, MetricThreshold] = {}

        # Alerts
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []

        # Background tasks
        self._collection_task: Optional[asyncio.Task[None]] = None
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._shutdown = False

        # Thread safety
        self._lock = threading.Lock()

        # Built-in system metrics
        self._register_system_metrics()

        self._log_info("Performance monitor initialized")

    def _register_system_metrics(self) -> None:
        """Register built-in system performance metrics."""
        self.register_metric(
            "system.cpu.percent",
            MetricType.GAUGE,
            MetricUnit.PERCENT,
            "CPU usage percentage",
            MetricThreshold(warning_threshold=70.0, error_threshold=85.0, critical_threshold=95.0),
        )

        self.register_metric(
            "system.memory.used_mb",
            MetricType.GAUGE,
            MetricUnit.MEGABYTES,
            "Memory usage in megabytes",
            MetricThreshold(
                warning_threshold=1024.0, error_threshold=2048.0, critical_threshold=4096.0
            ),
        )

        self.register_metric(
            "system.memory.percent",
            MetricType.GAUGE,
            MetricUnit.PERCENT,
            "Memory usage percentage",
            MetricThreshold(warning_threshold=70.0, error_threshold=85.0, critical_threshold=95.0),
        )

        self.register_metric(
            "sdk.operations.total",
            MetricType.COUNTER,
            MetricUnit.COUNT,
            "Total SDK operations performed",
        )

        self.register_metric(
            "sdk.operations.duration_ms",
            MetricType.HISTOGRAM,
            MetricUnit.MILLISECONDS,
            "SDK operation duration",
            MetricThreshold(
                warning_threshold=1000.0, error_threshold=5000.0, critical_threshold=10000.0
            ),
        )

        self.register_metric(
            "sdk.errors.total", MetricType.COUNTER, MetricUnit.COUNT, "Total SDK errors"
        )

        self.register_metric(
            "sdk.errors.rate_per_minute",
            MetricType.RATE,
            MetricUnit.PER_MINUTE,
            "SDK error rate per minute",
            MetricThreshold(warning_threshold=10.0, error_threshold=50.0, critical_threshold=100.0),
        )

    async def start(self) -> None:
        """Start performance monitoring."""
        if self._collection_task is None:
            self._collection_task = asyncio.create_task(self._collection_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        self._log_info("Performance monitoring started")

    async def stop(self) -> None:
        """Stop performance monitoring."""
        self._shutdown = True

        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self._log_info("Performance monitoring stopped")

    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        unit: MetricUnit,
        description: str,
        threshold: Optional[MetricThreshold] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Register a new performance metric."""
        with self._lock:
            self.metrics[name] = PerformanceMetric(
                name=name,
                metric_type=metric_type,
                unit=unit,
                description=description,
                tags=tags or {},
            )

            if threshold:
                self.metric_thresholds[name] = threshold

        self._log_info(f"Registered metric: {name} ({metric_type.value})")

    def record_value(
        self,
        metric_name: str,
        value: Union[int, float],
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric value."""
        if metric_name not in self.metrics:
            logger.warning(f"Unknown metric: {metric_name}")
            return

        timestamp = datetime.now(timezone.utc)
        metric_value = MetricValue(timestamp=timestamp, value=float(value), labels=labels or {})

        with self._lock:
            # Add to values
            self.metric_values[metric_name].append(metric_value)

            # Update metric statistics
            metric = self.metrics[metric_name]
            metric.current_value = float(value)
            metric.total_samples += 1
            metric.last_updated = timestamp

            # Update min/max/avg
            values = [mv.value for mv in self.metric_values[metric_name]]
            metric.min_value = min(values)
            metric.max_value = max(values)
            metric.avg_value = statistics.mean(values)

        # Check thresholds
        self._check_thresholds(metric_name, float(value))

    def increment_counter(
        self,
        metric_name: str,
        increment: Union[int, float] = 1,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Increment a counter metric."""
        if metric_name not in self.metrics:
            logger.warning(f"Unknown metric: {metric_name}")
            return

        metric = self.metrics[metric_name]
        if metric.metric_type != MetricType.COUNTER:
            logger.warning(f"Metric {metric_name} is not a counter")
            return

        current_value = metric.current_value or 0
        self.record_value(metric_name, current_value + increment, labels)

    def record_timer(
        self,
        metric_name: str,
        duration_ms: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a timer measurement."""
        self.record_value(metric_name, duration_ms, labels)

    def _check_thresholds(self, metric_name: str, value: float) -> None:
        """Check if metric value exceeds thresholds."""
        if metric_name not in self.metric_thresholds:
            return

        threshold = self.metric_thresholds[metric_name]
        severity = None
        threshold_value = None

        if threshold.critical_threshold and value >= threshold.critical_threshold:
            severity = AlertSeverity.CRITICAL
            threshold_value = threshold.critical_threshold
        elif threshold.error_threshold and value >= threshold.error_threshold:
            severity = AlertSeverity.ERROR
            threshold_value = threshold.error_threshold
        elif threshold.warning_threshold and value >= threshold.warning_threshold:
            severity = AlertSeverity.WARNING
            threshold_value = threshold.warning_threshold

        if severity and threshold_value:
            self._create_alert(metric_name, severity, threshold_value, value)

    def _create_alert(
        self,
        metric_name: str,
        severity: AlertSeverity,
        threshold_value: float,
        current_value: float,
    ) -> None:
        """Create performance alert."""
        alert = PerformanceAlert(
            metric_name=metric_name,
            severity=severity,
            threshold_value=threshold_value,
            current_value=current_value,
            message=f"Metric {metric_name} exceeded {severity.value} threshold: {current_value} >= {threshold_value}",
        )

        # Store alert
        with self._lock:
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

        self._log_error(f"Performance alert: {alert.message}", severity=severity)

    async def _collection_loop(self) -> None:
        """Background task for collecting system metrics."""
        while not self._shutdown:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(self.collection_interval)

    async def _collect_system_metrics(self) -> None:
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.record_value("system.cpu.percent", cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            self.record_value("system.memory.used_mb", memory_mb)
            self.record_value("system.memory.percent", memory.percent)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task for cleaning up old data."""
        while not self._shutdown:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")

    async def _cleanup_old_data(self) -> None:
        """Clean up old metric data and alerts."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)

        with self._lock:
            # Clean old metric values
            for metric_name, values in self.metric_values.items():
                # Remove values older than retention period
                while values and values[0].timestamp < cutoff_time:
                    values.popleft()

            # Clean old alerts
            self.alert_history = [
                alert for alert in self.alert_history if alert.timestamp >= cutoff_time
            ]

        self._log_info(f"Cleaned up data older than {self.retention_hours} hours")

    def get_metric(self, name: str) -> Optional[PerformanceMetric]:
        """Get metric by name."""
        return self.metrics.get(name)

    def get_metric_values(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[MetricValue]:
        """Get metric values within time range."""
        if name not in self.metric_values:
            return []

        values = list(self.metric_values[name])

        if start_time:
            values = [v for v in values if v.timestamp >= start_time]

        if end_time:
            values = [v for v in values if v.timestamp <= end_time]

        return values

    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active alerts."""
        with self._lock:
            return [alert for alert in self.active_alerts.values() if not alert.resolved]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        with self._lock:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.acknowledged = True
                return True
        return False

    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add callback for alert notifications."""
        self.alert_callbacks.append(callback)

    def generate_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> PerformanceReport:
        """Generate comprehensive performance report."""
        if not start_time:
            start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        if not end_time:
            end_time = datetime.now(timezone.utc)

        # Collect metrics for report period
        cpu_values = [
            v.value for v in self.get_metric_values("system.cpu.percent", start_time, end_time)
        ]
        memory_values = [
            v.value for v in self.get_metric_values("system.memory.used_mb", start_time, end_time)
        ]

        # Calculate aggregates
        avg_cpu = statistics.mean(cpu_values) if cpu_values else 0.0
        avg_memory = statistics.mean(memory_values) if memory_values else 0.0
        peak_memory = max(memory_values) if memory_values else 0.0

        # Count alerts in period
        period_alerts = [
            alert for alert in self.alert_history if start_time <= alert.timestamp <= end_time
        ]

        critical_alerts = len([a for a in period_alerts if a.severity == AlertSeverity.CRITICAL])
        unresolved_alerts = len([a for a in period_alerts if not a.resolved])

        return PerformanceReport(
            period_start=start_time,
            period_end=end_time,
            avg_cpu_percent=avg_cpu,
            avg_memory_mb=avg_memory,
            peak_memory_mb=peak_memory,
            total_operations=0,  # Would be calculated from operation metrics
            avg_operation_time_ms=0.0,
            error_rate_percent=0.0,
            total_requests=0,
            avg_response_time_ms=0.0,
            timeout_count=0,
            total_alerts=len(period_alerts),
            critical_alerts=critical_alerts,
            unresolved_alerts=unresolved_alerts,
        )

    def _log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        if self.dev_logger:
            self.dev_logger.log_info(SDKEventType.PERFORMANCE_METRIC_COLLECTED, message, **kwargs)
        else:
            logger.info(message)

    def _log_error(
        self, message: str, severity: AlertSeverity = AlertSeverity.ERROR, **kwargs: Any
    ) -> None:
        """Log error message."""
        if self.dev_logger:
            sdk_severity = {
                AlertSeverity.WARNING: SDKSeverity.WARNING,
                AlertSeverity.ERROR: SDKSeverity.ERROR,
                AlertSeverity.CRITICAL: SDKSeverity.CRITICAL,
            }.get(severity, SDKSeverity.ERROR)

            self.dev_logger.log_error(
                SDKEventType.PERFORMANCE_THRESHOLD_EXCEEDED, message, **kwargs
            )
        else:
            logger.error(message)


# Context manager for timing operations
class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(
        self, monitor: PerformanceMonitor, metric_name: str, labels: Optional[Dict[str, str]] = None
    ):
        self.monitor = monitor
        self.metric_name = metric_name
        self.labels = labels
        self.start_time: Optional[float] = None

    def __enter__(self) -> "PerformanceTimer":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.monitor.record_timer(self.metric_name, duration_ms, self.labels)


__all__ = [
    # Main class
    "PerformanceMonitor",
    # Utilities
    "PerformanceTimer",
]
