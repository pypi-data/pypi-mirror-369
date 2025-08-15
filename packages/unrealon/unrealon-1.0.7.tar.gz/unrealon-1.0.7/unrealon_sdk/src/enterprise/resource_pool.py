"""
Resource Pool - Layer 4 Concurrency Service

Enterprise-grade resource pooling system with intelligent lifecycle management,
health monitoring, and automatic optimization. Provides efficient resource
utilization with connection pooling, thread management, and memory optimization.

Features:
- Multi-type resource pooling (connections, threads, memory, files)
- Dynamic pool sizing with auto-scaling capabilities
- Health monitoring and automatic resource validation
- Resource lifecycle management with cleanup
- Pool exhaustion handling with queuing and overflow
- Performance optimization with usage analytics
- Leak detection and automatic resource recovery
- Pool warmup and preemptive resource allocation
- Resource tagging and categorization
- Integration with monitoring and alerting systems
"""

import asyncio
import logging
import threading
import time
import weakref
from typing import Dict, List, Optional, Any, Callable, Set, Union, TypeVar, Generic
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
import uuid

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity
from unrealon_sdk.src.dto.concurrency import (
    ResourceType,
    ResourceStatus,
    ConcurrencyEventType,
    ResourcePool as ResourcePoolDTO,
    ConcurrencyMetrics,
)
from unrealon_sdk.src.dto.resource_pooling import (
    ResourceLifecycleState,
    PoolScalingStrategy,
    ResourceMetadata,
    PoolConfig,
)

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ManagedResource(Generic[T]):
    """Wrapper for managed resources with metadata."""

    def __init__(
        self,
        resource: T,
        metadata: ResourceMetadata,
        validator: Optional[Callable[[T], bool]] = None,
        cleanup_func: Optional[Callable[[T], None]] = None,
    ):
        self.resource = resource
        self.metadata = metadata
        self._validator = validator
        self._cleanup_func = cleanup_func
        self._in_use = False
        self._acquired_at: Optional[datetime] = None
        self._acquired_by: Optional[str] = None

    def acquire(self, client_id: str) -> T:
        """Acquire resource for use."""
        if self._in_use:
            raise RuntimeError(f"Resource {self.metadata.resource_id} is already in use")

        self._in_use = True
        self._acquired_at = datetime.now(timezone.utc)
        self._acquired_by = client_id
        self.metadata.last_used = self._acquired_at
        self.metadata.usage_count += 1
        self.metadata.lifecycle_state = ResourceLifecycleState.IN_USE

        return self.resource

    def release(self) -> None:
        """Release resource back to pool."""
        self._in_use = False
        self._acquired_at = None
        self._acquired_by = None
        self.metadata.lifecycle_state = ResourceLifecycleState.IDLE

    def is_valid(self) -> bool:
        """Check if resource is valid."""
        if self._validator:
            try:
                return self._validator(self.resource)
            except Exception as e:
                self.metadata.error_count += 1
                self.metadata.last_error = str(e)
                return False
        return True

    def cleanup(self) -> None:
        """Cleanup resource."""
        if self._cleanup_func:
            try:
                self._cleanup_func(self.resource)
            except Exception as e:
                logger.error(f"Error cleaning up resource {self.metadata.resource_id}: {e}")

        self.metadata.lifecycle_state = ResourceLifecycleState.DESTROYED

    @property
    def is_in_use(self) -> bool:
        """Check if resource is currently in use."""
        return self._in_use

    @property
    def acquired_duration(self) -> Optional[timedelta]:
        """Get how long resource has been acquired."""
        if self._acquired_at:
            return datetime.now(timezone.utc) - self._acquired_at
        return None


