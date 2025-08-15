"""
Rate Limiter - Layer 3 Infrastructure Service

Enterprise-grade request throttling system with intelligent backoff strategies,
adaptive rate limiting, and comprehensive analytics. Provides protection against
API rate limits and ensures optimal request distribution.

Features:
- Multiple rate limiting strategies (Token Bucket, Sliding Window, etc.)
- Intelligent backoff algorithms (Exponential, Fibonacci, Jittered)
- Adaptive rate limiting based on system load
- Request queuing with timeout management
- Per-scope rate limiting (global, user, API key, endpoint)
- Real-time metrics and analytics
- Circuit breaker integration
- Thread-safe operations for concurrent access
"""

import asyncio
import logging
import time
import threading
import random
import math
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
import weakref

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity
from unrealon_sdk.src.dto.rate_limiting import (
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

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Enterprise-grade rate limiter with intelligent throttling and backoff.
    
    Provides comprehensive request throttling with multiple strategies,
    adaptive rate limiting, and detailed analytics for UnrealOn SDK operations.
    """

    def __init__(
        self,
        config: AdapterConfig,
        rate_config: Optional[RateLimitConfig] = None,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize rate limiter."""
        self.config = config
        self.rate_config = rate_config or RateLimitConfig()
        self.dev_logger = dev_logger

        # Thread safety
        self._lock = threading.RLock()

        # Quota tracking per scope
        self._quotas: Dict[str, RateLimitQuota] = {}

        # Backoff state tracking
        self._backoff_states: Dict[str, BackoffState] = {}

        # Request queue
        self._request_queue: deque[RateLimitRequest] = deque()
        self._queue_condition = threading.Condition(self._lock)

        # Statistics
        self.statistics = RateLimitStatistics()

        # Token bucket state (for TOKEN_BUCKET strategy)
        self._token_buckets: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Sliding window state (for SLIDING_WINDOW strategy)
        self._sliding_windows: Dict[str, deque[datetime]] = defaultdict(deque)

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._queue_processor_task: Optional[asyncio.Task[None]] = None
        self._metrics_task: Optional[asyncio.Task[None]] = None
        self._shutdown = False

        # System load tracking for adaptive limiting
        self._system_load = 0.0
        self._load_samples: deque[float] = deque(maxlen=100)

        self._log_info("Rate limiter initialized")

    async def start(self) -> None:
        """Start rate limiter background tasks."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        if self._queue_processor_task is None:
            self._queue_processor_task = asyncio.create_task(self._process_queue_loop())

        if self._metrics_task is None and self.rate_config.enable_metrics:
            self._metrics_task = asyncio.create_task(self._metrics_loop())

        self._log_info("Rate limiter started")

    async def stop(self) -> None:
        """Stop rate limiter and cleanup."""
        self._shutdown = True

        # Cancel background tasks
        for task in [self._cleanup_task, self._queue_processor_task, self._metrics_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Wake up any waiting threads
        with self._queue_condition:
            self._queue_condition.notify_all()

        self._log_info("Rate limiter stopped")

    async def check_rate_limit(
        self,
        scope_id: str,
        operation_type: str,
        scope_type: RateLimitScope = None,
    ) -> RateLimitRequest:
        """
        Check if request is allowed by rate limiter.
        
        Returns RateLimitRequest with decision and metadata.
        """
        if scope_type is None:
            scope_type = self.rate_config.scope

        request_id = generate_correlation_id()
        start_time = time.time()

        try:
            with self._lock:
                # Create request tracking
                request = RateLimitRequest(
                    request_id=request_id,
                    scope_id=scope_id,
                    scope_type=scope_type,
                    operation_type=operation_type,
                    quota_reset_time=datetime.now(timezone.utc) + timedelta(hours=1),  # Default
                )

                # Get or create quota for this scope
                quota_key = f"{scope_type.value}:{scope_id}"
                quota = self._get_or_create_quota(quota_key, scope_id, scope_type)

                # Check backoff state
                backoff_key = f"{scope_id}:{operation_type}"
                if backoff_key in self._backoff_states:
                    backoff_state = self._backoff_states[backoff_key]
                    if not backoff_state.can_retry():
                        request.status = RateLimitStatus.THROTTLED
                        request.retry_after_seconds = backoff_state.time_until_retry().total_seconds()
                        request.backoff_count = backoff_state.attempt_count
                        self._update_statistics_for_request(request)
                        return request

                # Apply rate limiting strategy
                decision = self._apply_rate_limiting_strategy(quota, request)

                # Handle decision
                if decision == RateLimitStatus.ALLOWED:
                    self._handle_allowed_request(quota, request)
                elif decision == RateLimitStatus.THROTTLED:
                    self._handle_throttled_request(quota, request, backoff_key)
                else:  # REJECTED
                    self._handle_rejected_request(quota, request, backoff_key)

                # Update statistics
                self._update_statistics_for_request(request)

                # Track processing time
                processing_time = (time.time() - start_time) * 1000
                request.processing_time_ms = processing_time

                return request

        except Exception as e:
            logger.error(f"Error in rate limit check: {e}")
            # Return permissive decision on error
            return RateLimitRequest(
                request_id=request_id,
                scope_id=scope_id,
                scope_type=scope_type,
                operation_type=operation_type,
                status=RateLimitStatus.ALLOWED,
                quota_reset_time=datetime.now(timezone.utc) + timedelta(hours=1),
            )

    def _get_or_create_quota(
        self, quota_key: str, scope_id: str, scope_type: RateLimitScope
    ) -> RateLimitQuota:
        """Get or create quota for scope."""
        if quota_key in self._quotas:
            quota = self._quotas[quota_key]
            # Reset if expired
            if quota.is_expired():
                quota = self._create_new_quota(scope_id, scope_type)
                self._quotas[quota_key] = quota
        else:
            quota = self._create_new_quota(scope_id, scope_type)
            self._quotas[quota_key] = quota

        return quota

    def _create_new_quota(self, scope_id: str, scope_type: RateLimitScope) -> RateLimitQuota:
        """Create new quota for scope."""
        now = datetime.now(timezone.utc)
        
        # Determine quota limits based on scope type
        if scope_type == RateLimitScope.GLOBAL:
            limit = int(self.rate_config.requests_per_hour)
        elif scope_type == RateLimitScope.USER:
            limit = int(self.rate_config.requests_per_hour * 0.1)  # 10% of global
        elif scope_type == RateLimitScope.API_KEY:
            limit = int(self.rate_config.requests_per_hour * 0.5)  # 50% of global
        else:
            limit = int(self.rate_config.requests_per_hour * 0.2)  # 20% of global

        # Apply adaptive adjustment
        if self.rate_config.adaptive_enabled:
            adaptive_multiplier = self._calculate_adaptive_multiplier()
            limit = int(limit * adaptive_multiplier)

        return RateLimitQuota(
            scope_id=scope_id,
            scope_type=scope_type,
            remaining_requests=limit,
            requests_limit=limit,
            reset_time=now + timedelta(hours=1),
            window_start=now,
            window_end=now + timedelta(hours=1),
            tokens_available=float(self.rate_config.bucket_capacity),
        )

    def _apply_rate_limiting_strategy(
        self, quota: RateLimitQuota, request: RateLimitRequest
    ) -> RateLimitStatus:
        """Apply configured rate limiting strategy."""
        strategy = self.rate_config.strategy

        if strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._apply_token_bucket(quota, request)
        elif strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._apply_sliding_window(quota, request)
        elif strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._apply_fixed_window(quota, request)
        else:
            # Default to simple counter
            return self._apply_simple_counter(quota, request)

    def _apply_token_bucket(self, quota: RateLimitQuota, request: RateLimitRequest) -> RateLimitStatus:
        """Apply token bucket rate limiting."""
        now = datetime.now(timezone.utc)
        
        # Refill tokens based on elapsed time
        time_elapsed = (now - quota.last_refill).total_seconds()
        tokens_to_add = time_elapsed * self.rate_config.refill_rate
        quota.tokens_available = min(
            self.rate_config.bucket_capacity,
            quota.tokens_available + tokens_to_add
        )
        quota.last_refill = now

        # Check if token available
        if quota.tokens_available >= 1.0:
            quota.tokens_available -= 1.0
            return RateLimitStatus.ALLOWED
        else:
            # Calculate retry after time
            tokens_needed = 1.0 - quota.tokens_available
            retry_after = tokens_needed / self.rate_config.refill_rate
            request.retry_after_seconds = retry_after
            
            if self.rate_config.queue_enabled:
                return RateLimitStatus.THROTTLED
            else:
                return RateLimitStatus.REJECTED

    def _apply_sliding_window(self, quota: RateLimitQuota, request: RateLimitRequest) -> RateLimitStatus:
        """Apply sliding window rate limiting."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.rate_config.window_size_seconds)
        
        # Get window for this scope
        scope_key = f"{request.scope_type.value}:{request.scope_id}"
        window = self._sliding_windows[scope_key]
        
        # Remove old entries
        while window and window[0] < window_start:
            window.popleft()
        
        # Check if under limit
        if len(window) < quota.requests_limit:
            window.append(now)
            return RateLimitStatus.ALLOWED
        else:
            # Calculate retry after time
            oldest_request = window[0]
            retry_after = (oldest_request + timedelta(seconds=self.rate_config.window_size_seconds) - now).total_seconds()
            request.retry_after_seconds = max(1.0, retry_after)
            
            if self.rate_config.queue_enabled:
                return RateLimitStatus.THROTTLED
            else:
                return RateLimitStatus.REJECTED

    def _apply_fixed_window(self, quota: RateLimitQuota, request: RateLimitRequest) -> RateLimitStatus:
        """Apply fixed window rate limiting."""
        if quota.remaining_requests > 0:
            return RateLimitStatus.ALLOWED
        else:
            retry_after = quota.time_until_reset().total_seconds()
            request.retry_after_seconds = retry_after
            
            if self.rate_config.queue_enabled:
                return RateLimitStatus.THROTTLED
            else:
                return RateLimitStatus.REJECTED

    def _apply_simple_counter(self, quota: RateLimitQuota, request: RateLimitRequest) -> RateLimitStatus:
        """Apply simple counter-based rate limiting."""
        return self._apply_fixed_window(quota, request)

    def _handle_allowed_request(self, quota: RateLimitQuota, request: RateLimitRequest) -> None:
        """Handle allowed request."""
        quota.current_requests += 1
        quota.remaining_requests = max(0, quota.remaining_requests - 1)
        quota.total_requests += 1
        
        request.status = RateLimitStatus.ALLOWED
        request.quota_remaining = quota.remaining_requests
        request.quota_reset_time = quota.reset_time
        
        self._log_rate_limit_event(RateLimitEventType.REQUEST_ALLOWED, request)

    def _handle_throttled_request(
        self, quota: RateLimitQuota, request: RateLimitRequest, backoff_key: str
    ) -> None:
        """Handle throttled request."""
        quota.throttled_requests += 1
        request.status = RateLimitStatus.THROTTLED
        request.quota_remaining = quota.remaining_requests
        request.quota_reset_time = quota.reset_time
        
        # Apply backoff
        self._apply_backoff(backoff_key, request)
        
        # Add to queue if enabled
        if self.rate_config.queue_enabled and len(self._request_queue) < self.rate_config.max_queue_size:
            request.queue_position = len(self._request_queue) + 1
            self._request_queue.append(request)
        
        self._log_rate_limit_event(RateLimitEventType.REQUEST_THROTTLED, request)

    def _handle_rejected_request(
        self, quota: RateLimitQuota, request: RateLimitRequest, backoff_key: str
    ) -> None:
        """Handle rejected request."""
        quota.rejected_requests += 1
        request.status = RateLimitStatus.REJECTED
        request.quota_remaining = quota.remaining_requests
        request.quota_reset_time = quota.reset_time
        
        # Apply backoff
        self._apply_backoff(backoff_key, request)
        
        self._log_rate_limit_event(RateLimitEventType.REQUEST_REJECTED, request)

    def _apply_backoff(self, backoff_key: str, request: RateLimitRequest) -> None:
        """Apply backoff strategy."""
        if backoff_key not in self._backoff_states:
            self._backoff_states[backoff_key] = BackoffState(
                scope_id=request.scope_id,
                operation_type=request.operation_type,
                strategy=self.rate_config.backoff_strategy,
                base_delay=self.rate_config.base_delay_seconds,
                max_delay=self.rate_config.max_delay_seconds,
                multiplier=self.rate_config.backoff_multiplier,
                next_retry_time=datetime.now(timezone.utc),
            )

        backoff_state = self._backoff_states[backoff_key]
        backoff_state.attempt_count += 1
        backoff_state.retry_history.append(datetime.now(timezone.utc))

        # Calculate delay based on strategy
        delay = self._calculate_backoff_delay(backoff_state)
        
        # Apply jitter if enabled
        if self.rate_config.jitter_enabled:
            jitter = random.uniform(0.8, 1.2)
            delay *= jitter

        # Clamp to max delay
        delay = min(delay, self.rate_config.max_delay_seconds)
        
        backoff_state.current_delay_seconds = delay
        backoff_state.next_retry_time = datetime.now(timezone.utc) + timedelta(seconds=delay)
        
        request.retry_after_seconds = delay
        request.backoff_count = backoff_state.attempt_count

    def _calculate_backoff_delay(self, backoff_state: BackoffState) -> float:
        """Calculate backoff delay based on strategy."""
        strategy = backoff_state.strategy
        attempt = backoff_state.attempt_count
        base_delay = backoff_state.base_delay

        if strategy == BackoffStrategy.LINEAR:
            return base_delay * attempt
        elif strategy == BackoffStrategy.EXPONENTIAL:
            return base_delay * (backoff_state.multiplier ** (attempt - 1))
        elif strategy == BackoffStrategy.FIBONACCI:
            return base_delay * self._fibonacci(attempt)
        elif strategy == BackoffStrategy.JITTERED:
            base = base_delay * (backoff_state.multiplier ** (attempt - 1))
            return base * random.uniform(0.5, 1.5)
        else:
            return base_delay

    def _fibonacci(self, n: int) -> int:
        """Calculate fibonacci number."""
        if n <= 2:
            return 1
        a, b = 1, 1
        for _ in range(3, n + 1):
            a, b = b, a + b
        return b

    def _calculate_adaptive_multiplier(self) -> float:
        """Calculate adaptive rate multiplier based on system load."""
        if not self.rate_config.adaptive_enabled:
            return 1.0

        # Simple load-based adaptation
        if self._system_load > self.rate_config.load_threshold:
            reduction = (self._system_load - self.rate_config.load_threshold) * self.rate_config.adaptation_factor
            return max(0.1, 1.0 - reduction)
        else:
            return 1.0

    def _update_statistics_for_request(self, request: RateLimitRequest) -> None:
        """Update statistics for processed request."""
        self.statistics.total_requests += 1

        if request.status == RateLimitStatus.ALLOWED:
            self.statistics.allowed_requests += 1
        elif request.status == RateLimitStatus.THROTTLED:
            self.statistics.throttled_requests += 1
        elif request.status == RateLimitStatus.REJECTED:
            self.statistics.rejected_requests += 1

        # Update processing time
        if request.processing_time_ms:
            current_avg = self.statistics.avg_processing_time_ms
            total = self.statistics.total_requests
            self.statistics.avg_processing_time_ms = (
                (current_avg * (total - 1) + request.processing_time_ms) / total
            )

        # Update rates
        if self.statistics.total_requests > 0:
            self.statistics.throttle_rate_percent = (
                self.statistics.throttled_requests / self.statistics.total_requests
            ) * 100
            self.statistics.rejection_rate_percent = (
                self.statistics.rejected_requests / self.statistics.total_requests
            ) * 100

    async def _cleanup_loop(self) -> None:
        """Background cleanup task."""
        while not self._shutdown:
            try:
                await asyncio.sleep(60)  # Run every minute
                self._cleanup_expired_quotas()
                self._cleanup_old_backoff_states()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")

    async def _process_queue_loop(self) -> None:
        """Background queue processing task."""
        while not self._shutdown:
            try:
                await asyncio.sleep(1)  # Check queue every second
                self._process_queued_requests()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in queue processing: {e}")

    async def _metrics_loop(self) -> None:
        """Background metrics collection task."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.rate_config.metrics_window_seconds)
                self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")

    def _cleanup_expired_quotas(self) -> None:
        """Remove expired quotas."""
        with self._lock:
            expired_keys = [
                key for key, quota in self._quotas.items() 
                if quota.is_expired()
            ]
            for key in expired_keys:
                del self._quotas[key]
            
            if expired_keys:
                self._log_info(f"Cleaned up {len(expired_keys)} expired quotas")

    def _cleanup_old_backoff_states(self) -> None:
        """Remove old backoff states."""
        with self._lock:
            now = datetime.now(timezone.utc)
            old_threshold = now - timedelta(hours=1)
            
            old_keys = [
                key for key, state in self._backoff_states.items()
                if state.retry_history and state.retry_history[-1] < old_threshold
            ]
            for key in old_keys:
                del self._backoff_states[key]
            
            if old_keys:
                self._log_info(f"Cleaned up {len(old_keys)} old backoff states")

    def _process_queued_requests(self) -> None:
        """Process queued requests that might now be allowed."""
        with self._lock:
            processed = 0
            while self._request_queue and processed < 10:  # Process up to 10 per cycle
                request = self._request_queue[0]
                
                # Check if quota allows this request now
                quota_key = f"{request.scope_type.value}:{request.scope_id}"
                if quota_key in self._quotas:
                    quota = self._quotas[quota_key]
                    if quota.remaining_requests > 0:
                        self._request_queue.popleft()
                        request.status = RateLimitStatus.ALLOWED
                        self._handle_allowed_request(quota, request)
                        processed += 1
                        continue
                
                # Check timeout
                age = (datetime.now(timezone.utc) - request.timestamp).total_seconds()
                if age > self.rate_config.queue_timeout_seconds:
                    self._request_queue.popleft()
                    self.statistics.queue_timeouts += 1
                    processed += 1
                    continue
                
                break  # Stop at first non-processable request
            
            if processed > 0:
                self._log_info(f"Processed {processed} queued requests")

    def _collect_metrics(self) -> None:
        """Collect and update metrics."""
        with self._lock:
            # Update queue metrics
            if self._request_queue:
                self.statistics.avg_queue_size = len(self._request_queue)
            
            # Update system load (simplified - could integrate with system monitoring)
            self._system_load = random.uniform(0.3, 0.9)  # Placeholder
            self._load_samples.append(self._system_load)
            
            self.statistics.system_load_percent = self._system_load * 100
            self.statistics.current_rate_multiplier = self._calculate_adaptive_multiplier()

    def get_statistics(self) -> RateLimitStatistics:
        """Get current rate limiting statistics."""
        with self._lock:
            return self.statistics.model_copy()

    def reset_statistics(self) -> None:
        """Reset rate limiting statistics."""
        with self._lock:
            self.statistics = RateLimitStatistics()
            self._log_info("Rate limiter statistics reset")

    def _log_rate_limit_event(self, event_type: RateLimitEventType, request: RateLimitRequest) -> None:
        """Log rate limiting event."""
        message = f"Rate limit {event_type.value}: {request.scope_id} ({request.status.value})"
        
        if self.dev_logger:
            self.dev_logger.log_debug(
                SDKEventType.DEBUG_CHECKPOINT,
                message,
                details={
                    "event_type": event_type.value,
                    "scope_id": request.scope_id,
                    "status": request.status.value,
                    "retry_after": request.retry_after_seconds,
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
    "RateLimiter",
    
    # Note: Rate limiting models are available via DTO imports:
    # from unrealon_sdk.src.dto.rate_limiting import ...
]
