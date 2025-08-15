"""
Cache Management DTOs - Data Transfer Objects for caching system.

This module contains all Pydantic models and enums related to cache management,
separated from business logic for clean architecture and reusability.

Components:
- Cache policies and configuration models
- Cache entry and statistics models  
- Cache event types and storage levels
- Performance and analytics data structures
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class CachePolicy(str, Enum):
    """Cache eviction policies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL_ONLY = "ttl_only"  # Only TTL-based expiration
    SIZE_ONLY = "size_only"  # Only size-based eviction


class CacheLevel(str, Enum):
    """Cache storage levels."""

    MEMORY = "memory"  # In-memory cache (fastest)
    PERSISTENT = "persistent"  # Disk-based cache (slower but persistent)
    DISTRIBUTED = "distributed"  # Network-distributed cache


class CacheEventType(str, Enum):
    """Cache-specific event types."""

    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    CACHE_SET = "cache_set"
    CACHE_DELETE = "cache_delete"
    CACHE_EXPIRE = "cache_expire"
    CACHE_EVICT = "cache_evict"
    CACHE_CLEAR = "cache_clear"
    CACHE_WARM = "cache_warm"


@dataclass
class CacheEntry(Generic[T]):
    """Individual cache entry with metadata."""

    key: str
    value: T
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[float] = None
    compressed: bool = False
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False

        age = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return age > self.ttl_seconds

    def touch(self) -> None:
        """Update access time and count."""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1


class CacheStatistics(BaseModel):
    """Cache performance statistics."""

    model_config = ConfigDict(extra="forbid")

    # Basic stats
    total_requests: int = Field(default=0, description="Total cache requests")
    cache_hits: int = Field(default=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, description="Number of cache misses")

    # Performance metrics
    hit_rate_percent: float = Field(default=0.0, description="Cache hit rate percentage")
    avg_access_time_ms: float = Field(default=0.0, description="Average access time")

    # Storage stats
    current_size: int = Field(default=0, description="Current number of entries")
    max_size: int = Field(default=0, description="Maximum cache size")
    memory_usage_bytes: int = Field(default=0, description="Memory usage in bytes")

    # Lifecycle stats
    total_sets: int = Field(default=0, description="Total cache sets")
    total_deletes: int = Field(default=0, description="Total cache deletes")
    total_evictions: int = Field(default=0, description="Total evictions")
    total_expirations: int = Field(default=0, description="Total expirations")

    # Time-based metrics
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CacheConfig(BaseModel):
    """Cache configuration model."""

    model_config = ConfigDict(extra="forbid")

    # Size limits
    max_entries: int = Field(default=10000, description="Maximum number of cache entries")
    max_memory_mb: int = Field(default=100, description="Maximum memory usage in MB")

    # TTL settings
    default_ttl_seconds: float = Field(default=3600.0, description="Default TTL in seconds")
    max_ttl_seconds: float = Field(default=86400.0, description="Maximum TTL in seconds")

    # Eviction policy
    eviction_policy: CachePolicy = Field(
        default=CachePolicy.LRU, description="Cache eviction policy"
    )
    eviction_threshold: float = Field(default=0.8, description="Threshold for eviction (0.0-1.0)")

    # Cleanup settings
    cleanup_interval_seconds: float = Field(default=300.0, description="Cleanup interval")
    compression_enabled: bool = Field(
        default=True, description="Enable compression for large objects"
    )
    compression_threshold_bytes: int = Field(
        default=1024, description="Size threshold for compression"
    )

    # Performance settings
    enable_statistics: bool = Field(default=True, description="Enable cache statistics")
    warm_cache_on_startup: bool = Field(default=False, description="Warm cache on startup")


class CacheOperation(BaseModel):
    """Cache operation tracking model."""

    model_config = ConfigDict(extra="forbid")

    operation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: CacheEventType = Field(..., description="Type of cache operation")
    cache_key: str = Field(..., description="Cache key involved")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: Optional[float] = Field(
        default=None, description="Operation duration in milliseconds"
    )
    success: bool = Field(default=True, description="Whether operation was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional operation details"
    )


class CacheMetrics(BaseModel):
    """Real-time cache metrics model."""

    model_config = ConfigDict(extra="forbid")

    # Performance metrics
    avg_get_time_ms: float = Field(default=0.0, description="Average GET operation time")
    avg_set_time_ms: float = Field(default=0.0, description="Average SET operation time")
    peak_memory_usage_bytes: int = Field(default=0, description="Peak memory usage")

    # Efficiency metrics
    hit_rate_last_hour: float = Field(default=0.0, description="Hit rate in last hour")
    eviction_rate_per_hour: float = Field(default=0.0, description="Evictions per hour")
    compression_ratio: float = Field(default=1.0, description="Average compression ratio")

    # Capacity metrics
    memory_utilization_percent: float = Field(
        default=0.0, description="Memory utilization percentage"
    )
    entry_utilization_percent: float = Field(
        default=0.0, description="Entry count utilization percentage"
    )

    # Recent activity (last 5 minutes)
    recent_operations: int = Field(default=0, description="Operations in last 5 minutes")
    recent_hits: int = Field(default=0, description="Cache hits in last 5 minutes")
    recent_misses: int = Field(default=0, description="Cache misses in last 5 minutes")

    # Timestamp
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    # Enums
    "CachePolicy",
    "CacheLevel",
    "CacheEventType",
    # Data models
    "CacheEntry",
    "CacheStatistics",
    "CacheConfig",
    "CacheOperation",
    "CacheMetrics",
]
