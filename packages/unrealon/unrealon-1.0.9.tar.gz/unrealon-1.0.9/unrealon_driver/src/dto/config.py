"""
Configuration models for UnrealOn Driver v3.0

Pydantic v2 models for type-safe configuration.
"""

from enum import Enum


class LogLevel(str, Enum):
    """Logging levels enumeration."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
