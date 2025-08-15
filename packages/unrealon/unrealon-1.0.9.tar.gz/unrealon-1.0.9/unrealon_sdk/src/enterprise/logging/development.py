"""
Development Process Logger for UnrealOn SDK

Enterprise-grade development logging system for tracking SDK development process,
performance metrics, debugging information, and compliance with development standards.
Following KISS methodology and 100% Pydantic v2 compliance.
"""

import logging
import json
import asyncio
from typing import Optional, List, Any, Dict
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import threading
import traceback
import sys
import os

# Pydantic v2 for all data models
from pydantic import BaseModel, Field, ConfigDict

# Auto-generated models from the API
# Import from centralized logging service
from unrealon_sdk.src.enterprise.logging.service import LogLevel, LogEntryMessage

# DTO models for development logging
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity, SDKContext, SDKDevelopmentEvent

# Core SDK components
from unrealon_sdk.src.core.exceptions import LoggingError
from unrealon_sdk.src.utils import generate_correlation_id

# Import cleanup module at module level to avoid inline imports
from unrealon_sdk.src.enterprise.logging.cleanup import clear_development_logs, sdk_startup_cleanup

# Direct import needed for return type
try:
    from unrealon_sdk.src.core.metadata import DevelopmentLoggerStatistics
except ImportError:
    # Fallback for circular import issues
    from typing import Any as DevelopmentLoggerStatistics

logger = logging.getLogger(__name__)


