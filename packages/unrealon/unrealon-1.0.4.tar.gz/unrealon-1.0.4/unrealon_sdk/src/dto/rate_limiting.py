"""
Rate Limiting DTOs - Data Transfer Objects for request throttling system.

This module contains all Pydantic models and enums related to rate limiting,
separated from business logic for clean architecture and reusability.

Components:
- Rate limiting strategies and configuration models
- Throttling metrics and statistics models
- Backoff algorithms and retry policies
- Performance and analytics data structures
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""

    TOKEN_BUCKET = "token_bucket"  # Token bucket algorithm
    LEAKY_BUCKET = "leaky_bucket"  # Leaky bucket algorithm
    SLIDING_WINDOW = "sliding_window"  # Sliding window counter
    FIXED_WINDOW = "fixed_window"  # Fixed window counter
    ADAPTIVE = "adaptive"  # Adaptive rate limiting based on load


class BackoffStrategy(str, Enum):
    """Backoff strategies for rate limiting."""

    LINEAR = "linear"  # Linear backoff
    EXPONENTIAL = "exponential"  # Exponential backoff
    FIBONACCI = "fibonacci"  # Fibonacci sequence backoff
    JITTERED = "jittered"  # Jittered exponential backoff
    CUSTOM = "custom"  # Custom backoff function


class RateLimitScope(str, Enum):
    """Rate limit scope levels."""

    GLOBAL = "global"  # Global rate limit across all operations
    USER = "user"  # Per-user rate limiting
    API_KEY = "api_key"  # Per-API key rate limiting
    ENDPOINT = "endpoint"  # Per-endpoint rate limiting
    OPERATION = "operation"  # Per-operation type rate limiting


class RateLimitStatus(str, Enum):
    """Rate limit operation status."""

    ALLOWED = "allowed"  # Request allowed
    THROTTLED = "throttled"  # Request throttled but queued
    REJECTED = "rejected"  # Request rejected due to rate limit
    RETRYING = "retrying"  # Request being retried with backoff


class RateLimitEventType(str, Enum):
    """Rate limit event types for monitoring."""

    REQUEST_ALLOWED = "request_allowed"
    REQUEST_THROTTLED = "request_throttled" 
    REQUEST_REJECTED = "request_rejected"
    LIMIT_EXCEEDED = "limit_exceeded"
    QUOTA_RESET = "quota_reset"
    BACKOFF_APPLIED = "backoff_applied"
    ADAPTIVE_ADJUSTMENT = "adaptive_adjustment"


class RateLimitConfig(BaseModel):
    """Rate limiting configuration model."""

    model_config = ConfigDict(extra="forbid")

    # Basic limits
    requests_per_second: float = Field(default=10.0, description="Requests per second limit")
    requests_per_minute: int = Field(default=600, description="Requests per minute limit")
    requests_per_hour: int = Field(default=36000, description="Requests per hour limit")
    requests_per_day: int = Field(default=864000, description="Requests per day limit")

    # Strategy configuration
    strategy: RateLimitStrategy = Field(
        default=RateLimitStrategy.TOKEN_BUCKET, description="Rate limiting strategy"
    )
    scope: RateLimitScope = Field(default=RateLimitScope.GLOBAL, description="Rate limit scope")

    # Token bucket specific
    bucket_capacity: int = Field(default=100, description="Token bucket capacity")
    refill_rate: float = Field(default=10.0, description="Token refill rate per second")

    # Sliding window specific
    window_size_seconds: int = Field(default=60, description="Sliding window size in seconds")
    window_segments: int = Field(default=10, description="Number of window segments")

    # Backoff configuration
    backoff_strategy: BackoffStrategy = Field(
        default=BackoffStrategy.EXPONENTIAL, description="Backoff strategy"
    )
    base_delay_seconds: float = Field(default=1.0, description="Base delay for backoff")
    max_delay_seconds: float = Field(default=300.0, description="Maximum delay for backoff")
    backoff_multiplier: float = Field(default=2.0, description="Backoff multiplier")
    jitter_enabled: bool = Field(default=True, description="Enable jitter in backoff")

    # Adaptive configuration
    adaptive_enabled: bool = Field(default=False, description="Enable adaptive rate limiting")
    load_threshold: float = Field(default=0.8, description="Load threshold for adaptation")
    adaptation_factor: float = Field(default=0.5, description="Rate adaptation factor")

    # Queue configuration
    queue_enabled: bool = Field(default=True, description="Enable request queuing")
    max_queue_size: int = Field(default=1000, description="Maximum queue size")
    queue_timeout_seconds: float = Field(default=30.0, description="Queue timeout")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable rate limit metrics")
    metrics_window_seconds: int = Field(default=300, description="Metrics collection window")


class RateLimitQuota(BaseModel):
    """Rate limit quota tracking model."""

    model_config = ConfigDict(extra="forbid")

    # Identification
    scope_id: str = Field(..., description="Scope identifier (user_id, api_key, etc.)")
    scope_type: RateLimitScope = Field(..., description="Scope type")

    # Current state
    current_requests: int = Field(default=0, description="Current request count")
    remaining_requests: int = Field(default=0, description="Remaining requests")
    reset_time: datetime = Field(..., description="When quota resets")

    # Limits
    requests_limit: int = Field(..., description="Request limit for this quota")
    window_start: datetime = Field(..., description="Window start time")
    window_end: datetime = Field(..., description="Window end time")

    # Token bucket state (if applicable)
    tokens_available: float = Field(default=0.0, description="Available tokens")
    last_refill: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Last token refill time"
    )

    # Statistics
    total_requests: int = Field(default=0, description="Total requests made")
    throttled_requests: int = Field(default=0, description="Throttled requests")
    rejected_requests: int = Field(default=0, description="Rejected requests")

    def is_expired(self) -> bool:
        """Check if quota window has expired."""
        return datetime.now(timezone.utc) > self.reset_time

    def time_until_reset(self) -> timedelta:
        """Get time until quota resets."""
        now = datetime.now(timezone.utc)
        if now >= self.reset_time:
            return timedelta(0)
        return self.reset_time - now


class RateLimitRequest(BaseModel):
    """Rate limit request tracking model."""

    model_config = ConfigDict(extra="forbid")

    # Request identification
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scope_id: str = Field(..., description="Scope identifier")
    scope_type: RateLimitScope = Field(..., description="Scope type")
    operation_type: str = Field(..., description="Type of operation")

    # Timing
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: Optional[float] = Field(default=None, description="Processing time")

    # Rate limit result
    status: RateLimitStatus = Field(..., description="Rate limit decision")
    retry_after_seconds: Optional[float] = Field(default=None, description="Retry after delay")
    queue_position: Optional[int] = Field(default=None, description="Position in queue")

    # Context
    quota_remaining: int = Field(default=0, description="Remaining quota")
    quota_reset_time: datetime = Field(..., description="Quota reset time")
    backoff_count: int = Field(default=0, description="Number of backoff attempts")

    # Metadata
    user_agent: Optional[str] = Field(default=None, description="User agent")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    additional_headers: Dict[str, str] = Field(
        default_factory=dict, description="Additional request headers"
    )


class RateLimitStatistics(BaseModel):
    """Rate limiting statistics model."""

    model_config = ConfigDict(extra="forbid")

    # Basic counters
    total_requests: int = Field(default=0, description="Total requests processed")
    allowed_requests: int = Field(default=0, description="Allowed requests")
    throttled_requests: int = Field(default=0, description="Throttled requests")
    rejected_requests: int = Field(default=0, description="Rejected requests")

    # Performance metrics
    avg_processing_time_ms: float = Field(default=0.0, description="Average processing time")
    throttle_rate_percent: float = Field(default=0.0, description="Throttle rate percentage")
    rejection_rate_percent: float = Field(default=0.0, description="Rejection rate percentage")

    # Queue metrics
    avg_queue_size: float = Field(default=0.0, description="Average queue size")
    avg_queue_wait_time_ms: float = Field(default=0.0, description="Average queue wait time")
    queue_timeouts: int = Field(default=0, description="Queue timeout count")

    # Backoff metrics
    total_backoffs: int = Field(default=0, description="Total backoff attempts")
    avg_backoff_delay_ms: float = Field(default=0.0, description="Average backoff delay")
    max_backoff_delay_ms: float = Field(default=0.0, description="Maximum backoff delay")

    # Adaptive metrics (if enabled)
    rate_adjustments: int = Field(default=0, description="Number of rate adjustments")
    current_rate_multiplier: float = Field(default=1.0, description="Current rate multiplier")
    system_load_percent: float = Field(default=0.0, description="Current system load")

    # Time window
    window_start: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Statistics window start"
    )
    window_end: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Statistics window end"
    )
    last_reset: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Last statistics reset"
    )


class BackoffState(BaseModel):
    """Backoff state tracking model."""

    model_config = ConfigDict(extra="forbid")

    # Identification
    scope_id: str = Field(..., description="Scope identifier")
    operation_type: str = Field(..., description="Operation type")

    # Backoff state
    attempt_count: int = Field(default=0, description="Current attempt count")
    current_delay_seconds: float = Field(default=0.0, description="Current delay")
    next_retry_time: datetime = Field(..., description="Next retry time")

    # Configuration
    strategy: BackoffStrategy = Field(..., description="Backoff strategy")
    base_delay: float = Field(..., description="Base delay")
    max_delay: float = Field(..., description="Maximum delay")
    multiplier: float = Field(default=2.0, description="Backoff multiplier")

    # History
    retry_history: List[datetime] = Field(
        default_factory=list, description="Retry attempt timestamps"
    )
    success_time: Optional[datetime] = Field(default=None, description="Last success time")

    def can_retry(self) -> bool:
        """Check if retry is allowed now."""
        return datetime.now(timezone.utc) >= self.next_retry_time

    def time_until_retry(self) -> timedelta:
        """Get time until next retry is allowed."""
        now = datetime.now(timezone.utc)
        if now >= self.next_retry_time:
            return timedelta(0)
        return self.next_retry_time - now


__all__ = [
    # Enums
    "RateLimitStrategy",
    "BackoffStrategy",
    "RateLimitScope",
    "RateLimitStatus",
    "RateLimitEventType",

    # Configuration models
    "RateLimitConfig",

    # Data models
    "RateLimitQuota",
    "RateLimitRequest",
    "RateLimitStatistics",
    "BackoffState",
]
