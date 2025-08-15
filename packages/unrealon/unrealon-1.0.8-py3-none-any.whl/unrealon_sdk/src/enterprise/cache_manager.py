"""
Cache Manager - Layer 3 Infrastructure Service

Intelligent caching system with TTL (Time To Live), size management,
and automatic eviction policies. Provides high-performance caching
for UnrealOn SDK components with comprehensive cache analytics.

Features:
- TTL-based cache expiration with automatic cleanup
- Size-based eviction using LRU (Least Recently Used) policy
- Multi-level cache hierarchy (memory, persistent)
- Cache hit/miss statistics and performance metrics
- Automatic cache warming and preloading
- Cache invalidation patterns and dependencies
- Compression support for large cached objects
- Thread-safe operations for concurrent access
"""

import asyncio
import logging
import time
import threading
import hashlib
import pickle
import gzip
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Generic
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import OrderedDict
import weakref

# Pydantic v2 for all data models
from pydantic import BaseModel, Field, ConfigDict

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity
from unrealon_sdk.src.dto.cache import (
    CachePolicy,
    CacheLevel,
    CacheEventType,
    CacheEntry,
    CacheStatistics,
    CacheConfig,
    CacheOperation,
    CacheMetrics,
)

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)

T = TypeVar("T")


# All cache models are now imported from DTO layer