class DevelopmentLogger:
    """
    Enterprise-grade development logging system for UnrealOn SDK.

    Features:
    - Structured development event logging
    - Real-time WebSocket streaming
    - Performance metrics tracking
    - Code quality monitoring
    - Layer-based development tracking (Skyscraper Architecture)
    - Type-safe logging with Pydantic v2
    - Thread-safe operations
    - Memory-efficient buffering
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        log_level: SDKSeverity = SDKSeverity.INFO,
        enable_console: bool = True,
        enable_websocket: bool = True,
        buffer_size: int = 50,
        flush_interval_seconds: float = 2.0,
    ):
        """Initialize development logger."""
        self.session_id = session_id or generate_correlation_id()
        self.log_level = log_level
        self.enable_console = enable_console
        self.enable_websocket = enable_websocket

        # WebSocket client for real-time streaming (will be injected)
        self._websocket_client = None

        # Buffering for performance
        self._buffer: List[SDKDevelopmentEvent] = []
        self._buffer_lock = threading.Lock()
        self._buffer_size = buffer_size
        self._flush_interval = flush_interval_seconds
        self._flush_task: Optional[asyncio.Task[None]] = None

        # Statistics
        self._events_logged = 0
        self._events_by_type: Dict[SDKEventType, int] = {}
        self._events_by_severity = {severity: 0 for severity in SDKSeverity}
        self._errors_count = 0
        self._warnings_count = 0

        # Context tracking
        self._current_layer: Optional[str] = None
        self._current_component: Optional[str] = None
        self._active_operations: Dict[str, datetime] = {}

        # Standard logger for console output
        self._setup_console_logger()
        
        # Perform automatic log cleanup for development logs
        self._cleanup_development_logs()

        # State
        self._initialized = True
        self._shutdown = False

        self.log_info(
            SDKEventType.SDK_INITIALIZED,
            f"DevelopmentLogger initialized for session {self.session_id}",
        )

    def _cleanup_development_logs(self) -> None:
        """Cleanup old development logs on startup."""
        try:
            # Use sdk_startup_cleanup to ensure it happens only once
            sdk_startup_cleanup()
        except Exception as e:
            # Don't fail logger initialization due to cleanup issues
            print(f"⚠️  SDK: Development log cleanup failed: {e}")

    def _setup_console_logger(self) -> None:
        """Setup console logging with structured formatting."""
        if not self.enable_console:
            return

        self.console_logger = logging.getLogger(f"sdk_dev_{self.session_id}")
        self.console_logger.setLevel(self._severity_to_logging_level(self.log_level))

        # Clear existing handlers
        self.console_logger.handlers.clear()

        # Custom formatter for development logs
        formatter = logging.Formatter(
            "%(asctime)s | SDK-DEV | %(levelname)s | %(message)s", datefmt="%H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.console_logger.addHandler(console_handler)

        # Prevent propagation to avoid duplicate logs
        self.console_logger.propagate = False

    async def initialize_websocket(self, websocket_client) -> None:
        """Initialize WebSocket client for real-time log streaming."""
        self._websocket_client = websocket_client

        if self.enable_websocket and self._flush_task is None:
            self._flush_task = asyncio.create_task(self._auto_flush_loop())

        self.log_info(
            SDKEventType.LOGGING_SERVICE_INITIALIZED,
            "WebSocket client initialized for development logging",
        )

    async def shutdown(self) -> None:
        """Shutdown logger and flush remaining events."""
        self._shutdown = True

        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self._flush_buffer()

        self.log_info(
            SDKEventType.SDK_SHUTDOWN,
            f"DevelopmentLogger shutdown complete. Total events: {self._events_logged}",
        )

    # Context Management
    def set_layer_context(self, layer_name: str) -> None:
        """Set current development layer context."""
        self._current_layer = layer_name
        self.log_info(
            SDKEventType.LAYER_STARTED,
            f"Entering development layer: {layer_name}",
            context=SDKContext(layer_name=layer_name),
        )

    def set_component_context(self, component_name: str) -> None:
        """Set current component context."""
        self._current_component = component_name
        self.log_debug(
            SDKEventType.COMPONENT_CREATED,
            f"Working on component: {component_name}",
            context=SDKContext(component_name=component_name, layer_name=self._current_layer),
        )

    def start_operation(self, operation_id: str, description: str) -> None:
        """Start tracking a long-running operation."""
        self._active_operations[operation_id] = datetime.now(timezone.utc)
        self.log_debug(
            SDKEventType.DEBUG_CHECKPOINT,
            f"Started operation: {description}",
            context=SDKContext(correlation_id=operation_id),
        )

    def complete_operation(self, operation_id: str, description: str, success: bool = True) -> None:
        """Complete a tracked operation."""
        if operation_id in self._active_operations:
            start_time = self._active_operations.pop(operation_id)
            duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            self.log_info(
                SDKEventType.COMPONENT_INTEGRATED if success else SDKEventType.COMPONENT_DEPRECATED,
                f"Completed operation: {description}",
                success=success,
                context=SDKContext(correlation_id=operation_id, execution_time_ms=duration),
                duration_ms=duration,
            )

    # Logging Methods
    def log_trace(
        self,
        event_type: SDKEventType,
        message: str,
        context: Optional[SDKContext] = None,
        details: Optional[Any] = None,
    ) -> None:
        """Log trace-level event."""
        self._log_event(
            event_type=event_type,
            message=message,
            severity=SDKSeverity.TRACE,
            success=True,
            context=context,
            details=details,
        )

    def log_debug(
        self,
        event_type: SDKEventType,
        message: str,
        context: Optional[SDKContext] = None,
        details: Optional[Any] = None,
    ) -> None:
        """Log debug-level event."""
        self._log_event(
            event_type=event_type,
            message=message,
            severity=SDKSeverity.DEBUG,
            success=True,
            context=context,
            details=details,
        )

    def log_info(
        self,
        event_type: SDKEventType,
        message: str,
        context: Optional[SDKContext] = None,
        details: Optional[Any] = None,
        success: bool = True,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Log info-level event."""
        self._log_event(
            event_type=event_type,
            message=message,
            severity=SDKSeverity.INFO,
            success=success,
            context=context,
            details=details,
            duration_ms=duration_ms,
        )

    def log_warning(
        self,
        event_type: SDKEventType,
        message: str,
        context: Optional[SDKContext] = None,
        details: Optional[Any] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Log warning-level event."""
        self._log_event(
            event_type=event_type,
            message=message,
            severity=SDKSeverity.WARNING,
            success=False,
            context=context,
            details=details,
            error_message=error_message,
        )
        self._warnings_count += 1

    def log_error(
        self,
        event_type: SDKEventType,
        message: str,
        context: Optional[SDKContext] = None,
        details: Optional[Any] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """Log error-level event."""
        # Include exception details if provided
        if exception:
            error_details = {
                **(details or {}),
                "exception_type": type(exception).__name__,
                "exception_str": str(exception),
                "stack_trace": traceback.format_exc(),
            }
        else:
            error_details = details

        self._log_event(
            event_type=event_type,
            message=message,
            severity=SDKSeverity.ERROR,
            success=False,
            context=context,
            details=error_details,
            error_code=error_code,
            error_message=error_message,
        )
        self._errors_count += 1

    def log_critical(
        self,
        event_type: SDKEventType,
        message: str,
        context: Optional[SDKContext] = None,
        details: Optional[Any] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """Log critical-level event."""
        # Include exception details if provided
        if exception:
            error_details = {
                **(details or {}),
                "exception_type": type(exception).__name__,
                "exception_str": str(exception),
                "stack_trace": traceback.format_exc(),
            }
        else:
            error_details = details

        self._log_event(
            event_type=event_type,
            message=message,
            severity=SDKSeverity.CRITICAL,
            success=False,
            context=context,
            details=error_details,
            error_code=error_code,
            error_message=error_message,
        )
        self._errors_count += 1

    # Specialized Logging Methods
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        threshold: Optional[float] = None,
        context: Optional[SDKContext] = None,
    ) -> None:
        """Log performance metric."""
        exceeded = threshold is not None and value > threshold

        details = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "threshold": threshold,
            "threshold_exceeded": exceeded,
        }

        severity = SDKSeverity.WARNING if exceeded else SDKSeverity.DEBUG
        event_type = (
            SDKEventType.PERFORMANCE_THRESHOLD_EXCEEDED
            if exceeded
            else SDKEventType.PERFORMANCE_METRIC_COLLECTED
        )

        self._log_event(
            event_type=event_type,
            message=f"Performance metric {metric_name}: {value} {unit}",
            severity=severity,
            success=not exceeded,
            context=context,
            details=details,
        )

    def log_api_call(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Log API call event."""
        details = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }

        event_type = SDKEventType.API_CALL_COMPLETED if success else SDKEventType.API_CALL_FAILED
        severity = SDKSeverity.DEBUG if success else SDKSeverity.ERROR

        self._log_event(
            event_type=event_type,
            message=f"{method} {url} - {status_code or 'No Response'}",
            severity=severity,
            success=success,
            details=details,
            error_message=error_message,
            duration_ms=duration_ms,
        )

    def log_layer_validation(
        self,
        layer_name: str,
        checklist_items: List[str],
        passed_items: List[str],
        failed_items: List[str],
    ) -> None:
        """Log layer validation results (Skyscraper Architecture)."""
        success = len(failed_items) == 0

        details = {
            "layer_name": layer_name,
            "total_items": len(checklist_items),
            "passed_items": len(passed_items),
            "failed_items": len(failed_items),
            "passed_list": passed_items,
            "failed_list": failed_items,
            "success_rate": len(passed_items) / len(checklist_items) * 100,
        }

        event_type = SDKEventType.LAYER_COMPLETED if success else SDKEventType.LAYER_FAILED
        severity = SDKSeverity.INFO if success else SDKSeverity.ERROR

        self._log_event(
            event_type=event_type,
            message=f"Layer {layer_name} validation: {len(passed_items)}/{len(checklist_items)} items passed",
            severity=severity,
            success=success,
            context=SDKContext(layer_name=layer_name),
            details=details,
        )

    # Internal Methods
    def _log_event(
        self,
        event_type: SDKEventType,
        message: str,
        severity: SDKSeverity,
        success: bool = True,
        context: Optional[SDKContext] = None,
        details: Optional[Any] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Internal method to log structured development event."""
        try:
            # Skip if below log level
            if not self._should_log(severity):
                return

            # Enhance context with current state
            enhanced_context = context or SDKContext()
            if not enhanced_context.layer_name:
                enhanced_context.layer_name = self._current_layer
            if not enhanced_context.component_name:
                enhanced_context.component_name = self._current_component
            if not enhanced_context.thread_id:
                enhanced_context.thread_id = str(threading.get_ident())
            if not enhanced_context.correlation_id:
                enhanced_context.correlation_id = generate_correlation_id()

            # Create event
            event = SDKDevelopmentEvent(
                event_type=event_type,
                severity=severity,
                message=message,
                success=success,
                context=enhanced_context,
                details=details or {},
                error_code=error_code,
                error_message=error_message,
                duration_ms=duration_ms,
            )

            # Update statistics
            self._events_logged += 1
            self._events_by_severity[severity] += 1
            self._events_by_type[event_type] = self._events_by_type.get(event_type, 0) + 1

            # Console logging
            if self.enable_console:
                self._log_to_console(event)

            # Buffer for WebSocket streaming
            if self.enable_websocket:
                with self._buffer_lock:
                    self._buffer.append(event)

                    # Auto-flush if buffer is full
                    if len(self._buffer) >= self._buffer_size:
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(self._flush_buffer())
                        except RuntimeError:
                            # No event loop running, skip async flush
                            pass

        except Exception as e:
            # Never let logging break the application
            if self.enable_console:
                print(f"DevelopmentLogger error: {e}", file=sys.stderr)

    def _should_log(self, severity: SDKSeverity) -> bool:
        """Check if event should be logged based on level."""
        severity_order = {
            SDKSeverity.TRACE: 0,
            SDKSeverity.DEBUG: 1,
            SDKSeverity.INFO: 2,
            SDKSeverity.WARNING: 3,
            SDKSeverity.ERROR: 4,
            SDKSeverity.CRITICAL: 5,
            SDKSeverity.FATAL: 6,
        }

        return severity_order.get(severity, 2) >= severity_order.get(self.log_level, 2)

    def _log_to_console(self, event: SDKDevelopmentEvent) -> None:
        """Log event to console with structured formatting."""
        try:
            # Format message with context
            context_info = []
            if event.context.layer_name:
                context_info.append(f"Layer:{event.context.layer_name}")
            if event.context.component_name:
                context_info.append(f"Component:{event.context.component_name}")
            if event.duration_ms:
                context_info.append(f"{event.duration_ms:.2f}ms")

            context_str = f" [{', '.join(context_info)}]" if context_info else ""
            formatted_message = f"{event.event_type.value.upper()}: {event.message}{context_str}"

            # Add error details
            if not event.success and event.error_message:
                formatted_message += f" | Error: {event.error_message}"

            # Log at appropriate level
            log_level = self._severity_to_logging_level(event.severity)
            self.console_logger.log(log_level, formatted_message)

        except Exception as e:
            print(f"Console logging error: {e}", file=sys.stderr)

    def _severity_to_logging_level(self, severity: SDKSeverity) -> int:
        """Convert SDK severity to Python logging level."""
        mapping = {
            SDKSeverity.TRACE: logging.DEBUG,
            SDKSeverity.DEBUG: logging.DEBUG,
            SDKSeverity.INFO: logging.INFO,
            SDKSeverity.WARNING: logging.WARNING,
            SDKSeverity.ERROR: logging.ERROR,
            SDKSeverity.CRITICAL: logging.CRITICAL,
            SDKSeverity.FATAL: logging.CRITICAL,
        }
        return mapping.get(severity, logging.INFO)

    async def _auto_flush_loop(self) -> None:
        """Background task for auto-flushing buffer."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self._flush_interval)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.enable_console:
                    print(f"Auto-flush error: {e}", file=sys.stderr)

    async def _flush_buffer(self) -> None:
        """Flush buffer to WebSocket."""
        if not self._websocket_client or not self.enable_websocket:
            return

        events_to_flush = []
        with self._buffer_lock:
            if self._buffer:
                events_to_flush = self._buffer.copy()
                self._buffer.clear()

        if not events_to_flush:
            return

        try:
            # Send WebSocket events with timeout to prevent blocking
            send_tasks = []
            for event in events_to_flush:
                ws_message = event.to_websocket_message(self.session_id)
                task = asyncio.create_task(self._websocket_client.send_log(ws_message))
                send_tasks.append(task)
            
            # Wait for all sends with timeout to prevent blocking
            if send_tasks:
                await asyncio.wait_for(
                    asyncio.gather(*send_tasks, return_exceptions=True),
                    timeout=2.0  # 2 second timeout for all sends
                )

            if self.enable_console and len(events_to_flush) > 1:
                self.console_logger.debug(f"Flushed {len(events_to_flush)} events to WebSocket")

        except asyncio.TimeoutError:
            if self.enable_console:
                self.console_logger.warning(f"WebSocket flush timeout - sent {len(events_to_flush)} events")
        except Exception as e:
            if self.enable_console:
                self.console_logger.error(f"Failed to flush events to WebSocket: {e}")

    # Statistics and Monitoring
    def get_statistics(self) -> DevelopmentLoggerStatistics:
        """Get development logger statistics."""
        return DevelopmentLoggerStatistics(
            total_events=self._events_logged,
            events_by_type=dict(self._events_by_type),
            events_by_severity=dict(self._events_by_severity),
            buffer_size=len(self._buffer),
            websocket_connected=self.enable_websocket and self.websocket_client is not None,
            startup_time=getattr(self, "_startup_time", datetime.now(timezone.utc)),
        )

    def get_active_operations(self) -> Dict[str, float]:
        """Get currently active operations with durations."""
        now = datetime.now(timezone.utc)
        return {
            op_id: (now - start_time).total_seconds()
            for op_id, start_time in self._active_operations.items()
        }


# Global development logger instance
_dev_logger: Optional[DevelopmentLogger] = None


def initialize_development_logger(
    session_id: Optional[str] = None,
    log_level: SDKSeverity = SDKSeverity.INFO,
    enable_console: bool = True,
    enable_websocket: bool = True,
) -> DevelopmentLogger:
    """Initialize global development logger."""
    global _dev_logger
    _dev_logger = DevelopmentLogger(
        session_id=session_id,
        log_level=log_level,
        enable_console=enable_console,
        enable_websocket=enable_websocket,
    )
    return _dev_logger


def get_development_logger() -> Optional[DevelopmentLogger]:
    """Get global development logger instance."""
    return _dev_logger


# Convenience decorator for automatic operation tracking
def track_development_operation(
    operation_name: str, event_type: SDKEventType = SDKEventType.DEBUG_CHECKPOINT
):
    """Decorator to automatically track development operations."""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            dev_logger = get_development_logger()
            if not dev_logger:
                return await func(*args, **kwargs)

            operation_id = generate_correlation_id()
            dev_logger.start_operation(operation_id, f"{operation_name}: {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                dev_logger.complete_operation(
                    operation_id, f"{operation_name}: {func.__name__}", success=True
                )
                return result
            except Exception as e:
                dev_logger.complete_operation(
                    operation_id, f"{operation_name}: {func.__name__}", success=False
                )
                dev_logger.log_error(
                    event_type,
                    f"Operation failed: {operation_name}",
                    exception=e,
                    context=SDKContext(method_name=func.__name__),
                )
                raise

        def sync_wrapper(*args, **kwargs):
            dev_logger = get_development_logger()
            if not dev_logger:
                return func(*args, **kwargs)

            operation_id = generate_correlation_id()
            dev_logger.start_operation(operation_id, f"{operation_name}: {func.__name__}")

            try:
                result = func(*args, **kwargs)
                dev_logger.complete_operation(
                    operation_id, f"{operation_name}: {func.__name__}", success=True
                )
                return result
            except Exception as e:
                dev_logger.complete_operation(
                    operation_id, f"{operation_name}: {func.__name__}", success=False
                )
                dev_logger.log_error(
                    event_type,
                    f"Operation failed: {operation_name}",
                    exception=e,
                    context=SDKContext(method_name=func.__name__),
                )
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
