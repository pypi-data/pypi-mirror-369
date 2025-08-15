"""
LoggingService - Structured Real-time Logging for Enterprise Parsing

Layer 3: Infrastructure Services - Enterprise logging with:
- Real-time log streaming via WebSocket
- Structured metadata with Pydantic v2 models
- Automatic buffering and batch processing
- Multiple destination support (local, WebSocket, external)
- Type-safe operations and correlation tracking

Enterprise Features:
- WebSocket-based real-time log streaming
- Structured metadata with full type safety
- Automatic buffering for performance
- Correlation tracking across requests
- Integration with external logging systems
- Performance metrics and log analytics
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import List, Optional, Any, Union, Callable, Dict
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import deque
import threading

# Pydantic v2 for all data models
from pydantic import BaseModel, Field, ConfigDict

# Auto-generated models - use LogLevel from HTTP models (standard enum)
from unrealon_sdk.src.clients.python_http.models import LogLevel, LoggingRequest

# Auto-generated WebSocket models - main models for logging
from unrealon_sdk.src.clients.python_websocket.types import LogEntryMessage

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig, LoggingConfig
from unrealon_sdk.src.core.exceptions import LoggingError
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models for structured logging
from unrealon_sdk.src.dto.logging import LogDestination
from unrealon_sdk.src.dto.structured_logging import LogBuffer

# Development logging (avoid circular import)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .development_logger import DevelopmentLogger

# SDK metadata models
from unrealon_sdk.src.core.metadata import LoggingServiceStatistics

logger = logging.getLogger(__name__)


# Use auto-generated LogEntryMessage directly for WebSocket logging
# All structured data goes into the entry field using flexible types


class StructuredLogger:
    """
    Type-safe structured logger using auto-generated LogEntryMessage.

    Provides a familiar logging interface while ensuring all
    log entries use the official WebSocket message format.
    """

    def __init__(self, name: str, service: "LoggingService"):
        self.name = name
        self.service = service
        self._default_context: Dict[str, Any] = {}

    def with_context(self, **context: Any) -> "StructuredLogger":
        """Create logger with additional context metadata."""
        new_logger = StructuredLogger(self.name, self.service)
        new_logger._default_context = {**self._default_context, **context}
        return new_logger

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with structured context."""
        self._log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context: Any) -> None:
        """Log info message with structured context."""
        self._log(LogLevel.INFO, message, **context)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with structured context."""
        self._log(LogLevel.WARNING, message, **context)

    def error(self, message: str, **context: Any) -> None:
        """Log error message with structured context."""
        self._log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message with structured context."""
        self._log(LogLevel.CRITICAL, message, **context)

    def _log(self, level: LogLevel, message: str, **context: Any) -> None:
        """Internal logging method using auto-generated LogEntryMessage."""
        now = datetime.now(timezone.utc)

        # Combine default context with provided context
        combined_context = {
            **self._default_context,
            **context,
            # Add runtime info
            "logger_name": self.name,
            "thread_id": str(threading.get_ident()),
            "level": level.value,
            "correlation_id": generate_correlation_id(),
        }

        # Create LogEntryMessage using the auto-generated model
        entry = LogEntryMessage(
            type="log_entry",
            session_id=self.service._session_id,
            entry=combined_context,  # All structured data goes here
            timestamp=now.isoformat(),
        )

        # Add the actual log message to entry data
        entry.entry["message"] = message
        entry.entry["timestamp"] = now.isoformat()

        self.service.log_entry(entry)


