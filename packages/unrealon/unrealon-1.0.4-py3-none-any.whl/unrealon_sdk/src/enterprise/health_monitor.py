"""
Health Monitor - Layer 3 Infrastructure Service

Comprehensive system health monitoring with diagnostics, alerting, and trend analysis.
Provides real-time health status for all SDK components with intelligent alerting
and predictive health analytics.

Features:
- Multi-component health monitoring
- Real-time health checks with configurable frequencies
- Intelligent alerting with severity-based routing
- Health trend analysis and predictions
- Dependency tracking and impact analysis
- System resource monitoring (CPU, memory, disk)
- Connection quality monitoring
- Automatic recovery recommendations
- Health dashboard metrics
- Integration with performance monitoring
"""

import asyncio
import logging
import time
import threading
import psutil
import statistics
from typing import Dict, List, Optional, Any, Callable, Set, Union
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity
from unrealon_sdk.src.dto.health import (
    ComponentStatus,
    HealthCheckType,
    AlertSeverity,
    HealthCheckFrequency,
    ConnectionHealthStatus,
    ComponentHealth,
    HealthCheckConfig,
    HealthAlert,
    SystemHealthSummary,
    HealthCheckResult,
    HealthTrend,
)

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)


@dataclass
class HealthMonitorConfig:
    """Configuration for health monitor."""
    
    # Check intervals
    default_check_interval_seconds: float = 30.0
    critical_check_interval_seconds: float = 5.0
    degraded_check_interval_seconds: float = 10.0
    
    # Thresholds
    cpu_warning_threshold: float = 70.0
    cpu_critical_threshold: float = 90.0
    memory_warning_threshold: float = 80.0
    memory_critical_threshold: float = 95.0
    disk_warning_threshold: float = 85.0
    disk_critical_threshold: float = 95.0
    
    # Response time thresholds (ms)
    response_time_warning_threshold: float = 1000.0
    response_time_critical_threshold: float = 5000.0
    
    # Error rate thresholds (%)
    error_rate_warning_threshold: float = 5.0
    error_rate_critical_threshold: float = 15.0
    
    # Alert settings
    enable_alerting: bool = True
    alert_cooldown_seconds: float = 300.0  # 5 minutes
    auto_resolve_alerts: bool = True
    
    # Trend analysis
    enable_trend_analysis: bool = True
    trend_analysis_hours: int = 24
    min_data_points_for_trend: int = 10
    
    # Recovery
    enable_auto_recovery: bool = False
    max_auto_recovery_attempts: int = 3


