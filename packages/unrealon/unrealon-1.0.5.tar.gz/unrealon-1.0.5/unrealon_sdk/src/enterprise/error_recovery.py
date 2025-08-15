"""
Error Recovery System - Layer 2 Connection Management Component

Enterprise-grade error recovery with exponential backoff, circuit breakers,
and automatic retry mechanisms. Provides resilient connection management
for WebSocket and HTTP clients with intelligent failure detection and recovery.

Features:
- Exponential backoff with jitter for retry timing
- Circuit breaker pattern for fault tolerance
- Automatic reconnection with configurable limits
- Health monitoring and recovery metrics
- Error classification and appropriate response strategies
- Integration with development logging for observability
"""

import asyncio
import logging
import time
import random
from typing import Optional, Dict, List, Any, Callable, Awaitable, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
import traceback

# Pydantic v2 for all data models
from pydantic import BaseModel, Field, ConfigDict

# Auto-generated models for error handling
from unrealon_sdk.src.clients.python_http.models import ErrorResponse

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.core.exceptions import ConnectionError, LoggingError
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models for error recovery
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity

# Development logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Types of errors that can trigger recovery mechanisms."""
    
    CONNECTION_TIMEOUT = "connection_timeout"
    CONNECTION_REFUSED = "connection_refused"
    NETWORK_UNREACHABLE = "network_unreachable"
    AUTHENTICATION_FAILED = "authentication_failed"
    SERVER_ERROR = "server_error"
    RATE_LIMITED = "rate_limited"
    WEBSOCKET_CLOSED = "websocket_closed"
    HTTP_CLIENT_ERROR = "http_client_error"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(str, Enum):
    """Recovery strategies for different error types."""
    
    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"
    NO_RETRY = "no_retry"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_retries: int = 5
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    exponential_base: float = 2.0
    jitter_factor: float = 0.1  # Add randomness to avoid thundering herd
    timeout: float = 30.0  # Operation timeout


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: float = 30.0  # Seconds before attempting recovery
    success_threshold: int = 3  # Successes needed to close circuit
    monitoring_window: float = 60.0  # Time window for failure counting


class ErrorRecoveryMetrics(BaseModel):
    """Metrics for error recovery operations."""
    
    model_config = ConfigDict(extra="forbid")
    
    total_errors: int = Field(default=0, description="Total errors encountered")
    errors_by_type: Dict[str, int] = Field(default_factory=dict, description="Errors by type")
    total_retries: int = Field(default=0, description="Total retry attempts")
    successful_recoveries: int = Field(default=0, description="Successful recoveries")
    failed_recoveries: int = Field(default=0, description="Failed recoveries")
    circuit_breaker_trips: int = Field(default=0, description="Circuit breaker activations")
    average_recovery_time: float = Field(default=0.0, description="Average recovery time in seconds")


