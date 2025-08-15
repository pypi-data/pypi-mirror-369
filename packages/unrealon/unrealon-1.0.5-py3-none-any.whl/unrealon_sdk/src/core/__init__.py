"""
Core SDK components for UnrealOn SDK v1.0

This module contains the essential SDK functionality:
- Types and data structures
- Exception hierarchy  
- Configuration management
- Core models
"""

from .types import ConnectionState
from .models import ConnectionHealthStatus, ComponentStatus
from .metadata import (
    SDKMetadata,
    RegistrationMetadata,
    CommandExecutionMetadata,
    LoggingContextMetadata,
    EnvironmentMetadata,
    ProxyOperationMetadata,
)
from .exceptions import (
    UnrealOnError,
    ConnectionError,
    AuthenticationError,
    ConfigurationError,
    CommandError,
    ProxyError,
    TimeoutError,
    ValidationError,
    RegistrationError,
    WebSocketError,
    MonitoringError,
    LoggingError,
    RateLimitError,
)

__all__ = [
    # Types
    "ConnectionState",
    # Models  
    "ConnectionHealthStatus",
    "ComponentStatus",
    # Metadata
    "SDKMetadata",
    "RegistrationMetadata",
    "CommandExecutionMetadata", 
    "LoggingContextMetadata",
    "EnvironmentMetadata",
    "ProxyOperationMetadata",
    # Exceptions
    "UnrealOnError",
    "ConnectionError",
    "AuthenticationError",
    "ConfigurationError",
    "CommandError",
    "ProxyError",
    "TimeoutError",
    "ValidationError",
    "RegistrationError",
    "WebSocketError",
    "MonitoringError",
    "LoggingError",
    "RateLimitError",
]
