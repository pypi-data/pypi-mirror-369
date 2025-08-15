"""
Concurrency & Threading DTOs - Data Transfer Objects for multithreading system.

This module contains all Pydantic models and enums related to concurrency management,
separated from business logic for clean architecture and reusability.

Components:
- Thread pool management and load balancing models
- Task scheduling and priority queue models
- Resource pooling and lifecycle management
- Performance optimization and monitoring models
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict


class ThreadPoolStrategy(str, Enum):
    """Thread pool management strategies."""

    FIXED = "fixed"  # Fixed number of threads
    DYNAMIC = "dynamic"  # Dynamic scaling based on load
    ADAPTIVE = "adaptive"  # ML-based adaptive scaling
    ELASTIC = "elastic"  # Cloud-style elastic scaling
    CUSTOM = "custom"  # Custom scaling algorithm


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies for task distribution."""

    ROUND_ROBIN = "round_robin"  # Simple round-robin
    LEAST_LOADED = "least_loaded"  # Assign to least loaded thread
    PERFORMANCE_BASED = "performance_based"  # Based on historical performance
    GEOGRAPHIC = "geographic"  # Geographic proximity
    RANDOM = "random"  # Random assignment
    WEIGHTED = "weighted"  # Weighted distribution


class TaskPriority(str, Enum):
    """Task priority levels."""

    CRITICAL = "critical"  # Highest priority - immediate execution
    HIGH = "high"  # High priority
    NORMAL = "normal"  # Normal priority
    LOW = "low"  # Low priority
    BACKGROUND = "background"  # Lowest priority - background tasks


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"  # Waiting in queue
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed with error
    CANCELLED = "cancelled"  # Cancelled before execution
    TIMEOUT = "timeout"  # Timed out during execution
    RETRYING = "retrying"  # Being retried after failure


class ResourceType(str, Enum):
    """Types of managed resources."""

    CONNECTION = "connection"  # Network connections
    THREAD = "thread"  # Thread resources
    MEMORY = "memory"  # Memory allocations
    FILE_HANDLE = "file_handle"  # File handles
    DATABASE = "database"  # Database connections
    CACHE = "cache"  # Cache resources
    CUSTOM = "custom"  # Custom resource type


class ResourceStatus(str, Enum):
    """Resource lifecycle status."""

    AVAILABLE = "available"  # Ready for use
    IN_USE = "in_use"  # Currently being used
    RESERVED = "reserved"  # Reserved for specific task
    EXHAUSTED = "exhausted"  # Resource limit reached
    ERROR = "error"  # Resource in error state
    MAINTENANCE = "maintenance"  # Under maintenance


class ConcurrencyEventType(str, Enum):
    """Concurrency monitoring event types."""

    THREAD_CREATED = "thread_created"
    THREAD_DESTROYED = "thread_destroyed"
    THREAD_IDLE = "thread_idle"
    THREAD_BUSY = "thread_busy"
    TASK_QUEUED = "task_queued"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DEADLOCK_DETECTED = "deadlock_detected"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    POOL_SCALED = "pool_scaled"


class ThreadPoolConfig(BaseModel):
    """Thread pool configuration model."""

    model_config = ConfigDict(extra="forbid")

    # Pool settings
    pool_name: str = Field(..., description="Thread pool name")
    strategy: ThreadPoolStrategy = Field(
        default=ThreadPoolStrategy.DYNAMIC, description="Pool strategy"
    )

    # Size limits
    min_threads: int = Field(default=2, description="Minimum number of threads")
    max_threads: int = Field(default=50, description="Maximum number of threads")
    core_threads: int = Field(default=5, description="Core number of threads")

    # Scaling parameters
    scale_up_threshold: float = Field(
        default=0.8, description="Scale up when utilization > threshold"
    )
    scale_down_threshold: float = Field(
        default=0.3, description="Scale down when utilization < threshold"
    )
    scale_up_factor: float = Field(default=1.5, description="Factor for scaling up")
    scale_down_factor: float = Field(default=0.8, description="Factor for scaling down")

    # Timing
    thread_idle_timeout_seconds: float = Field(default=60.0, description="Thread idle timeout")
    scaling_cooldown_seconds: float = Field(
        default=30.0, description="Cooldown between scaling operations"
    )

    # Queue settings
    max_queue_size: int = Field(default=1000, description="Maximum task queue size")
    queue_timeout_seconds: float = Field(default=30.0, description="Queue timeout")

    # Monitoring
    enable_monitoring: bool = Field(default=True, description="Enable thread monitoring")
    metrics_collection_interval: float = Field(
        default=10.0, description="Metrics collection interval"
    )

    # Load balancing
    load_balancing_strategy: LoadBalancingStrategy = Field(
        default=LoadBalancingStrategy.LEAST_LOADED, description="Load balancing strategy"
    )


