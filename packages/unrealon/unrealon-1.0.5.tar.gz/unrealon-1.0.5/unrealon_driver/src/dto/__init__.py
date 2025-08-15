"""
Data Transfer Objects for UnrealOn Driver v3.0

Type-safe configuration and data models using Pydantic v2.
COMPLIANCE: 100% Pydantic v2 compliant.
"""

from .cli import ParserInstanceConfig, create_parser_config
from .config import LogLevel
from .execution import (
    ParserTestConfig,
    DaemonModeConfig,
    ScheduledModeConfig,
    InteractiveModeConfig,
    ExecutionResult,
    ErrorInfo,
    PerformanceMetrics,
    ExecutionEnvironment,
    ScheduledModeStatus,
    DaemonCommandResult,
    DaemonStatusResult,
    DaemonHealthResult,
)
from .events import (
    DriverEventType,
    DriverEventContext,
    DriverEventMetrics,
    BROWSER_EVENTS,
    PARSER_EVENTS,
    LLM_EVENTS,
    SCHEDULER_EVENTS,
    WEBSOCKET_EVENTS,
    METRICS_EVENTS,
    ERROR_EVENTS,
)

__all__ = [
    "ParserInstanceConfig",
    "create_parser_config",
    "LogLevel",
    # Execution models
    "ParserTestConfig",
    "DaemonModeConfig",
    "ScheduledModeConfig",
    "InteractiveModeConfig",
    "ExecutionResult",
    "ErrorInfo",
    "PerformanceMetrics",
    "ExecutionEnvironment",
    # Daemon models
    "ScheduledModeStatus",
    "DaemonCommandResult",
    "DaemonStatusResult",
    "DaemonHealthResult",
    # Event models
    "DriverEventType",
    "DriverEventContext",
    "DriverEventMetrics",
    "BROWSER_EVENTS",
    "PARSER_EVENTS", 
    "LLM_EVENTS",
    "SCHEDULER_EVENTS",
    "WEBSOCKET_EVENTS",
    "METRICS_EVENTS",
    "ERROR_EVENTS",
]