class ErrorRecoveryEvent(BaseModel):
    """Event model for error recovery operations."""
    
    model_config = ConfigDict(extra="forbid")
    
    event_id: str = Field(default_factory=generate_correlation_id, description="Unique event ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    error_type: ErrorType = Field(..., description="Type of error")
    strategy: RecoveryStrategy = Field(..., description="Recovery strategy used")
    attempt_number: int = Field(..., description="Retry attempt number")
    delay_seconds: float = Field(..., description="Delay before retry")
    success: bool = Field(..., description="Whether recovery was successful")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    duration_ms: Optional[float] = Field(default=None, description="Recovery operation duration")


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""
    
    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.failure_times: List[float] = []
        
    def can_execute(self) -> bool:
        """Check if operation can be executed based on circuit breaker state."""
        now = time.time()
        
        # Clean old failures outside monitoring window
        cutoff_time = now - self.config.monitoring_window
        self.failure_times = [t for t in self.failure_times if t > cutoff_time]
        self.failure_count = len(self.failure_times)
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (self.last_failure_time and 
                now - self.last_failure_time >= self.config.recovery_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        
        # self.state == CircuitBreakerState.HALF_OPEN
        return True
    
    def record_success(self) -> None:
        """Record a successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.failure_times.clear()
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self) -> None:
        """Record a failed operation."""
        now = time.time()
        self.failure_times.append(now)
        self.failure_count += 1
        self.last_failure_time = now
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.success_count = 0


class ErrorRecoverySystem:
    """
    Enterprise-grade error recovery system with exponential backoff and circuit breakers.
    
    Provides intelligent error handling and automatic recovery for connection management
    components including WebSocket and HTTP clients.
    """
    
    def __init__(
        self,
        config: AdapterConfig,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize error recovery system."""
        self.config = config
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.dev_logger = dev_logger
        
        # Circuit breakers for different components
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Metrics
        self.metrics = ErrorRecoveryMetrics()
        
        # Error type to strategy mapping
        self.error_strategies: Dict[ErrorType, RecoveryStrategy] = {
            ErrorType.CONNECTION_TIMEOUT: RecoveryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.CONNECTION_REFUSED: RecoveryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.NETWORK_UNREACHABLE: RecoveryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.AUTHENTICATION_FAILED: RecoveryStrategy.NO_RETRY,
            ErrorType.SERVER_ERROR: RecoveryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.RATE_LIMITED: RecoveryStrategy.LINEAR_BACKOFF,
            ErrorType.WEBSOCKET_CLOSED: RecoveryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.HTTP_CLIENT_ERROR: RecoveryStrategy.CIRCUIT_BREAKER,
            ErrorType.UNKNOWN_ERROR: RecoveryStrategy.EXPONENTIAL_BACKOFF,
        }
        
        self._log_info("Error recovery system initialized")
    
    def get_circuit_breaker(self, component_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for component."""
        if component_name not in self.circuit_breakers:
            self.circuit_breakers[component_name] = CircuitBreaker(
                self.circuit_breaker_config, 
                component_name
            )
        return self.circuit_breakers[component_name]
    
    async def execute_with_recovery(
        self,
        operation: Callable[[], Awaitable[Any]],
        component_name: str,
        operation_name: str,
        error_classifier: Optional[Callable[[Exception], ErrorType]] = None,
    ) -> Any:
        """
        Execute operation with automatic error recovery.
        
        Args:
            operation: Async operation to execute
            component_name: Name of component (for circuit breaker)
            operation_name: Name of operation (for logging)
            error_classifier: Function to classify exceptions into ErrorType
            
        Returns:
            Result of successful operation
            
        Raises:
            Exception: If all recovery attempts fail
        """
        circuit_breaker = self.get_circuit_breaker(component_name)
        last_exception: Optional[Exception] = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            # Check circuit breaker
            if not circuit_breaker.can_execute():
                self._log_error(
                    f"Circuit breaker open for {component_name}, skipping {operation_name}",
                    error_type=ErrorType.UNKNOWN_ERROR,
                )
                self.metrics.circuit_breaker_trips += 1
                raise ConnectionError(f"Circuit breaker open for {component_name}")
            
            try:
                start_time = time.time()
                
                # Execute operation with timeout
                result = await asyncio.wait_for(
                    operation(),
                    timeout=self.retry_config.timeout
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Record success
                circuit_breaker.record_success()
                
                if attempt > 0:
                    self.metrics.successful_recoveries += 1
                    self._log_info(
                        f"Recovery successful for {operation_name} after {attempt} attempts",
                        duration_ms=duration_ms
                    )
                
                return result
                
            except Exception as e:
                last_exception = e
                self.metrics.total_errors += 1
                
                # Classify error
                error_type = error_classifier(e) if error_classifier else self._classify_error(e)
                self.metrics.errors_by_type[error_type.value] = (
                    self.metrics.errors_by_type.get(error_type.value, 0) + 1
                )
                
                # Record failure in circuit breaker
                circuit_breaker.record_failure()
                
                # Determine if we should retry
                strategy = self.error_strategies.get(error_type, RecoveryStrategy.EXPONENTIAL_BACKOFF)
                
                if strategy == RecoveryStrategy.NO_RETRY or attempt >= self.retry_config.max_retries:
                    self.metrics.failed_recoveries += 1
                    self._log_error(
                        f"Recovery failed for {operation_name} after {attempt + 1} attempts",
                        error_type=error_type,
                        exception=e
                    )
                    raise e
                
                # Calculate delay and wait
                delay = self._calculate_delay(attempt, strategy)
                
                self._log_recovery_event(
                    error_type=error_type,
                    strategy=strategy,
                    attempt_number=attempt + 1,
                    delay_seconds=delay,
                    success=False,
                    error_details={"exception": str(e), "component": component_name}
                )
                
                self.metrics.total_retries += 1
                
                if delay > 0:
                    await asyncio.sleep(delay)
        
        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        else:
            raise ConnectionError(f"Failed to execute {operation_name} after all retries")
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify exception into ErrorType for recovery strategy selection."""
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        if "timeout" in error_str or "timeout" in error_type_name:
            return ErrorType.CONNECTION_TIMEOUT
        elif "connection refused" in error_str or "refused" in error_str:
            return ErrorType.CONNECTION_REFUSED
        elif "network" in error_str or "unreachable" in error_str:
            return ErrorType.NETWORK_UNREACHABLE
        elif "auth" in error_str or "unauthorized" in error_str:
            return ErrorType.AUTHENTICATION_FAILED
        elif "server error" in error_str or "500" in error_str:
            return ErrorType.SERVER_ERROR
        elif "rate" in error_str or "429" in error_str:
            return ErrorType.RATE_LIMITED
        elif "websocket" in error_str or "socket" in error_str:
            return ErrorType.WEBSOCKET_CLOSED
        elif "http" in error_str:
            return ErrorType.HTTP_CLIENT_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def _calculate_delay(self, attempt: int, strategy: RecoveryStrategy) -> float:
        """Calculate delay for retry attempt based on strategy."""
        if strategy == RecoveryStrategy.IMMEDIATE_RETRY:
            return 0.0
        elif strategy == RecoveryStrategy.LINEAR_BACKOFF:
            delay = self.retry_config.base_delay * (attempt + 1)
        elif strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt)
        else:
            delay = self.retry_config.base_delay
        
        # Apply jitter to avoid thundering herd
        jitter = delay * self.retry_config.jitter_factor * (2 * random.random() - 1)
        delay += jitter
        
        # Clamp to max delay
        return min(delay, self.retry_config.max_delay)
    
    def _log_recovery_event(
        self,
        error_type: ErrorType,
        strategy: RecoveryStrategy,
        attempt_number: int,
        delay_seconds: float,
        success: bool,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log recovery event for monitoring and debugging."""
        event = ErrorRecoveryEvent(
            error_type=error_type,
            strategy=strategy,
            attempt_number=attempt_number,
            delay_seconds=delay_seconds,
            success=success,
            error_details=error_details,
        )
        
        self._log_info(
            f"Error recovery attempt {attempt_number}: {error_type.value} -> {strategy.value}",
            details={"recovery_event": event.model_dump()}
        )
    
    def _log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message with development logger if available."""
        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.ERROR_RECOVERY_STARTED,
                message,
                **kwargs
            )
        else:
            logger.info(message)
    
    def _log_error(
        self, 
        message: str, 
        error_type: ErrorType, 
        exception: Optional[Exception] = None,
        **kwargs: Any
    ) -> None:
        """Log error message with development logger if available."""
        if self.dev_logger:
            self.dev_logger.log_error(
                SDKEventType.ERROR_RECOVERY_FAILED,
                message,
                exception=exception,
                details={"error_type": error_type.value},
                **kwargs
            )
        else:
            logger.error(message, exc_info=exception)
    
    def get_metrics(self) -> ErrorRecoveryMetrics:
        """Get current error recovery metrics."""
        return self.metrics
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {
            name: {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
                "last_failure_time": breaker.last_failure_time,
            }
            for name, breaker in self.circuit_breakers.items()
        }
    
    def reset_circuit_breaker(self, component_name: str) -> bool:
        """Manually reset circuit breaker for component."""
        if component_name in self.circuit_breakers:
            breaker = self.circuit_breakers[component_name]
            breaker.state = CircuitBreakerState.CLOSED
            breaker.failure_count = 0
            breaker.success_count = 0
            breaker.failure_times.clear()
            
            self._log_info(f"Circuit breaker reset for {component_name}")
            return True
        return False


__all__ = [
    # Main class
    "ErrorRecoverySystem",
    # Enums
    "ErrorType",
    "RecoveryStrategy", 
    "CircuitBreakerState",
    # Configuration
    "RetryConfig",
    "CircuitBreakerConfig",
    # Models
    "ErrorRecoveryMetrics",
    "ErrorRecoveryEvent",
    # Circuit breaker
    "CircuitBreaker",
]