class ThreadInfo(BaseModel):
    """Individual thread information model."""

    model_config = ConfigDict(extra="forbid")

    # Thread identification
    thread_id: str = Field(..., description="Thread identifier")
    thread_name: str = Field(..., description="Thread name")
    pool_name: str = Field(..., description="Pool this thread belongs to")

    # Status
    is_alive: bool = Field(..., description="Whether thread is alive")
    is_busy: bool = Field(default=False, description="Whether thread is executing task")
    current_task_id: Optional[str] = Field(default=None, description="Currently executing task ID")

    # Performance metrics
    total_tasks_executed: int = Field(default=0, description="Total tasks executed")
    avg_task_duration_ms: float = Field(default=0.0, description="Average task duration")
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Resource usage
    cpu_usage_percent: Optional[float] = Field(default=None, description="CPU usage percentage")
    memory_usage_mb: Optional[float] = Field(default=None, description="Memory usage in MB")

    # Timing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_task_start: Optional[datetime] = Field(default=None, description="Last task start time")
    last_task_end: Optional[datetime] = Field(default=None, description="Last task end time")

    # Health
    error_count: int = Field(default=0, description="Number of errors encountered")
    last_error: Optional[str] = Field(default=None, description="Last error message")


class Task(BaseModel):
    """Task execution model."""

    model_config = ConfigDict(extra="forbid")

    # Task identification
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str = Field(..., description="Task name")
    task_type: str = Field(..., description="Task type/category")

    # Priority and scheduling
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")

    # Execution context
    assigned_thread_id: Optional[str] = Field(default=None, description="Assigned thread ID")
    pool_name: Optional[str] = Field(default=None, description="Assigned pool name")

    # Timing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = Field(default=None, description="Scheduled execution time")
    started_at: Optional[datetime] = Field(default=None, description="Actual start time")
    completed_at: Optional[datetime] = Field(default=None, description="Completion time")

    # Performance
    estimated_duration_ms: Optional[float] = Field(default=None, description="Estimated duration")
    actual_duration_ms: Optional[float] = Field(default=None, description="Actual duration")
    timeout_seconds: Optional[float] = Field(default=None, description="Task timeout")

    # Dependencies
    dependencies: List[str] = Field(
        default_factory=list, description="Task dependencies (task IDs)"
    )
    dependents: List[str] = Field(default_factory=list, description="Tasks depending on this one")

    # Results and errors
    result: Optional[Any] = Field(default=None, description="Task result")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    # Context and metadata
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context data")
    tags: Dict[str, str] = Field(default_factory=dict, description="Task tags")