class LoggingService:
    """
    Enterprise-grade structured logging service.

    Features:
    - Real-time WebSocket log streaming
    - Structured metadata with type safety
    - Automatic buffering and batching
    - Multiple destination support
    - Correlation tracking
    - Performance monitoring
    """

    def __init__(self, config: AdapterConfig):
        """
        Initialize LoggingService with configuration.

        Args:
            config: Adapter configuration containing logging settings
        """
        self.config = config
        self.logging_config = config.logging_config or LoggingConfig()
        self.logger = logger

        # Session management for WebSocket logging
        self._session_id = generate_correlation_id()

        # WebSocket client for real-time streaming (will be injected)
        self._websocket_client = None

        # Buffering for performance
        self._buffer = LogBuffer(
            max_size=self.logging_config.buffer_size,
            flush_interval_seconds=self.logging_config.flush_interval_seconds,
        )
        self._buffer.flush_callback = self._flush_entries

        # Structured loggers registry
        self._loggers: Dict[str, StructuredLogger] = {}

        # Statistics
        self._total_logs = 0
        self._logs_by_level = {level: 0 for level in LogLevel}
        self._websocket_errors = 0

        # Background tasks
        self._initialized = False

        current_level = self.logging_config.level or self.logging_config.log_level
        self.logger.info(f"LoggingService initialized with level: {current_level}")

    async def initialize(self, websocket_client: Any) -> None:
        """Initialize logging service with WebSocket client."""
        self._websocket_client = websocket_client

        if self.logging_config.enabled:
            await self._buffer.start_auto_flush()

        self._initialized = True
        self.logger.info("LoggingService initialization complete")

    async def shutdown(self) -> None:
        """Shutdown logging service and flush remaining logs."""
        await self._buffer.stop_auto_flush()
        self._initialized = False
        self.logger.info("LoggingService shutdown complete")

    def get_logger(self, name: str) -> StructuredLogger:
        """
        Get or create a structured logger.

        Args:
            name: Logger name

        Returns:
            StructuredLogger instance
        """
        if name not in self._loggers:
            self._loggers[name] = StructuredLogger(name, self)

        return self._loggers[name]

    def log_entry(self, entry: LogEntryMessage) -> None:
        """
        Log a structured entry using auto-generated LogEntryMessage.

        Args:
            entry: LogEntryMessage to process
        """
        if not self.logging_config.enabled:
            return

        # Extract log level from entry data for filtering
        log_level_str = entry.entry.get("level", "info")
        try:
            entry_level = LogLevel(log_level_str)
        except ValueError:
            entry_level = LogLevel.INFO  # Default fallback

        # Check log level filtering
        current_level = self.logging_config.level or self.logging_config.log_level
        current_level_value = self._get_level_value(current_level)
        entry_level_value = self._get_level_value(entry_level)

        if entry_level_value < current_level_value:
            return  # Skip logs below configured level

        # Update statistics
        self._total_logs += 1
        self._logs_by_level[entry_level] += 1

        # Add to buffer for processing
        self._buffer.add_entry(entry)

        # Also send to console if configured
        if LogDestination.CONSOLE in self.logging_config.destinations:
            self._log_to_console(entry)

    def _get_level_value(self, level: LogLevel) -> int:
        """Get numeric value for log level comparison."""
        level_values = {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
            LogLevel.CRITICAL: 50,
        }
        return level_values.get(level, 0)

    def _log_to_console(self, entry: LogEntryMessage) -> None:
        """Log entry to console using standard logging."""
        # Extract log level from entry data
        level_str = entry.entry.get("level", "info")
        try:
            log_level = LogLevel(level_str)
        except ValueError:
            log_level = LogLevel.INFO

        python_level = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }.get(log_level, logging.INFO)

        # Extract message and metadata from entry
        message = entry.entry.get("message", "")
        correlation_id = entry.entry.get("correlation_id", "")
        parser_id = entry.entry.get("parser_id", "")

        # Format message with key metadata
        metadata_str = ""
        if correlation_id:
            metadata_str += f" [corr_id={correlation_id[:8]}]"
        if parser_id:
            metadata_str += f" [parser={parser_id}]"

        formatted_message = f"{message}{metadata_str}"
        self.logger.log(python_level, formatted_message)

    async def _flush_entries(self, entries: List[LogEntryMessage]) -> None:
        """Flush buffered entries to configured destinations."""
        if not entries:
            return

        # Send to WebSocket if enabled and connected
        if (
            LogDestination.WEBSOCKET in self.logging_config.destinations
            and self._websocket_client
            and self._websocket_client.is_connected()
        ):

            await self._send_to_websocket(entries)

        # Send to other destinations (file, HTTP, etc.)
        # Implementation would depend on configuration

    async def _send_to_websocket(self, entries: List[LogEntryMessage]) -> None:
        """Send log entries to WebSocket with timeout to prevent blocking."""
        try:
            # Send entries concurrently with timeout
            send_tasks = [
                asyncio.create_task(self._websocket_client.send_log(entry))
                for entry in entries
            ]
            
            if send_tasks:
                await asyncio.wait_for(
                    asyncio.gather(*send_tasks, return_exceptions=True),
                    timeout=3.0  # 3 second timeout for all sends
                )

            self.logger.debug(f"Sent {len(entries)} log entries via WebSocket")

        except asyncio.TimeoutError:
            self._websocket_errors += len(entries)
            self.logger.warning(f"WebSocket send timeout - attempted {len(entries)} entries")
        except Exception as e:
            self._websocket_errors += 1
            self.logger.error(f"Failed to send logs via WebSocket: {e}")

    def get_statistics(self) -> LoggingServiceStatistics:
        """Get comprehensive logging statistics."""
        return LoggingServiceStatistics(
            total_logs=self._total_logs,
            logs_by_level={level.value: count for level, count in self._logs_by_level.items()},
            websocket_logs=self._total_logs - self._websocket_errors,
            buffer_size=len(self._buffer.entries),
            failed_sends=self._websocket_errors,
            last_flush=getattr(self, "_last_flush", datetime.now(timezone.utc)),
        )

    async def test_connectivity(self) -> bool:
        """Test WebSocket connectivity for logging."""
        if not self._websocket_client:
            return False

        try:
            test_entry = LogEntryMessage(
                type="log_entry",
                session_id=self._session_id,
                entry={
                    "level": LogLevel.DEBUG.value,
                    "message": "Connectivity test from LoggingService",
                    "correlation_id": generate_correlation_id(),
                    "test": True,
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            await self._websocket_client.send_log(test_entry)
            return True

        except Exception as e:
            self.logger.error(f"Logging connectivity test failed: {e}")
            return False


# Convenience function for getting loggers
def get_logger(
    name: str, service: Optional[LoggingService] = None
) -> Union[StructuredLogger, logging.Logger]:
    """
    Get a structured logger if service is available, otherwise fallback to standard logger.
    
    Automatically performs log cleanup on first call to ensure clean logging environment.

    Args:
        name: Logger name
        service: LoggingService instance, optional

    Returns:
        StructuredLogger if service provided, otherwise standard Logger
    """
    if service and service._initialized:
        return service.get_logger(name)
    else:
        # Use standard logger - cleanup handled at module initialization
        return logging.getLogger(name)


# Centralized exports for easy importing
# Import all logging-related models from this module
__all__ = [
    # Core service
    "LoggingService",
    "StructuredLogger",
    "get_logger",
    # Enums and types
    "LogDestination",
    "LogBuffer",
    # Auto-generated models (re-exported for convenience)
    "LogLevel",
    "LoggingRequest",
    "LogEntryMessage",
]
