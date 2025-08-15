"""
Driver Logger v3.0 - Specialized logging for UnrealOn Driver

Wraps the SDK DevelopmentLogger with Driver-specific convenience methods.
Provides structured logging for browser automation, data extraction, and system monitoring.
Following zero-configuration philosophy of Driver v3.0.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from unrealon_sdk.src.enterprise.logging.development import (
    DevelopmentLogger,
    initialize_development_logger,
    get_development_logger,
)
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity, SDKContext
from unrealon_driver.src.dto.events import DriverEventType


# Global driver logger instance for zero-configuration
_driver_logger: Optional["DriverLogger"] = None


def initialize_driver_logger(
    parser_id: str = "unknown",
    parser_name: str = "UnrealOn Parser",
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_websocket: bool = False,
    system_dir: Optional[str] = None,
) -> "DriverLogger":
    """
    Initialize the global driver logger with zero configuration.

    Args:
        parser_id: Unique parser identifier
        parser_name: Human-readable parser name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Enable console output
        enable_websocket: Enable WebSocket streaming

    Returns:
        Configured DriverLogger instance
    """
    global _driver_logger

    # Map string log levels to SDK severity
    level_map = {
        "TRACE": SDKSeverity.TRACE,
        "DEBUG": SDKSeverity.DEBUG,
        "INFO": SDKSeverity.INFO,
        "WARNING": SDKSeverity.WARNING,
        "ERROR": SDKSeverity.ERROR,
        "CRITICAL": SDKSeverity.CRITICAL,
    }

    sdk_level = level_map.get(log_level.upper(), SDKSeverity.INFO)

    # Use SDK logger with correct parameters
    dev_logger = initialize_development_logger(
        session_id=f"{parser_id}_session",
        log_level=sdk_level,
        enable_console=enable_console,
        enable_websocket=enable_websocket,
    )

    # Set layer context for Driver
    dev_logger.set_layer_context("UnrealOn_Driver")
    
    # 🔥 ADD FILE LOGGING SUPPORT
    file_logger = None
    if system_dir:
        log_file_path = Path(system_dir) / "logs" / "parser.log"
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create standard Python file logger
        file_logger = logging.getLogger(f"driver_file_{parser_id}")
        file_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Remove existing handlers to avoid duplicates
        for handler in file_logger.handlers[:]:
            file_logger.removeHandler(handler)
            
        # Add file handler
        file_handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter(
            '%(asctime)s | DRIVER | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        file_logger.addHandler(file_handler)
        file_logger.propagate = False  # Prevent double logging

    _driver_logger = DriverLogger(dev_logger, parser_id, parser_name, file_logger)
    return _driver_logger


def get_driver_logger() -> Optional["DriverLogger"]:
    """Get the global driver logger instance."""
    return _driver_logger


def ensure_driver_logger(
    parser_id: str = "default", 
    parser_name: str = "UnrealOn Parser",
    system_dir: Optional[str] = None,
) -> "DriverLogger":
    """
    Ensure driver logger exists, create if needed (zero-configuration).

    Args:
        parser_id: Fallback parser ID if none exists
        parser_name: Fallback parser name if none exists

    Returns:
        DriverLogger instance
    """
    global _driver_logger
    if not _driver_logger:
        _driver_logger = initialize_driver_logger(
            parser_id=parser_id, parser_name=parser_name, system_dir=system_dir
        )
    return _driver_logger


class DriverLogger:
    """
    Specialized logger for Driver v3.0 operations.

    Zero-configuration logging with enterprise features:
    - Browser automation events
    - Data extraction operations
    - Service lifecycle tracking
    - Performance metrics
    - Real-time WebSocket streaming (optional)
    - Structured logging with Pydantic v2
    """

    def __init__(
        self,
        dev_logger: DevelopmentLogger,
        parser_id: str = "unknown",
        parser_name: str = "UnrealOn Parser",
        file_logger: Optional[logging.Logger] = None,
    ):
        """Initialize driver logger with SDK development logger and optional file logger."""
        self._dev_logger = dev_logger
        self._file_logger = file_logger
        self.parser_id = parser_id
        self.parser_name = parser_name

        # Set component context
        self._dev_logger.set_component_context(f"Parser[{parser_id}]")

        # Log initialization
        self.info(f"🚀 DriverLogger initialized: {parser_name}")

    # ==========================================
    # BASIC LOGGING METHODS
    # ==========================================

    def debug(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self._dev_logger.log_debug(
            SDKEventType.COMPONENT_TESTED,
            message,
            context=self._create_context(details),
        )
        # 🔥 Also log to file if file logger exists
        if self._file_logger:
            self._file_logger.debug(message)

    def info(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self._dev_logger.log_info(
            SDKEventType.COMMAND_COMPLETED,
            message,
            context=self._create_context(details),
        )
        # 🔥 Also log to file if file logger exists
        if self._file_logger:
            self._file_logger.info(message)

    def warning(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self._dev_logger.log_warning(
            SDKEventType.PERFORMANCE_THRESHOLD_EXCEEDED,
            message,
            context=self._create_context(details),
        )
        # 🔥 Also log to file if file logger exists
        if self._file_logger:
            self._file_logger.warning(message)

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log error message with optional exception."""
        context = self._create_context(details)
        if error:
            context.metadata["error_type"] = type(error).__name__
            context.metadata["error_message"] = str(error)

        self._dev_logger.log_error(
            SDKEventType.COMMAND_FAILED, message, context=context
        )
        # 🔥 Also log to file if file logger exists
        if self._file_logger:
            error_msg = f"{message} - {error}" if error else message
            self._file_logger.error(error_msg)

    def critical(
        self,
        message: str,
        error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log critical message."""
        context = self._create_context(details)
        if error:
            context.metadata["error_type"] = type(error).__name__
            context.metadata["error_message"] = str(error)

        self._dev_logger.log_critical(SDKEventType.SDK_ERROR, message, context=context)

    # ==========================================
    # DRIVER-SPECIFIC LOGGING METHODS
    # ==========================================

    def log_parser_start(
        self, mode: str = "test", details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log parser execution start."""
        context = self._create_context(details)
        context.metadata["execution_mode"] = mode
        context.metadata["parser_name"] = self.parser_name

        self._dev_logger.log_info(
            SDKEventType.COMMAND_RECEIVED,
            f"🎯 Parser started in {mode} mode",
            context=context,
        )

    def log_parser_success(
        self,
        result_count: int = 0,
        duration: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log successful parser completion."""
        context = self._create_context(details)
        context.metadata["result_count"] = result_count
        if duration:
            context.metadata["duration_seconds"] = duration

        self._dev_logger.log_info(
            SDKEventType.COMMAND_COMPLETED,
            f"✅ Parser completed successfully - {result_count} items processed",
            context=context,
        )

    def log_parser_error(
        self, error: Exception, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log parser execution error."""
        context = self._create_context(details)
        context.metadata["error_type"] = type(error).__name__
        context.metadata["error_message"] = str(error)

        self._dev_logger.log_error(
            SDKEventType.COMMAND_FAILED,
            f"❌ Parser execution failed: {error}",
            context=context,
        )

    def log_browser_operation(
        self,
        operation: str,
        url: str = "",
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log browser automation operation."""
        context = self._create_context(details)
        context.metadata["operation"] = operation
        context.metadata["url"] = url
        context.metadata["success"] = success

        status = "✅" if success else "❌"
        message = f"{status} Browser {operation}"
        if url:
            message += f" - {url}"

        event_type = (
            SDKEventType.COMMAND_COMPLETED if success else SDKEventType.COMMAND_FAILED
        )

        if success:
            self._dev_logger.log_info(event_type, message, context=context)
        else:
            self._dev_logger.log_error(event_type, message, context=context)

    def log_data_extraction(
        self,
        selector: str,
        items_count: int,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log data extraction operation."""
        context = self._create_context(details)
        context.metadata["selector"] = selector
        context.metadata["items_extracted"] = items_count
        context.metadata["success"] = success

        status = "✅" if success else "❌"
        message = f"{status} Data extraction - {items_count} items from '{selector}'"

        event_type = (
            SDKEventType.COMMAND_COMPLETED if success else SDKEventType.COMMAND_FAILED
        )

        if success:
            self._dev_logger.log_info(event_type, message, context=context)
        else:
            self._dev_logger.log_error(event_type, message, context=context)

    def log_service_operation(
        self,
        service_name: str,
        operation: str,
        success: bool = True,
        duration: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log service operation (browser, llm, websocket, etc.)."""
        context = self._create_context(details)
        context.metadata["service"] = service_name
        context.metadata["operation"] = operation
        context.metadata["success"] = success
        if duration:
            context.metadata["duration_seconds"] = duration

        status = "✅" if success else "❌"
        message = f"{status} {service_name.title()} {operation}"
        if duration:
            message += f" ({duration:.3f}s)"

        event_type = (
            SDKEventType.COMMAND_COMPLETED if success else SDKEventType.COMMAND_FAILED
        )

        if success:
            self._dev_logger.log_info(event_type, message, context=context)
        else:
            self._dev_logger.log_error(event_type, message, context=context)

    def log_llm_operation(
        self,
        operation: str,
        tokens: int = 0,
        cost: float = 0.0,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log LLM operation with cost tracking."""
        context = self._create_context(details)
        context.metadata["llm_operation"] = operation
        context.metadata["tokens_used"] = tokens
        context.metadata["cost_usd"] = cost
        context.metadata["success"] = success

        status = "✅" if success else "❌"
        message = f"{status} LLM {operation}"
        if tokens > 0:
            message += f" - {tokens} tokens"
        if cost > 0:
            message += f" (${cost:.4f})"

        event_type = (
            SDKEventType.COMMAND_COMPLETED if success else SDKEventType.COMMAND_FAILED
        )

        if success:
            self._dev_logger.log_info(event_type, message, context=context)
        else:
            self._dev_logger.log_error(event_type, message, context=context)

    # ==========================================
    # PERFORMANCE & METRICS
    # ==========================================

    def start_operation(self, operation_name: str, description: str = "") -> str:
        """Start tracking operation performance."""
        import time
        import uuid
        
        # Generate operation ID and store start time
        operation_id = f"{operation_name}_{uuid.uuid4().hex[:8]}"
        if not hasattr(self, '_operation_times'):
            self._operation_times = {}
        self._operation_times[operation_id] = time.time()
        
        # Start operation in SDK logger
        desc = description or f"Starting {operation_name} operation"
        self._dev_logger.start_operation(operation_id, desc)
        
        return operation_id

    def end_operation(
        self,
        operation_id: str,
        success: bool = True,
        result_data: Optional[Dict[str, Any]] = None,
    ) -> float:
        """End operation tracking and return duration."""
        import time
        # Calculate duration manually since complete_operation returns None
        if operation_id in getattr(self, '_operation_times', {}):
            start_time = self._operation_times.pop(operation_id)
            duration = time.time() - start_time
        else:
            duration = 0.0
            
        # Complete the operation in SDK logger
        description = f"Operation {operation_id} {'completed' if success else 'failed'}"
        self._dev_logger.complete_operation(operation_id, description, success)
        
        return duration

    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log performance metric."""
        context = self._create_context(details)
        context.metadata["metric_name"] = metric_name
        context.metadata["metric_value"] = value
        context.metadata["metric_unit"] = unit

        message = f"📊 {metric_name}: {value}"
        if unit:
            message += f" {unit}"

        self._dev_logger.log_info(
            SDKEventType.PERFORMANCE_METRIC_COLLECTED, message, context=context
        )

    # ==========================================
    # CONTEXT & UTILITIES
    # ==========================================

    def _create_context(self, details: Optional[Dict[str, Any]] = None) -> SDKContext:
        """Create SDK context for logging."""
        metadata = {
            "parser_id": self.parser_id,
            "parser_name": self.parser_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if details:
            metadata.update(details)

        return SDKContext(
            parser_id=self.parser_id,
            component_name=f"Parser[{self.parser_id}]",
            layer_name="UnrealOn_Driver",
            metadata=metadata,
        )

    def set_parser_context(self, parser_id: str, parser_name: str) -> None:
        """Update parser context."""
        self.parser_id = parser_id
        self.parser_name = parser_name
        self._dev_logger.set_component_context(f"Parser[{parser_id}]")

    def health_check(self) -> Dict[str, Any]:
        """Check logger health."""
        return {
            "status": "healthy" if self._dev_logger else "unhealthy",
            "parser_id": self.parser_id,
            "parser_name": self.parser_name,
            "session_id": self._dev_logger.session_id if self._dev_logger else None,
            "log_level": self._dev_logger.log_level.value if self._dev_logger else None,
            "console_enabled": (
                self._dev_logger.enable_console if self._dev_logger else False
            ),
            "websocket_enabled": (
                self._dev_logger.enable_websocket if self._dev_logger else False
            ),
        }

    async def cleanup(self) -> None:
        """Clean up logger resources."""
        if self._dev_logger:
            await self._dev_logger.shutdown()
            # Note: Don't log after shutdown
            self.info("🏁 DriverLogger cleanup completed")

    def __repr__(self) -> str:
        return f"<DriverLogger(parser_id={self.parser_id}, parser_name={self.parser_name})>"