class ResourcePool(BaseModel):
    """Resource pool management model."""

    model_config = ConfigDict(extra="forbid")

    # Pool identification
    pool_id: str = Field(..., description="Pool identifier")
    pool_name: str = Field(..., description="Pool name")
    resource_type: ResourceType = Field(..., description="Type of resources in pool")

    # Pool configuration
    min_size: int = Field(default=1, description="Minimum pool size")
    max_size: int = Field(default=100, description="Maximum pool size")
    current_size: int = Field(default=0, description="Current pool size")

    # Resource status
    available_resources: int = Field(default=0, description="Available resources")
    in_use_resources: int = Field(default=0, description="Resources in use")
    reserved_resources: int = Field(default=0, description="Reserved resources")

    # Performance metrics
    total_requests: int = Field(default=0, description="Total resource requests")
    successful_acquisitions: int = Field(default=0, description="Successful acquisitions")
    failed_acquisitions: int = Field(default=0, description="Failed acquisitions")
    avg_acquisition_time_ms: float = Field(default=0.0, description="Average acquisition time")

    # Health and lifecycle
    status: ResourceStatus = Field(default=ResourceStatus.AVAILABLE, description="Pool status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_maintenance: Optional[datetime] = Field(default=None, description="Last maintenance time")

    # Auto-management
    auto_scale: bool = Field(default=True, description="Enable auto-scaling")
    scale_threshold: float = Field(default=0.8, description="Scaling threshold")
    idle_timeout_seconds: float = Field(default=300.0, description="Resource idle timeout")


class ConcurrencyMetrics(BaseModel):
    """Concurrency system metrics model."""

    model_config = ConfigDict(extra="forbid")

    # Thread pool metrics
    total_threads: int = Field(default=0, description="Total number of threads")
    active_threads: int = Field(default=0, description="Active threads")
    idle_threads: int = Field(default=0, description="Idle threads")
    thread_utilization_percent: float = Field(default=0.0, description="Thread utilization")

    # Task metrics
    total_tasks: int = Field(default=0, description="Total tasks processed")
    pending_tasks: int = Field(default=0, description="Tasks in queue")
    running_tasks: int = Field(default=0, description="Currently running tasks")
    completed_tasks: int = Field(default=0, description="Completed tasks")
    failed_tasks: int = Field(default=0, description="Failed tasks")

    # Performance metrics
    avg_task_duration_ms: float = Field(default=0.0, description="Average task duration")
    avg_queue_wait_time_ms: float = Field(default=0.0, description="Average queue wait time")
    throughput_tasks_per_second: float = Field(default=0.0, description="Tasks per second")

    # Resource metrics
    total_resource_pools: int = Field(default=0, description="Number of resource pools")
    total_resources: int = Field(default=0, description="Total managed resources")
    available_resources: int = Field(default=0, description="Available resources")
    resource_utilization_percent: float = Field(default=0.0, description="Resource utilization")

    # Error metrics
    deadlock_count: int = Field(default=0, description="Detected deadlocks")
    timeout_count: int = Field(default=0, description="Task timeouts")
    error_rate_percent: float = Field(default=0.0, description="Overall error rate")

    # System metrics
    cpu_usage_percent: float = Field(default=0.0, description="System CPU usage")
    memory_usage_mb: float = Field(default=0.0, description="System memory usage")

    # Timing
    measurement_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    measurement_end: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    collection_interval_seconds: float = Field(
        default=60.0, description="Metrics collection interval"
    )


class LoadBalancingDecision(BaseModel):
    """Load balancing decision model."""

    model_config = ConfigDict(extra="forbid")

    # Decision context
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = Field(..., description="Task being assigned")
    strategy_used: LoadBalancingStrategy = Field(..., description="Strategy used for decision")

    # Assignment result
    selected_thread_id: str = Field(..., description="Selected thread ID")
    selected_pool_name: str = Field(..., description="Selected pool name")

    # Decision factors
    thread_utilization: float = Field(..., description="Selected thread utilization")
    load_score: float = Field(..., description="Load balancing score")
    performance_history: Optional[float] = Field(default=None, description="Historical performance")

    # Alternative options
    alternative_threads: List[str] = Field(default_factory=list, description="Other thread options")
    rejection_reasons: Dict[str, str] = Field(
        default_factory=dict, description="Why others were rejected"
    )

    # Timing
    decision_time_ms: float = Field(..., description="Time taken to make decision")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeadlockDetection(BaseModel):
    """Deadlock detection result model."""

    model_config = ConfigDict(extra="forbid")

    # Detection info
    detection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Deadlock details
    involved_threads: List[str] = Field(..., description="Threads involved in deadlock")
    involved_resources: List[str] = Field(..., description="Resources involved")
    deadlock_chain: List[str] = Field(..., description="Chain of dependencies")

    # Resolution
    resolution_strategy: str = Field(..., description="Strategy used to resolve deadlock")
    resolved: bool = Field(default=False, description="Whether deadlock was resolved")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution time")

    # Impact
    affected_tasks: List[str] = Field(
        default_factory=list, description="Tasks affected by deadlock"
    )
    resolution_time_ms: Optional[float] = Field(default=None, description="Time to resolve")

    # Context
    system_state: Dict[str, Any] = Field(default_factory=dict, description="System state snapshot")


__all__ = [
    # Enums
    "ThreadPoolStrategy",
    "LoadBalancingStrategy",
    "TaskPriority",
    "TaskStatus",
    "ResourceType",
    "ResourceStatus",
    "ConcurrencyEventType",
    # Configuration models
    "ThreadPoolConfig",
    # Core models
    "ThreadInfo",
    "Task",
    "ResourcePool",
    "ConcurrencyMetrics",
    "LoadBalancingDecision",
    "DeadlockDetection",
]