class ResourcePoolManager:
    """
    Enterprise-grade resource pool manager.

    Manages multiple resource pools with intelligent lifecycle management,
    health monitoring, and performance optimization.
    """

    def __init__(
        self,
        config: AdapterConfig,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize resource pool manager."""
        self.config = config
        self.dev_logger = dev_logger

        # Pool management
        self._pools: Dict[str, "ResourcePoolInstance"] = {}
        self._pool_configs: Dict[str, PoolConfig] = {}

        # Resource factories
        self._resource_factories: Dict[str, Callable[[], Any]] = {}
        self._resource_validators: Dict[str, Callable[[Any], bool]] = {}
        self._resource_cleanup_funcs: Dict[str, Callable[[Any], None]] = {}

        # Global metrics
        self._global_metrics = ConcurrencyMetrics()

        # Background tasks
        self._monitor_task: Optional[asyncio.Task[None]] = None
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._scaling_task: Optional[asyncio.Task[None]] = None
        self._shutdown = False

        # Thread safety
        self._lock = threading.RLock()

        self._log_info("Resource pool manager initialized")

    async def start(self) -> None:
        """Start resource pool manager."""
        # Start background tasks
        if self._monitor_task is None:
            self._monitor_task = asyncio.create_task(self._monitoring_loop())

        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        if self._scaling_task is None:
            self._scaling_task = asyncio.create_task(self._scaling_loop())

        self._log_info("Resource pool manager started")

    async def stop(self) -> None:
        """Stop resource pool manager and cleanup all pools."""
        self._shutdown = True

        # Cancel background tasks
        for task in [self._monitor_task, self._cleanup_task, self._scaling_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Shutdown all pools
        for pool_name, pool in list(self._pools.items()):
            await pool.shutdown()

        self._log_info("Resource pool manager stopped")

    def create_pool(
        self,
        pool_config: PoolConfig,
        resource_factory: Callable[[], T],
        validator: Optional[Callable[[T], bool]] = None,
        cleanup_func: Optional[Callable[[T], None]] = None,
    ) -> None:
        """Create new resource pool."""

        with self._lock:
            if pool_config.pool_name in self._pools:
                raise ValueError(f"Pool '{pool_config.pool_name}' already exists")

            # Store configuration and factories
            self._pool_configs[pool_config.pool_name] = pool_config
            self._resource_factories[pool_config.pool_name] = resource_factory
            if validator:
                self._resource_validators[pool_config.pool_name] = validator
            if cleanup_func:
                self._resource_cleanup_funcs[pool_config.pool_name] = cleanup_func

            # Create pool instance
            pool = ResourcePoolInstance(
                config=pool_config,
                resource_factory=resource_factory,
                validator=validator,
                cleanup_func=cleanup_func,
                dev_logger=self.dev_logger,
            )

            self._pools[pool_config.pool_name] = pool

            # Initialize pool
            asyncio.create_task(pool.initialize())

            self._log_info(
                f"Created resource pool '{pool_config.pool_name}' for {pool_config.resource_type.value}"
            )

    @asynccontextmanager
    async def acquire_resource(
        self,
        pool_name: str,
        timeout_seconds: Optional[float] = None,
        client_id: Optional[str] = None,
    ):
        """Acquire resource from pool with context manager."""

        if pool_name not in self._pools:
            raise ValueError(f"Pool '{pool_name}' does not exist")

        pool = self._pools[pool_name]
        client_id = client_id or generate_correlation_id()

        # Acquire resource
        managed_resource = await pool.acquire_resource(client_id, timeout_seconds)

        try:
            yield managed_resource.resource
        finally:
            # Always return resource to pool
            await pool.return_resource(managed_resource)

    async def get_pool_status(self, pool_name: str) -> Optional[ResourcePoolDTO]:
        """Get pool status information."""
        if pool_name not in self._pools:
            return None

        pool = self._pools[pool_name]
        return await pool.get_status()

    async def get_all_pools_status(self) -> List[ResourcePoolDTO]:
        """Get status for all pools."""
        statuses = []
        for pool in self._pools.values():
            status = await pool.get_status()
            statuses.append(status)
        return statuses

    def get_global_metrics(self) -> ConcurrencyMetrics:
        """Get global resource pool metrics."""
        return self._global_metrics.model_copy()

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                await self._collect_global_metrics()
                await self._check_pool_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in resource pool monitoring: {e}")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_pools()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in resource pool cleanup: {e}")

    async def _scaling_loop(self) -> None:
        """Background scaling loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(45)  # Scale every 45 seconds
                await self._auto_scale_pools()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in resource pool scaling: {e}")

    async def _collect_global_metrics(self) -> None:
        """Collect global metrics from all pools."""
        total_resources = 0
        available_resources = 0

        for pool in self._pools.values():
            status = await pool.get_status()
            total_resources += status.current_size
            available_resources += status.available_resources

        # Update global metrics
        self._global_metrics.total_resources = total_resources
        self._global_metrics.available_resources = available_resources

        if total_resources > 0:
            self._global_metrics.resource_utilization_percent = (
                (total_resources - available_resources) / total_resources * 100
            )

    async def _check_pool_health(self) -> None:
        """Check health of all pools."""
        for pool_name, pool in self._pools.items():
            try:
                await pool.health_check()
            except Exception as e:
                logger.error(f"Health check failed for pool '{pool_name}': {e}")

    async def _cleanup_pools(self) -> None:
        """Cleanup all pools."""
        for pool in self._pools.values():
            await pool.cleanup()

    async def _auto_scale_pools(self) -> None:
        """Auto-scale all pools based on their configurations."""
        for pool in self._pools.values():
            await pool.auto_scale()

    def _log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED, message, **kwargs
            )
        else:
            logger.info(message)