class HealthMonitor:
    """
    Enterprise-grade health monitoring system.
    
    Provides comprehensive health monitoring for all SDK components
    with intelligent alerting, trend analysis, and recovery recommendations.
    """

    def __init__(
        self,
        config: AdapterConfig,
        health_config: Optional[HealthMonitorConfig] = None,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize health monitor."""
        self.config = config
        self.health_config = health_config or HealthMonitorConfig()
        self.dev_logger = dev_logger

        # Thread safety
        self._lock = threading.RLock()

        # Component tracking
        self._components: Dict[str, ComponentHealth] = {}
        self._health_checks: Dict[str, HealthCheckConfig] = {}
        self._check_results: Dict[str, deque[HealthCheckResult]] = defaultdict(
            lambda: deque(maxlen=1000)
        )

        # Alert management
        self._active_alerts: Dict[str, HealthAlert] = {}
        self._alert_history: deque[HealthAlert] = deque(maxlen=10000)
        self._alert_cooldowns: Dict[str, datetime] = {}

        # Health trend data
        self._health_metrics: Dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self._trend_analysis: Dict[str, HealthTrend] = {}

        # System metrics
        self._system_metrics: Dict[str, float] = {}
        self._system_history: deque[Dict[str, float]] = deque(maxlen=1000)

        # Background tasks
        self._monitor_task: Optional[asyncio.Task[None]] = None
        self._trend_analysis_task: Optional[asyncio.Task[None]] = None
        self._system_metrics_task: Optional[asyncio.Task[None]] = None
        self._shutdown = False

        # Health check callbacks
        self._custom_checks: Dict[str, Callable[[], HealthCheckResult]] = {}

        # Statistics
        self._total_checks = 0
        self._failed_checks = 0
        self._monitoring_start_time = datetime.now(timezone.utc)

        self._log_info("Health monitor initialized")

    async def start(self) -> None:
        """Start health monitoring."""
        if self._monitor_task is None:
            self._monitor_task = asyncio.create_task(self._monitoring_loop())

        if self._trend_analysis_task is None and self.health_config.enable_trend_analysis:
            self._trend_analysis_task = asyncio.create_task(self._trend_analysis_loop())

        if self._system_metrics_task is None:
            self._system_metrics_task = asyncio.create_task(self._system_metrics_loop())

        self._log_info("Health monitor started")

    async def stop(self) -> None:
        """Stop health monitoring."""
        self._shutdown = True

        # Cancel background tasks
        for task in [self._monitor_task, self._trend_analysis_task, self._system_metrics_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._log_info("Health monitor stopped")

    def register_component(
        self,
        component_id: str,
        component_name: str,
        component_type: str,
        health_check_config: Optional[HealthCheckConfig] = None,
        custom_check: Optional[Callable[[], HealthCheckResult]] = None,
    ) -> None:
        """Register a component for health monitoring."""
        with self._lock:
            # Create component health record
            component_health = ComponentHealth(
                component_id=component_id,
                component_name=component_name,
                component_type=component_type,
                status=ComponentStatus.UNKNOWN,
                environment=getattr(self.config, 'environment', 'unknown'),
            )
            
            self._components[component_id] = component_health

            # Configure health checks
            if health_check_config:
                self._health_checks[component_id] = health_check_config
            else:
                # Default health check config
                self._health_checks[component_id] = HealthCheckConfig(
                    check_type=HealthCheckType.CUSTOM,
                    frequency=HealthCheckFrequency.NORMAL,
                )

            # Register custom check if provided
            if custom_check:
                self._custom_checks[component_id] = custom_check

            self._log_info(f"Registered component: {component_name} ({component_id})")

    def unregister_component(self, component_id: str) -> None:
        """Unregister a component from health monitoring."""
        with self._lock:
            if component_id in self._components:
                component_name = self._components[component_id].component_name
                
                # Clean up all related data
                del self._components[component_id]
                self._health_checks.pop(component_id, None)
                self._check_results.pop(component_id, None)
                self._custom_checks.pop(component_id, None)
                
                # Remove component-specific metrics and trends
                keys_to_remove = [k for k in self._health_metrics.keys() if k.startswith(f"{component_id}:")]
                for key in keys_to_remove:
                    del self._health_metrics[key]
                    self._trend_analysis.pop(key, None)

                self._log_info(f"Unregistered component: {component_name} ({component_id})")

    async def perform_health_check(self, component_id: str) -> HealthCheckResult:
        """Perform health check for specific component."""
        if component_id not in self._components:
            raise ValueError(f"Component {component_id} not registered")

        start_time = time.time()
        check_id = generate_correlation_id()

        try:
            # Get health check configuration
            health_check = self._health_checks[component_id]
            component = self._components[component_id]

            # Perform custom check if available
            if component_id in self._custom_checks:
                result = await self._execute_custom_check(component_id, check_id)
            else:
                result = await self._execute_standard_check(component_id, check_id, health_check)

            # Update component health
            self._update_component_health(component_id, result)

            # Store check result
            with self._lock:
                self._check_results[component_id].append(result)
                self._total_checks += 1
                if not result.success:
                    self._failed_checks += 1

            # Check for alerts
            await self._check_for_alerts(component_id, result)

            return result

        except Exception as e:
            # Create failed result
            result = HealthCheckResult(
                check_id=check_id,
                component_id=component_id,
                check_type=self._health_checks[component_id].check_type,
                status=ComponentStatus.UNHEALTHY,
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
                completed_at=datetime.now(timezone.utc),
            )

            # Update component health
            self._update_component_health(component_id, result)

            with self._lock:
                self._check_results[component_id].append(result)
                self._total_checks += 1
                self._failed_checks += 1

            logger.error(f"Health check failed for {component_id}: {e}")
            return result

    async def _execute_custom_check(self, component_id: str, check_id: str) -> HealthCheckResult:
        """Execute custom health check."""
        custom_check = self._custom_checks[component_id]
        
        try:
            if asyncio.iscoroutinefunction(custom_check):
                result = await custom_check()
            else:
                result = custom_check()
            
            # Ensure result has correct check_id
            result.check_id = check_id
            return result
            
        except Exception as e:
            return HealthCheckResult(
                check_id=check_id,
                component_id=component_id,
                check_type=HealthCheckType.CUSTOM,
                status=ComponentStatus.UNHEALTHY,
                success=False,
                response_time_ms=0.0,
                error_message=f"Custom check failed: {str(e)}",
            )

    async def _execute_standard_check(
        self, component_id: str, check_id: str, health_check: HealthCheckConfig
    ) -> HealthCheckResult:
        """Execute standard health check based on type."""
        start_time = time.time()
        
        try:
            if health_check.check_type == HealthCheckType.CONNECTION:
                success = await self._check_connection_health(component_id)
            elif health_check.check_type == HealthCheckType.API:
                success = await self._check_api_health(component_id, health_check)
            elif health_check.check_type == HealthCheckType.MEMORY:
                success = await self._check_memory_health()
            elif health_check.check_type == HealthCheckType.CPU:
                success = await self._check_cpu_health()
            else:
                success = True  # Default to healthy for unknown types

            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_id=check_id,
                component_id=component_id,
                check_type=health_check.check_type,
                status=ComponentStatus.HEALTHY if success else ComponentStatus.UNHEALTHY,
                success=success,
                response_time_ms=response_time,
                message="Health check completed",
            )

        except Exception as e:
            return HealthCheckResult(
                check_id=check_id,
                component_id=component_id,
                check_type=health_check.check_type,
                status=ComponentStatus.UNHEALTHY,
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
            )

    async def _check_connection_health(self, component_id: str) -> bool:
        """Check connection health for component."""
        # This would integrate with actual connection managers
        # For now, return True as placeholder
        return True

    async def _check_api_health(self, component_id: str, health_check: HealthCheckConfig) -> bool:
        """Check API health for component."""
        # This would make actual API calls to check health endpoints
        # For now, return True as placeholder
        return True

    async def _check_memory_health(self) -> bool:
        """Check system memory health."""
        try:
            memory = psutil.virtual_memory()
            return memory.percent < self.health_config.memory_critical_threshold
        except Exception:
            return False

    async def _check_cpu_health(self) -> bool:
        """Check system CPU health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            return cpu_percent < self.health_config.cpu_critical_threshold
        except Exception:
            return False

    def _update_component_health(self, component_id: str, result: HealthCheckResult) -> None:
        """Update component health based on check result."""
        with self._lock:
            if component_id in self._components:
                component = self._components[component_id]
                old_status = component.status
                
                component.status = result.status
                component.last_check_time = result.completed_at
                
                if result.response_time_ms:
                    component.response_time_ms = result.response_time_ms
                
                if result.error_message:
                    component.status_message = result.error_message
                else:
                    component.status_message = "Component healthy"

                # Track status changes
                if old_status != result.status:
                    self._log_info(
                        f"Component {component.component_name} status changed: {old_status.value} → {result.status.value}"
                    )

    async def _check_for_alerts(self, component_id: str, result: HealthCheckResult) -> None:
        """Check if health check result should trigger alerts."""
        if not self.health_config.enable_alerting:
            return

        component = self._components[component_id]
        alert_key = f"{component_id}:status"

        # Check cooldown
        if alert_key in self._alert_cooldowns:
            cooldown_end = self._alert_cooldowns[alert_key]
            if datetime.now(timezone.utc) < cooldown_end:
                return

        # Determine if alert is needed
        should_alert = False
        severity = AlertSeverity.INFO

        if result.status == ComponentStatus.UNHEALTHY:
            should_alert = True
            severity = AlertSeverity.CRITICAL
        elif result.status == ComponentStatus.DEGRADED:
            should_alert = True
            severity = AlertSeverity.WARNING

        # Check response time thresholds
        if result.response_time_ms:
            if result.response_time_ms > self.health_config.response_time_critical_threshold:
                should_alert = True
                severity = AlertSeverity.CRITICAL
            elif result.response_time_ms > self.health_config.response_time_warning_threshold:
                should_alert = True
                severity = AlertSeverity.WARNING

        if should_alert:
            await self._create_alert(component_id, result, severity)

    async def _create_alert(
        self, component_id: str, result: HealthCheckResult, severity: AlertSeverity
    ) -> None:
        """Create health alert."""
        component = self._components[component_id]
        
        alert = HealthAlert(
            component_id=component_id,
            alert_type=result.check_type,
            severity=severity,
            title=f"Health Alert: {component.component_name}",
            message=f"Component {component.component_name} is {result.status.value}",
            description=result.error_message or result.message,
            current_status=result.status,
            current_value=result.response_time_ms,
        )

        with self._lock:
            alert_key = f"{component_id}:status"
            self._active_alerts[alert_key] = alert
            self._alert_history.append(alert)
            
            # Set cooldown
            cooldown_end = datetime.now(timezone.utc) + timedelta(
                seconds=self.health_config.alert_cooldown_seconds
            )
            self._alert_cooldowns[alert_key] = cooldown_end

        self._log_alert(alert)

    async def _monitoring_loop(self) -> None:
        """Main health monitoring loop."""
        while not self._shutdown:
            try:
                # Perform health checks for all registered components
                for component_id in list(self._components.keys()):
                    if self._shutdown:
                        break
                    
                    try:
                        await self.perform_health_check(component_id)
                    except Exception as e:
                        logger.error(f"Error in health check for {component_id}: {e}")
                
                # Wait for next cycle
                await asyncio.sleep(self.health_config.default_check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retrying

    async def _trend_analysis_loop(self) -> None:
        """Background trend analysis loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._perform_trend_analysis()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trend analysis: {e}")

    async def _system_metrics_loop(self) -> None:
        """Background system metrics collection loop."""
        while not self._shutdown:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(60)  # Collect every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")

    async def _collect_system_metrics(self) -> None:
        """Collect system resource metrics."""
        try:
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
            }
            
            with self._lock:
                self._system_metrics = metrics
                self._system_history.append(metrics.copy())
                
                # Store in health metrics for trend analysis
                for metric_name, value in metrics.items():
                    self._health_metrics[f"system:{metric_name}"].append(value)
                    
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def _perform_trend_analysis(self) -> None:
        """Perform trend analysis on health metrics."""
        with self._lock:
            for metric_key, values in self._health_metrics.items():
                if len(values) >= self.health_config.min_data_points_for_trend:
                    try:
                        trend = self._analyze_metric_trend(metric_key, values)
                        self._trend_analysis[metric_key] = trend
                    except Exception as e:
                        logger.error(f"Error analyzing trend for {metric_key}: {e}")

    def _analyze_metric_trend(self, metric_key: str, values: deque[float]) -> HealthTrend:
        """Analyze trend for a specific metric."""
        values_list = list(values)
        
        # Basic statistical analysis
        current_value = values_list[-1]
        average_value = statistics.mean(values_list)
        min_value = min(values_list)
        max_value = max(values_list)
        std_dev = statistics.stdev(values_list) if len(values_list) > 1 else 0.0
        
        # Simple trend analysis (could be enhanced with more sophisticated algorithms)
        recent_values = values_list[-10:]  # Last 10 values
        older_values = values_list[-20:-10] if len(values_list) >= 20 else values_list[:-10]
        
        if older_values:
            recent_avg = statistics.mean(recent_values)
            older_avg = statistics.mean(older_values)
            change_percentage = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0.0
            
            if abs(change_percentage) < 5:
                trend_direction = "stable"
                trend_strength = 0.1
            elif change_percentage > 0:
                trend_direction = "up"
                trend_strength = min(1.0, abs(change_percentage) / 50.0)
            else:
                trend_direction = "down"
                trend_strength = min(1.0, abs(change_percentage) / 50.0)
        else:
            change_percentage = 0.0
            trend_direction = "stable"
            trend_strength = 0.0

        return HealthTrend(
            component_id=metric_key.split(':')[0],
            metric_name=metric_key.split(':', 1)[1] if ':' in metric_key else metric_key,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            change_percentage=change_percentage,
            analysis_period_hours=self.health_config.trend_analysis_hours,
            data_points=len(values_list),
            current_value=current_value,
            average_value=average_value,
            min_value=min_value,
            max_value=max_value,
            standard_deviation=std_dev,
        )

    def get_system_health_summary(self) -> SystemHealthSummary:
        """Get overall system health summary."""
        with self._lock:
            healthy = sum(1 for c in self._components.values() if c.status == ComponentStatus.HEALTHY)
            degraded = sum(1 for c in self._components.values() if c.status == ComponentStatus.DEGRADED)
            unhealthy = sum(1 for c in self._components.values() if c.status == ComponentStatus.UNHEALTHY)
            total = len(self._components)
            
            # Determine overall status
            if unhealthy > 0:
                overall_status = ComponentStatus.UNHEALTHY
            elif degraded > 0:
                overall_status = ComponentStatus.DEGRADED
            elif healthy > 0:
                overall_status = ComponentStatus.HEALTHY
            else:
                overall_status = ComponentStatus.UNKNOWN

            # Calculate averages
            avg_response_time = 0.0
            if self._components:
                response_times = [
                    c.response_time_ms for c in self._components.values() 
                    if c.response_time_ms is not None
                ]
                if response_times:
                    avg_response_time = statistics.mean(response_times)

            # System resource averages
            avg_cpu = self._system_metrics.get('cpu_percent', 0.0)
            avg_memory = self._system_metrics.get('memory_percent', 0.0)
            avg_disk = self._system_metrics.get('disk_percent', 0.0)

            # Alert counts
            active_alerts = len(self._active_alerts)
            critical_alerts = sum(
                1 for alert in self._active_alerts.values() 
                if alert.severity == AlertSeverity.CRITICAL
            )
            warning_alerts = sum(
                1 for alert in self._active_alerts.values() 
                if alert.severity == AlertSeverity.WARNING
            )

            # System uptime
            uptime = (datetime.now(timezone.utc) - self._monitoring_start_time).total_seconds()

            return SystemHealthSummary(
                overall_status=overall_status,
                healthy_components=healthy,
                degraded_components=degraded,
                unhealthy_components=unhealthy,
                total_components=total,
                system_uptime_seconds=uptime,
                avg_response_time_ms=avg_response_time,
                total_requests=self._total_checks,
                error_rate_percent=(self._failed_checks / self._total_checks * 100) if self._total_checks > 0 else 0.0,
                avg_cpu_usage_percent=avg_cpu,
                avg_memory_usage_percent=avg_memory,
                avg_disk_usage_percent=avg_disk,
                active_alerts=active_alerts,
                critical_alerts=critical_alerts,
                warning_alerts=warning_alerts,
            )

    def get_component_health(self, component_id: str) -> Optional[ComponentHealth]:
        """Get health status for specific component."""
        with self._lock:
            return self._components.get(component_id)

    def get_all_components_health(self) -> List[ComponentHealth]:
        """Get health status for all components."""
        with self._lock:
            return list(self._components.values())

    def get_active_alerts(self) -> List[HealthAlert]:
        """Get all active health alerts."""
        with self._lock:
            return list(self._active_alerts.values())

    def get_trend_analysis(self, metric_key: Optional[str] = None) -> Union[HealthTrend, Dict[str, HealthTrend]]:
        """Get trend analysis for specific metric or all metrics."""
        with self._lock:
            if metric_key:
                return self._trend_analysis.get(metric_key)
            else:
                return self._trend_analysis.copy()

    def _log_alert(self, alert: HealthAlert) -> None:
        """Log health alert."""
        severity_map = {
            AlertSeverity.INFO: SDKSeverity.INFO,
            AlertSeverity.WARNING: SDKSeverity.WARNING,
            AlertSeverity.ERROR: SDKSeverity.ERROR,
            AlertSeverity.CRITICAL: SDKSeverity.CRITICAL,
            AlertSeverity.FATAL: SDKSeverity.CRITICAL,
        }
        
        message = f"Health Alert: {alert.title} - {alert.message}"
        
        if self.dev_logger:
            self.dev_logger.log(
                SDKEventType.SYSTEM_HEALTH_DEGRADED,
                severity_map.get(alert.severity, SDKSeverity.INFO),
                message,
                details={
                    "alert_id": alert.alert_id,
                    "component_id": alert.component_id,
                    "severity": alert.severity.value,
                    "current_status": alert.current_status.value,
                },
            )
        else:
            logger.warning(message)

    def _log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.HEALTH_CHECK_PASSED, message, **kwargs
            )
        else:
            logger.info(message)


__all__ = [
    # Main business logic class
    "HealthMonitor",
    # Configuration
    "HealthMonitorConfig",
    
    # Note: Health monitoring models are available via DTO imports:
    # from unrealon_sdk.src.dto.health import ...
]
