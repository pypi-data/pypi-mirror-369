"""
Task Scheduling DTOs - Data Transfer Objects for task scheduling system.

This module contains all Pydantic models, enums, and dataclasses related to task scheduling,
separated from business logic for clean architecture and reusability.

Components:
- Task scheduling types and strategies
- Schedule information and dependency management
- Task progress tracking and configuration
- Scheduler configuration and metrics
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict


class ScheduleType(str, Enum):
    """Task scheduling types."""

    IMMEDIATE = "immediate"  # Execute immediately
    DELAYED = "delayed"  # Execute after delay
    SCHEDULED = "scheduled"  # Execute at specific time
    RECURRING = "recurring"  # Recurring execution
    CRON = "cron"  # Cron-style scheduling


class TaskSchedulerStrategy(str, Enum):
    """Task scheduling strategies."""

    FIFO = "fifo"  # First In First Out
    PRIORITY = "priority"  # Priority-based
    DEADLINE = "deadline"  # Deadline-based (Earliest Deadline First)
    SHORTEST_JOB = "shortest_job"  # Shortest Job First
    FAIR_SHARE = "fair_share"  # Fair share scheduling
    ADAPTIVE = "adaptive"  # Adaptive based on performance


@dataclass
class ScheduleInfo:
    """Task scheduling information."""

    schedule_type: ScheduleType
    scheduled_time: Optional[datetime] = None
    delay_seconds: Optional[float] = None
    cron_expression: Optional[str] = None
    repeat_interval: Optional[timedelta] = None
    max_executions: Optional[int] = None
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None


@dataclass
class TaskDependency:
    """Task dependency relationship."""

    task_id: str
    depends_on: str
    dependency_type: str = "completion"  # completion, data, resource
    optional: bool = False
    timeout_seconds: Optional[float] = None


@dataclass
class TaskProgress:
    """Task execution progress tracking."""

    task_id: str
    current_step: int = 0
    total_steps: int = 1
    progress_percent: float = 0.0
    status_message: str = ""
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TaskSchedulerConfig(BaseModel):
    """Task scheduler configuration model."""

    model_config = ConfigDict(extra="forbid")

    # Core settings
    max_concurrent_tasks: int = Field(default=100, description="Maximum concurrent tasks")
    default_timeout_seconds: float = Field(default=300.0, description="Default task timeout")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=2.0, description="Retry backoff multiplier")

    # Dead letter queue
    enable_dead_letter_queue: bool = Field(default=True, description="Enable dead letter queue")
    dead_letter_max_size: int = Field(default=1000, description="Dead letter queue max size")

    # Scheduling
    schedule_resolution_seconds: float = Field(default=1.0, description="Schedule resolution")
    dependency_timeout_seconds: float = Field(default=3600.0, description="Dependency timeout")
    strategy: TaskSchedulerStrategy = Field(
        default=TaskSchedulerStrategy.PRIORITY, description="Scheduling strategy"
    )

    # Persistence and caching
    enable_task_persistence: bool = Field(default=False, description="Enable task persistence")
    enable_result_caching: bool = Field(default=True, description="Enable result caching")
    cache_ttl_seconds: float = Field(default=3600.0, description="Cache TTL in seconds")


__all__ = [
    # Enums
    "ScheduleType",
    "TaskSchedulerStrategy",
    # Data classes
    "ScheduleInfo",
    "TaskDependency",
    "TaskProgress",
    # Configuration models
    "TaskSchedulerConfig",
]
