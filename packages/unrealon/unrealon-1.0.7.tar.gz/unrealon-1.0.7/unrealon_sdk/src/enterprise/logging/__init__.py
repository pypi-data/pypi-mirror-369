"""
Enterprise Logging Package for UnrealOn SDK

Centralized logging infrastructure following enterprise standards:
- Type-safe structured logging with Pydantic v2
- Real-time log streaming via WebSocket
- Development process tracking and debugging
- Automatic log cleanup and rotation
- Performance monitoring and analytics

Modules:
- service: Enterprise-grade structured logging service
- development: Development process logging and tracking
- cleanup: Automatic log file cleanup utilities

Following KISS methodology and 100% compliance with enterprise requirements.
"""

# Import all logging components for easy access
from .service import (
    LoggingService,
    StructuredLogger,
    LogLevel,
    LogEntryMessage,
    LogBuffer,
    LogDestination,
    get_logger,
)

from .development import (
    DevelopmentLogger,
    SDKEventType,
    SDKSeverity,
    SDKContext,
    SDKDevelopmentEvent,
)

from .cleanup import (
    clear_old_sdk_logs,
    clear_development_logs,
    setup_sdk_logging_with_cleanup,
)

# Centralized exports following enterprise standards
__all__ = [
    # Core logging service
    "LoggingService",
    "StructuredLogger",
    "get_logger",
    
    # Data models
    "LogLevel",
    "LogEntryMessage",
    "LogBuffer",
    "LogDestination",
    
    # Development logging
    "DevelopmentLogger",
    "SDKEventType",
    "SDKSeverity",
    "SDKContext",
    "SDKDevelopmentEvent",
    
    # Cleanup utilities
    "clear_old_sdk_logs",
    "clear_development_logs",
    "setup_sdk_logging_with_cleanup",
]
