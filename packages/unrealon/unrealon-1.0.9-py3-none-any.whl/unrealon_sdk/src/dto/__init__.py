"""
UnrealOn SDK Data Transfer Objects (DTOs)

Custom Pydantic models for type-safe data transfer within the SDK.
These models complement auto-generated client models with SDK-specific functionality.

Architecture:
- /clients/     - Auto-generated models (DO NOT EDIT)
- /core/models/ - Core SDK models (base functionality)
- /dto/         - Custom DTO models (SDK-specific data structures)

All models follow CRITICAL_REQUIREMENTS.md:
- 100% Pydantic v2 with strict validation
- No Dict[str, Any] usage - type-safe models only
- Full type annotations for all fields
- Python 3.9+ compatibility (no X | Y syntax)
"""

# Event-related DTOs
from .events import (
    EventMetadata,
    EventSubscriptionFilter,
    EventDeliveryResult,
    EventStatistics,
)

# WebSocket connection DTOs
from .websocket import (
    WebSocketConnectionState,
)

# Health and monitoring DTOs
from .health import (
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

# Authentication DTOs
from .authentication import (
    AuthenticationStatus,
    SecurityEventType,
    AuthenticationContext,
    SecurityEvent,
    RateLimitConfig,
)

# Logging DTOs (development logging)
from .logging import (
    LogDestination,
    SDKEventType,
    SDKSeverity,
    SDKContext,
    SDKDevelopmentEvent,
)

# Structured Logging DTOs (enterprise logging service)
from .structured_logging import (
    LogBuffer,
)

# Performance Monitoring DTOs
from .performance import (
    MetricType,
    AlertSeverity,
    MetricUnit,
    MetricValue,
    MetricThreshold,
    PerformanceMetric,
    PerformanceAlert,
    PerformanceReport,
)

# Cache Management DTOs
from .cache import (
    CachePolicy,
    CacheLevel,
    CacheEventType,
    CacheEntry,
    CacheStatistics,
    CacheConfig,
    CacheOperation,
    CacheMetrics,
)

# Rate Limiting DTOs
from .rate_limiting import (
    RateLimitStrategy,
    BackoffStrategy,
    RateLimitScope,
    RateLimitStatus,
    RateLimitEventType,
    RateLimitConfig,
    RateLimitQuota,
    RateLimitRequest,
    RateLimitStatistics,
    BackoffState,
)

# Concurrency & Threading DTOs
from .concurrency import (
    ThreadPoolStrategy,
    LoadBalancingStrategy,
    TaskPriority,
    TaskStatus,
    ResourceType,
    ResourceStatus,
    ConcurrencyEventType,
    ThreadPoolConfig,
    ThreadInfo,
    Task,
    ResourcePool,
    ConcurrencyMetrics,
    LoadBalancingDecision,
    DeadlockDetection,
)

# Task Scheduling DTOs
from .task_scheduling import (
    ScheduleType,
    TaskSchedulerStrategy,
    ScheduleInfo,
    TaskDependency,
    TaskProgress,
    TaskSchedulerConfig,
)

# Resource Pooling DTOs
from .resource_pooling import (
    ResourceLifecycleState,
    PoolScalingStrategy,
    ResourceMetadata,
    PoolConfig,
)

# Load Balancing DTOs
from .load_balancing import (
    LoadBalancingAlgorithm,
    NodeHealthStatus,
    TrafficDirection,
    FailoverStrategy,
    CircuitBreakerState,
    LoadBalancerNode,
    LoadBalancingRule,
    LoadBalancingDecisionRequest,
    LoadBalancingDecisionResult,
    LoadBalancerStatistics,
    HealthCheckConfig,
    LoadBalancingSession,
)

# Common utility DTOs
# from .common import (
#     # Will be added as needed
# )

__all__ = [
    # Events
    "EventMetadata",
    "EventSubscriptionFilter",
    "EventDeliveryResult",
    "EventStatistics",
    # WebSocket
    "WebSocketConnectionState",
    # Health
    "ComponentStatus",
    "HealthCheckType",
    "AlertSeverity",
    "HealthCheckFrequency",
    "ConnectionHealthStatus",
    "ComponentHealth",
    "HealthCheckConfig",
    "HealthAlert",
    "SystemHealthSummary",
    "HealthCheckResult",
    "HealthTrend",
    # Authentication
    "AuthenticationStatus",
    "SecurityEventType",
    "AuthenticationContext",
    "SecurityEvent",
    "RateLimitConfig",
    # Logging (development)
    "LogDestination",
    "SDKEventType",
    "SDKSeverity",
    "SDKContext",
    "SDKDevelopmentEvent",
    # Structured Logging (enterprise service)
    "LogBuffer",
    # Performance Monitoring
    "MetricType",
    "AlertSeverity",
    "MetricUnit",
    "MetricValue",
    "MetricThreshold",
    "PerformanceMetric",
    "PerformanceAlert",
    "PerformanceReport",
    # Cache Management
    "CachePolicy",
    "CacheLevel",
    "CacheEventType",
    "CacheEntry",
    "CacheStatistics",
    "CacheConfig",
    "CacheOperation",
    "CacheMetrics",
    # Rate Limiting
    "RateLimitStrategy",
    "BackoffStrategy",
    "RateLimitScope",
    "RateLimitStatus",
    "RateLimitEventType",
    "RateLimitConfig",
    "RateLimitQuota",
    "RateLimitRequest",
    "RateLimitStatistics",
    "BackoffState",
    # Concurrency & Threading
    "ThreadPoolStrategy",
    "LoadBalancingStrategy",
    "TaskPriority",
    "TaskStatus",
    "ResourceType",
    "ResourceStatus",
    "ConcurrencyEventType",
    "ThreadPoolConfig",
    "ThreadInfo",
    "Task",
    "ResourcePool",
    "ConcurrencyMetrics",
    "LoadBalancingDecision",
    "DeadlockDetection",
    # Task Scheduling
    "ScheduleType",
    "TaskSchedulerStrategy",
    "ScheduleInfo",
    "TaskDependency",
    "TaskProgress",
    "TaskSchedulerConfig",
    # Resource Pooling
    "ResourceLifecycleState",
    "PoolScalingStrategy",
    "ResourceMetadata",
    "PoolConfig",
    # Load Balancing
    "LoadBalancingAlgorithm",
    "NodeHealthStatus",
    "TrafficDirection",
    "FailoverStrategy",
    "CircuitBreakerState",
    "LoadBalancerNode",
    "LoadBalancingRule",
    "LoadBalancingDecisionRequest",
    "LoadBalancingDecisionResult",
    "LoadBalancerStatistics",
    "HealthCheckConfig",
    "LoadBalancingSession",
]
