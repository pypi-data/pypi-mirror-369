"""
UnrealOn SDK v1.0 - Enterprise Parsing Platform

The most advanced SDK for building enterprise-grade parsing solutions with:
- 90% code reduction through intelligent automation
- Type-safe operations with auto-generated models  
- Production-ready features out of the box
- Real-time communication and monitoring

Quick Start:
```python
from unrealon_sdk import AdapterClient, AdapterConfig

config = AdapterConfig(api_key="up_dev_your_api_key")
adapter = AdapterClient(config)

@adapter.on_command("parse_data")
async def handle_parsing(command):
    return {"status": "success", "data": parsed_data}
```

For complete documentation: https://docs.unrealon.com
"""

# Core client classes - main public API
from .core.client import AdapterClient
from .core.config import AdapterConfig

# Core types and exceptions
from .core.types import ConnectionState
from .core.models import ConnectionHealthStatus
from .core.exceptions import (
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

# Auto-generated client models - all API types come from here!
from .clients.python_http.models import (
    ParserType,
    LogLevel,
    ServiceRegistrationDto,
    ParserRegistrationRequest,
    ParserRegistrationResponse,
    SuccessResponse,
    ErrorResponse,
    HealthResponse,
    LoggingRequest,
    LoggingResponse,
    ParserCommandRequest,
)

# Auto-generated WebSocket models
from .clients.python_websocket.types import (
    ParserCommandEvent,
    CommandStatus,
    CommandType,
    CommandPriority,
    ParserStatus,
    ProcessingPhase,
)

# WebSocket events from events.py
from .clients.python_websocket.events import (
    SocketEvent,
)

# Utility functions and helpers
from .utils import (
    validate_api_key,
    extract_domain,
    calculate_success_rate,
    format_duration,
)

# Public API exports
__all__ = [
    # Core classes
    "AdapterClient",
    "AdapterConfig",
    # Exception hierarchy
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
    # Core SDK types (minimal)
    "ConnectionState",
    "ConnectionHealthStatus",
    # Auto-generated HTTP models
    "ParserType",
    "LogLevel",
    "ServiceRegistrationDto",
    "ParserRegistrationRequest",
    "ParserRegistrationResponse",
    "SuccessResponse",
    "ErrorResponse",
    "HealthResponse",
    "LoggingRequest",
    "LoggingResponse",
    "ParserCommandRequest",
    # Auto-generated WebSocket models
    "ParserCommandEvent",
    "CommandStatus",
    "CommandType",
    "CommandPriority",
    "ParserStatus",
    "ProcessingPhase",
    "SocketEvent",
    # Utilities
    "validate_api_key",
    "extract_domain",
    "calculate_success_rate",
    "format_duration",
]

# Compatibility and feature detection
FEATURES = {
    "auto_generated_models": True,
    "real_time_websocket": True,
    "intelligent_proxy_rotation": True,
    "multi_destination_logging": True,
    "enterprise_monitoring": True,
    "production_error_handling": True,
    "type_safe_operations": True,
    "minimal_configuration": True,
}


def get_features() -> dict:
    """Get available SDK features."""
    return FEATURES.copy()