class ResourcePoolInstance(Generic[T]):
    """Individual resource pool instance."""

    def __init__(
        self,
        config: PoolConfig,
        resource_factory: Callable[[], T],
        validator: Optional[Callable[[T], bool]] = None,
        cleanup_func: Optional[Callable[[T], None]] = None,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        self.config = config
        self._resource_factory = resource_factory
        self._validator = validator
        self._cleanup_func = cleanup_func
        self.dev_logger = dev_logger

        # Resource storage
        self._resources: Dict[str, ManagedResource[T]] = {}
        self._available: deque[str] = deque()
        self._in_use: Set[str] = set()

        # Acquisition queue
        self._acquisition_queue: deque[asyncio.Future] = deque()

        # Metrics
        self._metrics = ResourcePoolDTO(
            pool_id=config.pool_name,
            pool_name=config.pool_name,
            resource_type=config.resource_type,
            min_size=config.min_size,
            max_size=config.max_size,
        )

        # Performance tracking
        self._acquisition_times: deque[float] = deque(maxlen=100)
        self._last_scale_time: Optional[datetime] = None

        # Thread safety
        self._lock = asyncio.Lock()

        # Initialization state
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize pool with initial resources."""
        async with self._lock:
            if self._initialized:
                return

            # Create initial resources
            for i in range(self.config.initial_size):
                try:
                    resource_id = await self._create_resource()
                    if resource_id:
                        self._available.append(resource_id)
                except Exception as e:
                    logger.error(f"Failed to create initial resource {i}: {e}")

            # Warmup if enabled
            if self.config.enable_warmup:
                await self._warmup_pool()

            self._initialized = True
            self._update_metrics()

    async def acquire_resource(
        self,
        client_id: str,
        timeout_seconds: Optional[float] = None,
    ) -> ManagedResource[T]:
        """Acquire resource from pool."""

        timeout_seconds = timeout_seconds or self.config.acquisition_timeout_seconds
        start_time = time.time()

        try:
            # Try to get available resource
            async with asyncio.wait_for(self._lock, timeout=timeout_seconds):

                # Check for available resources
                while self._available:
                    resource_id = self._available.popleft()
                    managed_resource = self._resources[resource_id]

                    # Validate resource if configured
                    if self.config.validation_on_acquire and not managed_resource.is_valid():
                        await self._destroy_resource(resource_id)
                        continue

                    # Acquire resource
                    managed_resource.acquire(client_id)
                    self._in_use.add(resource_id)

                    # Track acquisition time
                    acquisition_time = (time.time() - start_time) * 1000
                    self._acquisition_times.append(acquisition_time)

                    self._update_metrics()
                    return managed_resource

                # No available resources, try to create new one
                if len(self._resources) < self.config.max_size:
                    resource_id = await self._create_resource()
                    if resource_id:
                        managed_resource = self._resources[resource_id]
                        managed_resource.acquire(client_id)
                        self._in_use.add(resource_id)

                        acquisition_time = (time.time() - start_time) * 1000
                        self._acquisition_times.append(acquisition_time)

                        self._update_metrics()
                        return managed_resource

                # Pool exhausted, add to queue
                future = asyncio.Future()
                self._acquisition_queue.append(future)

            # Wait for resource to become available
            try:
                managed_resource = await asyncio.wait_for(future, timeout=timeout_seconds)
                managed_resource.acquire(client_id)

                acquisition_time = (time.time() - start_time) * 1000
                self._acquisition_times.append(acquisition_time)

                return managed_resource

            except asyncio.TimeoutError:
                # Remove from queue if still there
                try:
                    self._acquisition_queue.remove(future)
                except ValueError:
                    pass
                raise

        except asyncio.TimeoutError:
            self._metrics.failed_acquisitions += 1
            raise RuntimeError(
                f"Failed to acquire resource from pool '{self.config.pool_name}' within {timeout_seconds}s"
            )

    async def return_resource(self, managed_resource: ManagedResource[T]) -> None:
        """Return resource to pool."""

        async with self._lock:
            resource_id = managed_resource.metadata.resource_id

            if resource_id not in self._resources:
                return  # Resource was already destroyed

            # Validate resource if configured
            if self.config.validation_on_return and not managed_resource.is_valid():
                await self._destroy_resource(resource_id)
                return

            # Release resource
            managed_resource.release()
            self._in_use.discard(resource_id)

            # Check if someone is waiting
            if self._acquisition_queue:
                future = self._acquisition_queue.popleft()
                if not future.cancelled():
                    future.set_result(managed_resource)
                    return

            # Return to available pool
            self._available.append(resource_id)
            self._update_metrics()

    async def _create_resource(self) -> Optional[str]:
        """Create new resource."""
        try:
            # Create resource using factory
            resource = self._resource_factory()
            resource_id = str(uuid.uuid4())

            # Create metadata
            metadata = ResourceMetadata(
                resource_id=resource_id,
                resource_type=self.config.resource_type,
                created_at=datetime.now(timezone.utc),
                last_used=datetime.now(timezone.utc),
                lifecycle_state=ResourceLifecycleState.READY,
            )

            # Create managed resource
            managed_resource = ManagedResource(
                resource=resource,
                metadata=metadata,
                validator=self._validator,
                cleanup_func=self._cleanup_func,
            )

            self._resources[resource_id] = managed_resource
            return resource_id

        except Exception as e:
            logger.error(f"Failed to create resource: {e}")
            return None

    async def _destroy_resource(self, resource_id: str) -> None:
        """Destroy resource and clean up."""
        if resource_id in self._resources:
            managed_resource = self._resources[resource_id]

            # Clean up resource
            try:
                managed_resource.cleanup()
            except Exception as e:
                logger.error(f"Error during resource cleanup: {e}")

            # Remove from all collections
            del self._resources[resource_id]
            self._in_use.discard(resource_id)

            # Remove from available queue if present
            try:
                self._available.remove(resource_id)
            except ValueError:
                pass

    async def _warmup_pool(self) -> None:
        """Warm up pool by pre-creating resources."""
        warmup_count = min(self.config.warmup_size, self.config.max_size - len(self._resources))

        for _ in range(warmup_count):
            resource_id = await self._create_resource()
            if resource_id:
                self._available.append(resource_id)

    async def health_check(self) -> None:
        """Perform health check on pool resources."""
        if not self.config.enable_health_checks:
            return

        unhealthy_resources = []

        async with self._lock:
            for resource_id, managed_resource in self._resources.items():
                if resource_id not in self._in_use:  # Only check idle resources
                    if not managed_resource.is_valid():
                        unhealthy_resources.append(resource_id)

        # Remove unhealthy resources
        for resource_id in unhealthy_resources:
            await self._destroy_resource(resource_id)

        if unhealthy_resources:
            logger.info(
                f"Removed {len(unhealthy_resources)} unhealthy resources from pool '{self.config.pool_name}'"
            )

    async def auto_scale(self) -> None:
        """Auto-scale pool based on configuration."""
        if self.config.scaling_strategy == PoolScalingStrategy.FIXED:
            return

        async with self._lock:
            current_size = len(self._resources)
            available_count = len(self._available)
            in_use_count = len(self._in_use)

            utilization = in_use_count / current_size if current_size > 0 else 0.0

            # Check if scaling is needed
            should_scale_up = (
                utilization > self.config.scale_up_threshold
                and current_size < self.config.max_size
                and available_count == 0
            )

            should_scale_down = (
                utilization < self.config.scale_down_threshold
                and current_size > self.config.min_size
                and available_count > (current_size * 0.5)  # More than 50% are idle
            )

            # Scale up
            if should_scale_up:
                new_size = min(int(current_size * self.config.scale_factor), self.config.max_size)
                resources_to_add = new_size - current_size

                for _ in range(resources_to_add):
                    resource_id = await self._create_resource()
                    if resource_id:
                        self._available.append(resource_id)

                self._last_scale_time = datetime.now(timezone.utc)
                logger.info(
                    f"Scaled up pool '{self.config.pool_name}' from {current_size} to {len(self._resources)}"
                )

            # Scale down
            elif should_scale_down:
                new_size = max(int(current_size / self.config.scale_factor), self.config.min_size)
                resources_to_remove = current_size - new_size

                # Remove only idle resources
                removed_count = 0
                while removed_count < resources_to_remove and self._available:
                    resource_id = self._available.popleft()
                    await self._destroy_resource(resource_id)
                    removed_count += 1

                if removed_count > 0:
                    self._last_scale_time = datetime.now(timezone.utc)
                    logger.info(
                        f"Scaled down pool '{self.config.pool_name}' by {removed_count} resources"
                    )

    async def cleanup(self) -> None:
        """Cleanup idle and expired resources."""
        expired_resources = []

        async with self._lock:
            current_time = datetime.now(timezone.utc)

            for resource_id, managed_resource in self._resources.items():
                if resource_id not in self._in_use:  # Only cleanup idle resources
                    metadata = managed_resource.metadata

                    # Check idle timeout
                    idle_time = (current_time - metadata.last_used).total_seconds()
                    if idle_time > self.config.idle_timeout_seconds:
                        expired_resources.append(resource_id)

                    # Check max lifetime
                    elif (
                        self.config.max_lifetime_seconds
                        and (current_time - metadata.created_at).total_seconds()
                        > self.config.max_lifetime_seconds
                    ):
                        expired_resources.append(resource_id)

        # Remove expired resources
        for resource_id in expired_resources:
            await self._destroy_resource(resource_id)

        if expired_resources:
            logger.info(
                f"Cleaned up {len(expired_resources)} expired resources from pool '{self.config.pool_name}'"
            )

    async def get_status(self) -> ResourcePoolDTO:
        """Get current pool status."""
        self._update_metrics()
        return self._metrics.model_copy()

    async def shutdown(self) -> None:
        """Shutdown pool and cleanup all resources."""
        async with self._lock:
            # Cancel all waiting acquisitions
            while self._acquisition_queue:
                future = self._acquisition_queue.popleft()
                if not future.cancelled():
                    future.cancel()

            # Destroy all resources
            for resource_id in list(self._resources.keys()):
                await self._destroy_resource(resource_id)

            self._available.clear()
            self._in_use.clear()

    def _update_metrics(self) -> None:
        """Update pool metrics."""
        self._metrics.current_size = len(self._resources)
        self._metrics.available_resources = len(self._available)
        self._metrics.in_use_resources = len(self._in_use)
        self._metrics.total_requests += 1

        if self._acquisition_times:
            self._metrics.avg_acquisition_time_ms = sum(self._acquisition_times) / len(
                self._acquisition_times
            )


__all__ = [
    # Main classes
    "ResourcePoolManager",
    "ResourcePoolInstance",
    "ManagedResource",
    # Note: Resource pooling models are available via DTO imports:
    # from unrealon_sdk.src.dto.resource_pooling import ...
    # from unrealon_sdk.src.dto.concurrency import ...
]