class CacheManager:
    """
    Enterprise-grade intelligent cache manager.

    Provides high-performance caching with TTL, size management,
    and comprehensive analytics for UnrealOn SDK components.
    """

    def __init__(
        self,
        config: AdapterConfig,
        cache_config: Optional[CacheConfig] = None,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize cache manager."""
        self.config = config
        self.cache_config = cache_config or CacheConfig()
        self.dev_logger = dev_logger

        # Cache storage
        self._cache: OrderedDict[str, CacheEntry[Any]] = OrderedDict()
        self._lock = threading.RLock()

        # Statistics
        self.statistics = CacheStatistics(max_size=self.cache_config.max_entries)

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._shutdown = False

        # Performance tracking
        self._access_times: List[float] = []

        # Cache warming callbacks
        self._warm_callbacks: List[Callable[[], None]] = []

        self._log_info("Cache manager initialized")

    async def start(self) -> None:
        """Start cache manager background tasks."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        # Warm cache if enabled
        if self.cache_config.warm_cache_on_startup:
            await self._warm_cache()

        self._log_info("Cache manager started")

    async def stop(self) -> None:
        """Stop cache manager and cleanup."""
        self._shutdown = True

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self._log_info("Cache manager stopped")

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get value from cache."""
        start_time = time.time()

        with self._lock:
            self.statistics.total_requests += 1

            if key in self._cache:
                entry = self._cache[key]

                # Check if expired
                if entry.is_expired():
                    self._remove_entry(key, CacheEventType.CACHE_EXPIRE)
                    self.statistics.cache_misses += 1
                    self._log_cache_event(CacheEventType.CACHE_MISS, key, "expired")
                    return default

                # Update access info
                entry.touch()

                # Move to end for LRU
                if self.cache_config.eviction_policy == CachePolicy.LRU:
                    self._cache.move_to_end(key)

                self.statistics.cache_hits += 1
                self._log_cache_event(CacheEventType.CACHE_HIT, key)

                # Track access time
                access_time = (time.time() - start_time) * 1000
                self._track_access_time(access_time)

                return entry.value
            else:
                self.statistics.cache_misses += 1
                self._log_cache_event(CacheEventType.CACHE_MISS, key, "not found")
                return default

    def set(
        self,
        key: str,
        value: T,
        ttl_seconds: Optional[float] = None,
        compress: bool = False,
    ) -> bool:
        """Set value in cache."""
        try:
            # Use default TTL if not specified
            if ttl_seconds is None:
                ttl_seconds = self.cache_config.default_ttl_seconds

            # Clamp TTL to maximum
            if ttl_seconds > self.cache_config.max_ttl_seconds:
                ttl_seconds = self.cache_config.max_ttl_seconds

            # Calculate size
            size_bytes = self._calculate_size(value)

            # Compress if needed
            if compress or (
                self.cache_config.compression_enabled
                and size_bytes > self.cache_config.compression_threshold_bytes
            ):
                value = self._compress_value(value)
                compress = True

            with self._lock:
                # Check if we need to evict entries (sync version for set method)
                self._ensure_capacity_sync()

                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.now(timezone.utc),
                    last_accessed=datetime.now(timezone.utc),
                    ttl_seconds=ttl_seconds,
                    compressed=compress,
                    size_bytes=size_bytes,
                )

                # Add to cache
                if key in self._cache:
                    # Update existing entry
                    old_entry = self._cache[key]
                    self.statistics.memory_usage_bytes -= old_entry.size_bytes

                self._cache[key] = entry
                self.statistics.current_size = len(self._cache)
                self.statistics.memory_usage_bytes += size_bytes
                self.statistics.total_sets += 1

                self._log_cache_event(CacheEventType.CACHE_SET, key)
                return True

        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key, CacheEventType.CACHE_DELETE)
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self.statistics.current_size = 0
            self.statistics.memory_usage_bytes = 0

            self._log_cache_event(CacheEventType.CACHE_CLEAR, f"cleared {count} entries")

    def exists(self, key: str) -> bool:
        """Check if key exists in cache (without accessing it)."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                return not entry.is_expired()
            return False

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all cache keys, optionally filtered by pattern."""
        with self._lock:
            keys = list(self._cache.keys())

            if pattern:
                import fnmatch

                keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]

            return keys

    def get_statistics(self) -> CacheStatistics:
        """Get cache statistics."""
        with self._lock:
            # Update calculated stats
            total_requests = self.statistics.cache_hits + self.statistics.cache_misses
            if total_requests > 0:
                self.statistics.hit_rate_percent = (
                    self.statistics.cache_hits / total_requests
                ) * 100

            if self._access_times:
                self.statistics.avg_access_time_ms = sum(self._access_times) / len(
                    self._access_times
                )

            return self.statistics.model_copy()

    def reset_statistics(self) -> None:
        """Reset cache statistics."""
        with self._lock:
            self.statistics = CacheStatistics(
                max_size=self.cache_config.max_entries,
                current_size=len(self._cache),
                memory_usage_bytes=self.statistics.memory_usage_bytes,
            )
            self._access_times.clear()

            self._log_info("Cache statistics reset")

    def _ensure_capacity_sync(self) -> None:
        """Ensure cache doesn't exceed capacity limits (synchronous version)."""
        # Check entry count
        max_entries = self.cache_config.max_entries
        if len(self._cache) >= max_entries:
            self._evict_entries_sync(int(max_entries * (1 - self.cache_config.eviction_threshold)))

        # Check memory usage
        max_memory_bytes = self.cache_config.max_memory_mb * 1024 * 1024
        if self.statistics.memory_usage_bytes >= max_memory_bytes:
            self._evict_by_memory_sync()

    async def _ensure_capacity(self) -> None:
        """Ensure cache doesn't exceed capacity limits (async version)."""
        # Check entry count
        max_entries = self.cache_config.max_entries
        if len(self._cache) >= max_entries:
            await self._evict_entries(int(max_entries * (1 - self.cache_config.eviction_threshold)))

        # Check memory usage
        max_memory_bytes = self.cache_config.max_memory_mb * 1024 * 1024
        if self.statistics.memory_usage_bytes >= max_memory_bytes:
            await self._evict_by_memory()

    async def _evict_entries(self, target_count: int) -> None:
        """Evict entries based on eviction policy."""
        if len(self._cache) <= target_count:
            return

        evict_count = len(self._cache) - target_count
        policy = self.cache_config.eviction_policy

        if policy == CachePolicy.LRU:
            # Remove least recently used (from front of OrderedDict)
            for _ in range(evict_count):
                if self._cache:
                    key = next(iter(self._cache))
                    self._remove_entry(key, CacheEventType.CACHE_EVICT)

        elif policy == CachePolicy.LFU:
            # Remove least frequently used
            entries = list(self._cache.items())
            entries.sort(key=lambda x: x[1].access_count)
            for key, _ in entries[:evict_count]:
                self._remove_entry(key, CacheEventType.CACHE_EVICT)

        elif policy == CachePolicy.FIFO:
            # Remove oldest entries
            entries = list(self._cache.items())
            entries.sort(key=lambda x: x[1].created_at)
            for key, _ in entries[:evict_count]:
                self._remove_entry(key, CacheEventType.CACHE_EVICT)

        self._log_info(f"Evicted {evict_count} entries using {policy.value} policy")

    def _evict_entries_sync(self, target_count: int) -> None:
        """Evict entries based on eviction policy (synchronous version)."""
        if len(self._cache) <= target_count:
            return

        evict_count = len(self._cache) - target_count
        policy = self.cache_config.eviction_policy

        if policy == CachePolicy.LRU:
            # Remove least recently used (from front of OrderedDict)
            for _ in range(evict_count):
                if self._cache:
                    key = next(iter(self._cache))
                    self._remove_entry(key, CacheEventType.CACHE_EVICT)

        elif policy == CachePolicy.LFU:
            # Remove least frequently used
            entries = list(self._cache.items())
            entries.sort(key=lambda x: x[1].access_count)
            for key, _ in entries[:evict_count]:
                self._remove_entry(key, CacheEventType.CACHE_EVICT)

        elif policy == CachePolicy.FIFO:
            # Remove oldest entries
            entries = list(self._cache.items())
            entries.sort(key=lambda x: x[1].created_at)
            for key, _ in entries[:evict_count]:
                self._remove_entry(key, CacheEventType.CACHE_EVICT)

        self._log_info(f"Evicted {evict_count} entries using {policy.value} policy (sync)")

    async def _evict_by_memory(self) -> None:
        """Evict entries to reduce memory usage."""
        target_memory = (
            self.cache_config.max_memory_mb * 1024 * 1024 * self.cache_config.eviction_threshold
        )

        # Sort by size (largest first) and remove until under target
        entries = list(self._cache.items())
        entries.sort(key=lambda x: x[1].size_bytes, reverse=True)

        for key, entry in entries:
            if self.statistics.memory_usage_bytes <= target_memory:
                break
            self._remove_entry(key, CacheEventType.CACHE_EVICT)

        self._log_info(
            f"Memory-based eviction completed, usage: {self.statistics.memory_usage_bytes} bytes"
        )

    def _evict_by_memory_sync(self) -> None:
        """Evict entries to reduce memory usage (synchronous version)."""
        target_memory = (
            self.cache_config.max_memory_mb * 1024 * 1024 * self.cache_config.eviction_threshold
        )

        # Sort by size (largest first) and remove until under target
        entries = list(self._cache.items())
        entries.sort(key=lambda x: x[1].size_bytes, reverse=True)

        for key, entry in entries:
            if self.statistics.memory_usage_bytes <= target_memory:
                break
            self._remove_entry(key, CacheEventType.CACHE_EVICT)

        self._log_info(
            f"Memory-based eviction completed (sync), usage: {self.statistics.memory_usage_bytes} bytes"
        )

    def _remove_entry(self, key: str, event_type: CacheEventType) -> None:
        """Remove entry from cache and update statistics."""
        if key in self._cache:
            entry = self._cache[key]
            del self._cache[key]

            self.statistics.current_size = len(self._cache)
            self.statistics.memory_usage_bytes -= entry.size_bytes

            if event_type == CacheEventType.CACHE_EVICT:
                self.statistics.total_evictions += 1
            elif event_type == CacheEventType.CACHE_EXPIRE:
                self.statistics.total_expirations += 1
            elif event_type == CacheEventType.CACHE_DELETE:
                self.statistics.total_deletes += 1

    async def _cleanup_loop(self) -> None:
        """Background task for cleaning up expired entries."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.cache_config.cleanup_interval_seconds)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")

    async def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        expired_keys = []

        with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)

        for key in expired_keys:
            with self._lock:
                self._remove_entry(key, CacheEventType.CACHE_EXPIRE)

        if expired_keys:
            self._log_info(f"Cleaned up {len(expired_keys)} expired cache entries")

    async def _warm_cache(self) -> None:
        """Warm cache using registered callbacks."""
        for callback in self._warm_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in cache warming callback: {e}")

        self._log_cache_event(
            CacheEventType.CACHE_WARM, f"warmed with {len(self._warm_callbacks)} callbacks"
        )

    def add_warm_callback(self, callback: Callable[[], None]) -> None:
        """Add callback for cache warming."""
        self._warm_callbacks.append(callback)

    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes."""
        try:
            return len(pickle.dumps(value))
        except Exception:
            # Fallback estimation
            return len(str(value).encode("utf-8"))

    def _compress_value(self, value: Any) -> bytes:
        """Compress value using gzip."""
        try:
            pickled = pickle.dumps(value)
            return gzip.compress(pickled)
        except Exception as e:
            logger.error(f"Error compressing value: {e}")
            return value

    def _decompress_value(self, compressed_data: bytes) -> Any:
        """Decompress value from gzip."""
        try:
            decompressed = gzip.decompress(compressed_data)
            return pickle.loads(decompressed)
        except Exception as e:
            logger.error(f"Error decompressing value: {e}")
            return compressed_data

    def _track_access_time(self, access_time_ms: float) -> None:
        """Track cache access time for statistics."""
        self._access_times.append(access_time_ms)

        # Keep only recent access times
        if len(self._access_times) > 1000:
            self._access_times = self._access_times[-500:]

    def _log_cache_event(self, event_type: CacheEventType, key: str, details: str = "") -> None:
        """Log cache event."""
        message = f"Cache {event_type.value}: {key}"
        if details:
            message += f" ({details})"

        if self.dev_logger:
            self.dev_logger.log_debug(
                SDKEventType.DEBUG_CHECKPOINT,
                message,
                details={"cache_event": event_type.value, "key": key, "details": details},
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


# Context manager for cache operations
class CacheContext:
    """Context manager for automatic cache operations."""

    def __init__(
        self,
        cache_manager: CacheManager,
        key_generator: Callable[..., str],
        ttl_seconds: Optional[float] = None,
    ):
        self.cache_manager = cache_manager
        self.key_generator = key_generator
        self.ttl_seconds = ttl_seconds

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for automatic caching."""

        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            cache_key = self.key_generator(*args, **kwargs)

            # Try to get from cache
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache_manager.set(cache_key, result, self.ttl_seconds)

            return result

        return wrapper


__all__ = [
    # Main business logic class
    "CacheManager",
    # Utilities
    "CacheContext",
    # Note: Cache models (CacheConfig, CacheEntry, CacheStatistics, etc.)
    # are available via DTO imports: from unrealon_sdk.src.dto.cache import ...
]
