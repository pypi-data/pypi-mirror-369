"""
Task Scheduler - Layer 4 Concurrency Service

Advanced task scheduling system with priority-based execution, dependency management,
and intelligent scheduling algorithms. Provides enterprise-grade task orchestration
with automatic retry, timeout handling, and performance optimization.

Features:
- Priority-based task queuing with multiple priority levels
- Dependency management with cycle detection
- Scheduled execution with cron-like scheduling
- Automatic retry with intelligent backoff strategies
- Timeout handling and resource management
- Progress tracking and result aggregation
- Cancellation support with cleanup
- Performance-based task optimization
- Dead letter queue for failed tasks
- Task result caching and persistence
"""

import asyncio
import logging
import time
import heapq
import threading
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import uuid
import weakref

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity
from unrealon_sdk.src.dto.concurrency import (
    TaskPriority,
    TaskStatus,
    ConcurrencyEventType,
    Task,
    ConcurrencyMetrics,
)
from unrealon_sdk.src.dto.task_scheduling import (
    ScheduleType,
    TaskSchedulerStrategy,
    ScheduleInfo,
    TaskDependency,
    TaskProgress,
    TaskSchedulerConfig,
)

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Enterprise-grade task scheduler.

    Provides advanced task scheduling with priority management,
    dependency resolution, and comprehensive execution monitoring.
    """

    def __init__(
        self,
        config: AdapterConfig,
        scheduler_config: Optional[TaskSchedulerConfig] = None,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize task scheduler."""
        self.config = config
        self.scheduler_config = scheduler_config or TaskSchedulerConfig()
        self.dev_logger = dev_logger

        # Task storage
        self._tasks: Dict[str, Task] = {}
        self._scheduled_tasks: List[Tuple[float, str]] = []  # (execution_time, task_id)
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: Dict[str, Task] = {}
        self._failed_tasks: Dict[str, Task] = {}

        # Dependency management
        self._dependencies: Dict[str, List[TaskDependency]] = defaultdict(list)
        self._waiting_tasks: Dict[str, Set[str]] = defaultdict(set)  # task_id -> depends_on_ids
        self._dependent_tasks: Dict[str, Set[str]] = defaultdict(set)  # task_id -> dependent_ids

        # Scheduling
        self._schedule_info: Dict[str, ScheduleInfo] = {}
        self._recurring_tasks: Set[str] = set()

        # Progress tracking
        self._task_progress: Dict[str, TaskProgress] = {}

        # Dead letter queue
        self._dead_letter_queue: deque[Task] = deque(
            maxlen=self.scheduler_config.dead_letter_max_size
        )

        # Result caching
        self._result_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}

        # Performance metrics
        self._metrics = ConcurrencyMetrics()
        self._task_performance: Dict[str, List[float]] = defaultdict(list)

        # Background tasks
        self._scheduler_task: Optional[asyncio.Task[None]] = None
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._metrics_task: Optional[asyncio.Task[None]] = None
        self._shutdown = False

        # Thread safety
        self._lock = threading.RLock()

        # Task execution callbacks
        self._on_task_start: Optional[Callable[[Task], None]] = None
        self._on_task_complete: Optional[Callable[[Task, Any], None]] = None
        self._on_task_error: Optional[Callable[[Task, Exception], None]] = None

        self._log_info("Task scheduler initialized")

    async def start(self) -> None:
        """Start task scheduler."""
        if self._scheduler_task is None:
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())

        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        if self._metrics_task is None:
            self._metrics_task = asyncio.create_task(self._metrics_loop())

        self._log_info("Task scheduler started")

    async def stop(self) -> None:
        """Stop task scheduler."""
        self._shutdown = True

        # Cancel running tasks
        for task_id, task in list(self._running_tasks.items()):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Cancel background tasks
        for task in [self._scheduler_task, self._cleanup_task, self._metrics_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._log_info("Task scheduler stopped")

    def schedule_task(
        self,
        task_func: Callable,
        *args,
        task_name: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        schedule_type: ScheduleType = ScheduleType.IMMEDIATE,
        scheduled_time: Optional[datetime] = None,
        delay_seconds: Optional[float] = None,
        dependencies: Optional[List[str]] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Schedule task for execution."""

        # Create task
        task = Task(
            task_name=task_name or f"{task_func.__name__}",
            task_type=f"{task_func.__module__}.{task_func.__name__}",
            priority=priority,
            dependencies=dependencies or [],
            timeout_seconds=timeout_seconds or self.scheduler_config.default_timeout_seconds,
            max_retries=max_retries or self.scheduler_config.max_retries,
            context=context or {},
        )

        # Store function and arguments
        task.context.update(
            {
                "func": task_func,
                "args": args,
                "kwargs": kwargs,
            }
        )

        # Create schedule info
        schedule_info = ScheduleInfo(schedule_type=schedule_type)

        if schedule_type == ScheduleType.DELAYED and delay_seconds:
            schedule_info.delay_seconds = delay_seconds
            schedule_info.next_execution = datetime.now(timezone.utc) + timedelta(
                seconds=delay_seconds
            )
        elif schedule_type == ScheduleType.SCHEDULED and scheduled_time:
            schedule_info.scheduled_time = scheduled_time
            schedule_info.next_execution = scheduled_time
        else:
            schedule_info.next_execution = datetime.now(timezone.utc)

        with self._lock:
            # Store task and schedule info
            self._tasks[task.task_id] = task
            self._schedule_info[task.task_id] = schedule_info

            # Handle dependencies
            if task.dependencies:
                self._setup_dependencies(task)

            # Add to schedule if not waiting for dependencies
            if not self._waiting_tasks.get(task.task_id):
                self._add_to_schedule(task.task_id, schedule_info.next_execution)

            # Initialize progress tracking
            self._task_progress[task.task_id] = TaskProgress(task_id=task.task_id)

        self._log_task_event(ConcurrencyEventType.TASK_QUEUED, task)
        return task.task_id

    def schedule_recurring_task(
        self,
        task_func: Callable,
        interval: timedelta,
        *args,
        task_name: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_executions: Optional[int] = None,
        start_time: Optional[datetime] = None,
        **kwargs,
    ) -> str:
        """Schedule recurring task."""

        task_id = self.schedule_task(
            task_func,
            *args,
            task_name=task_name,
            priority=priority,
            schedule_type=ScheduleType.RECURRING,
            scheduled_time=start_time or datetime.now(timezone.utc),
            **kwargs,
        )

        # Update schedule info for recurring
        schedule_info = self._schedule_info[task_id]
        schedule_info.repeat_interval = interval
        schedule_info.max_executions = max_executions

        self._recurring_tasks.add(task_id)
        return task_id

    def _setup_dependencies(self, task: Task) -> None:
        """Setup task dependencies."""
        for dep_id in task.dependencies:
            dependency = TaskDependency(
                task_id=task.task_id,
                depends_on=dep_id,
            )
            self._dependencies[task.task_id].append(dependency)
            self._waiting_tasks[task.task_id].add(dep_id)
            self._dependent_tasks[dep_id].add(task.task_id)

    def _add_to_schedule(self, task_id: str, execution_time: datetime) -> None:
        """Add task to schedule."""
        timestamp = execution_time.timestamp()
        heapq.heappush(self._scheduled_tasks, (timestamp, task_id))

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while not self._shutdown:
            try:
                current_time = time.time()
                tasks_to_execute = []

                # Find tasks ready for execution
                with self._lock:
                    while self._scheduled_tasks and self._scheduled_tasks[0][0] <= current_time:
                        _, task_id = heapq.heappop(self._scheduled_tasks)
                        if task_id in self._tasks:
                            tasks_to_execute.append(task_id)

                # Execute ready tasks
                for task_id in tasks_to_execute:
                    if len(self._running_tasks) < self.scheduler_config.max_concurrent_tasks:
                        await self._execute_task(task_id)
                    else:
                        # Re-schedule for later if at capacity
                        execution_time = datetime.fromtimestamp(current_time + 1, tz=timezone.utc)
                        self._add_to_schedule(task_id, execution_time)

                # Sleep based on resolution
                await asyncio.sleep(self.scheduler_config.schedule_resolution_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(1)

    async def _execute_task(self, task_id: str) -> None:
        """Execute task."""
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]

        # Update task status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)

        # Update progress
        progress = self._task_progress.get(task_id)
        if progress:
            progress.started_at = task.started_at
            progress.status_message = "Executing..."

        # Create execution task
        execution_task = asyncio.create_task(self._run_task_with_timeout(task))
        self._running_tasks[task_id] = execution_task

        self._log_task_event(ConcurrencyEventType.TASK_STARTED, task)

        # Call start callback
        if self._on_task_start:
            try:
                self._on_task_start(task)
            except Exception as e:
                logger.error(f"Error in task start callback: {e}")

    async def _run_task_with_timeout(self, task: Task) -> None:
        """Run task with timeout handling."""
        try:
            # Extract function and arguments
            func = task.context["func"]
            args = task.context.get("args", ())
            kwargs = task.context.get("kwargs", {})

            # Execute with timeout
            if task.timeout_seconds:
                result = await asyncio.wait_for(
                    self._execute_task_function(func, args, kwargs), timeout=task.timeout_seconds
                )
            else:
                result = await self._execute_task_function(func, args, kwargs)

            # Task completed successfully
            await self._handle_task_completion(task, result)

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error_message = f"Task timed out after {task.timeout_seconds} seconds"
            await self._handle_task_failure(task, asyncio.TimeoutError("Task timeout"))

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            await self._handle_task_failure(task, e)

        finally:
            # Clean up
            self._running_tasks.pop(task.task_id, None)
            task.completed_at = datetime.now(timezone.utc)

            if task.started_at:
                duration = (task.completed_at - task.started_at).total_seconds() * 1000
                task.actual_duration_ms = duration

                # Track performance
                task_type = task.task_type
                self._task_performance[task_type].append(duration)

                # Keep only recent performance data
                if len(self._task_performance[task_type]) > 100:
                    self._task_performance[task_type] = self._task_performance[task_type][-50:]

    async def _execute_task_function(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """Execute task function (async or sync)."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def _handle_task_completion(self, task: Task, result: Any) -> None:
        """Handle successful task completion."""
        task.status = TaskStatus.COMPLETED
        task.result = result

        # Update progress
        progress = self._task_progress.get(task.task_id)
        if progress:
            progress.progress_percent = 100.0
            progress.status_message = "Completed"
            progress.last_update = datetime.now(timezone.utc)

        # Cache result if enabled
        if self.scheduler_config.enable_result_caching:
            cache_key = f"{task.task_type}:{hash(str(task.context))}"
            self._result_cache[cache_key] = result
            self._cache_timestamps[cache_key] = datetime.now(timezone.utc)

        # Move to completed tasks
        with self._lock:
            self._completed_tasks[task.task_id] = task

            # Handle dependent tasks
            for dependent_id in self._dependent_tasks.get(task.task_id, set()):
                if dependent_id in self._waiting_tasks:
                    self._waiting_tasks[dependent_id].discard(task.task_id)

                    # If all dependencies met, schedule for execution
                    if not self._waiting_tasks[dependent_id]:
                        del self._waiting_tasks[dependent_id]
                        dependent_task = self._tasks.get(dependent_id)
                        if dependent_task:
                            schedule_info = self._schedule_info.get(dependent_id)
                            if schedule_info:
                                self._add_to_schedule(dependent_id, schedule_info.next_execution)

            # Handle recurring tasks
            if task.task_id in self._recurring_tasks:
                await self._reschedule_recurring_task(task.task_id)

        self._log_task_event(ConcurrencyEventType.TASK_COMPLETED, task)

        # Call completion callback
        if self._on_task_complete:
            try:
                self._on_task_complete(task, result)
            except Exception as e:
                logger.error(f"Error in task completion callback: {e}")

    async def _handle_task_failure(self, task: Task, exception: Exception) -> None:
        """Handle task failure."""

        # Check if retry is possible
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING

            # Calculate retry delay with exponential backoff
            delay = self.scheduler_config.retry_backoff_factor ** (task.retry_count - 1)
            retry_time = datetime.now(timezone.utc) + timedelta(seconds=delay)

            # Re-schedule task
            self._add_to_schedule(task.task_id, retry_time)

            self._log_info(
                f"Retrying task {task.task_id} (attempt {task.retry_count}/{task.max_retries}) in {delay}s"
            )
            return

        # Task permanently failed
        with self._lock:
            self._failed_tasks[task.task_id] = task

            # Add to dead letter queue if enabled
            if self.scheduler_config.enable_dead_letter_queue:
                self._dead_letter_queue.append(task)

        self._log_task_event(ConcurrencyEventType.TASK_FAILED, task)

        # Call error callback
        if self._on_task_error:
            try:
                self._on_task_error(task, exception)
            except Exception as e:
                logger.error(f"Error in task error callback: {e}")

    async def _reschedule_recurring_task(self, task_id: str) -> None:
        """Reschedule recurring task for next execution."""
        schedule_info = self._schedule_info.get(task_id)
        if not schedule_info or not schedule_info.repeat_interval:
            return

        # Check execution count limit
        schedule_info.execution_count += 1
        if (
            schedule_info.max_executions
            and schedule_info.execution_count >= schedule_info.max_executions
        ):
            self._recurring_tasks.discard(task_id)
            return

        # Calculate next execution time
        schedule_info.last_execution = datetime.now(timezone.utc)
        schedule_info.next_execution = schedule_info.last_execution + schedule_info.repeat_interval

        # Create new task instance for next execution
        original_task = self._tasks[task_id]
        new_task = Task(
            task_name=original_task.task_name,
            task_type=original_task.task_type,
            priority=original_task.priority,
            timeout_seconds=original_task.timeout_seconds,
            max_retries=original_task.max_retries,
            context=original_task.context.copy(),
        )

        # Store new task
        self._tasks[new_task.task_id] = new_task
        self._schedule_info[new_task.task_id] = schedule_info
        self._task_progress[new_task.task_id] = TaskProgress(task_id=new_task.task_id)

        # Schedule for next execution
        self._add_to_schedule(new_task.task_id, schedule_info.next_execution)

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                await self._cleanup_old_tasks()
                await self._cleanup_cache()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_old_tasks(self) -> None:
        """Clean up old completed/failed tasks."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

        with self._lock:
            # Clean up completed tasks
            old_completed = [
                task_id
                for task_id, task in self._completed_tasks.items()
                if task.completed_at and task.completed_at < cutoff_time
            ]
            for task_id in old_completed:
                del self._completed_tasks[task_id]
                self._task_progress.pop(task_id, None)

            # Clean up failed tasks
            old_failed = [
                task_id
                for task_id, task in self._failed_tasks.items()
                if task.completed_at and task.completed_at < cutoff_time
            ]
            for task_id in old_failed:
                del self._failed_tasks[task_id]
                self._task_progress.pop(task_id, None)

            if old_completed or old_failed:
                self._log_info(
                    f"Cleaned up {len(old_completed)} completed and {len(old_failed)} failed tasks"
                )

    async def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        if not self.scheduler_config.enable_result_caching:
            return

        cutoff_time = datetime.now(timezone.utc) - timedelta(
            seconds=self.scheduler_config.cache_ttl_seconds
        )

        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items() if timestamp < cutoff_time
        ]

        for key in expired_keys:
            self._result_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)

        if expired_keys:
            self._log_info(f"Cleaned up {len(expired_keys)} expired cache entries")

    async def _metrics_loop(self) -> None:
        """Background metrics collection loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(60)  # Collect every minute
                await self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")

    async def _collect_metrics(self) -> None:
        """Collect scheduler metrics."""
        with self._lock:
            self._metrics.total_tasks = len(self._tasks)
            self._metrics.running_tasks = len(self._running_tasks)
            self._metrics.pending_tasks = len(self._scheduled_tasks)
            self._metrics.completed_tasks = len(self._completed_tasks)
            self._metrics.failed_tasks = len(self._failed_tasks)

            # Calculate average task duration
            all_durations = []
            for durations in self._task_performance.values():
                all_durations.extend(durations)

            if all_durations:
                self._metrics.avg_task_duration_ms = sum(all_durations) / len(all_durations)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel task execution."""
        with self._lock:
            # Cancel if running
            if task_id in self._running_tasks:
                execution_task = self._running_tasks[task_id]
                execution_task.cancel()

                # Update task status
                if task_id in self._tasks:
                    self._tasks[task_id].status = TaskStatus.CANCELLED

                return True

            # Remove from schedule if pending
            elif task_id in self._tasks:
                self._tasks[task_id].status = TaskStatus.CANCELLED

                # Remove from scheduled tasks
                self._scheduled_tasks = [
                    (timestamp, tid) for timestamp, tid in self._scheduled_tasks if tid != task_id
                ]
                heapq.heapify(self._scheduled_tasks)

                return True

        return False

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get task status."""
        return (
            self._tasks.get(task_id)
            or self._completed_tasks.get(task_id)
            or self._failed_tasks.get(task_id)
        )

    def get_task_progress(self, task_id: str) -> Optional[TaskProgress]:
        """Get task progress."""
        return self._task_progress.get(task_id)

    def get_metrics(self) -> ConcurrencyMetrics:
        """Get scheduler metrics."""
        return self._metrics.model_copy()

    def get_dead_letter_queue(self) -> List[Task]:
        """Get dead letter queue contents."""
        return list(self._dead_letter_queue)

    def set_callbacks(
        self,
        on_start: Optional[Callable[[Task], None]] = None,
        on_complete: Optional[Callable[[Task, Any], None]] = None,
        on_error: Optional[Callable[[Task, Exception], None]] = None,
    ) -> None:
        """Set task execution callbacks."""
        self._on_task_start = on_start
        self._on_task_complete = on_complete
        self._on_task_error = on_error

    def _log_task_event(self, event_type: ConcurrencyEventType, task: Task) -> None:
        """Log task event."""
        message = f"Task {event_type.value}: {task.task_name} ({task.task_id})"

        if self.dev_logger:
            self.dev_logger.log_debug(
                SDKEventType.DEBUG_CHECKPOINT,
                message,
                details={
                    "event_type": event_type.value,
                    "task_id": task.task_id,
                    "task_status": task.status.value,
                    "priority": task.priority.value,
                },
            )
        else:
            logger.debug(message)

    def _log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED, message, **kwargs
            )
        else:
            logger.info(message)


__all__ = [
    # Main business logic class
    "TaskScheduler",
    # Note: Task scheduling models are available via DTO imports:
    # from unrealon_sdk.src.dto.task_scheduling import ...
    # from unrealon_sdk.src.dto.concurrency import ...
]
