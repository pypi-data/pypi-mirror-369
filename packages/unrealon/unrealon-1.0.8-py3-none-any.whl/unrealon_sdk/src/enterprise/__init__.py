"""
UnrealOn SDK Enterprise Services

Layer 3: Infrastructure Services - Core enterprise-grade components
providing intelligent proxy management, structured logging, performance
monitoring, and error recovery capabilities.

Enterprise Features:
- Intelligent proxy rotation with geographic awareness
- Real-time structured logging via WebSocket
- Performance metrics collection and analysis
- Automatic error recovery and circuit breakers
- Health monitoring and alerting
- Intelligent caching with TTL management

Quick Start:
```python
from unrealon_sdk import AdapterClient, AdapterConfig
from unrealon_sdk.src.enterprise import ProxyManager, LoggingService, MonitoringManager

config = AdapterConfig(api_key="up_dev_your_api_key")
adapter = AdapterClient(config)

# Enterprise services are automatically initialized
# Just use the adapter client normally!
```

These services power the enterprise-grade capabilities of the UnrealOn SDK.
"""

from .proxy_manager import ProxyManager
from .logging.service import LoggingService
from .logging.development import (
    DevelopmentLogger,
    initialize_development_logger,
    get_development_logger,
    track_development_operation,
    SDKEventType,
    SDKSeverity,
    SDKContext,
)

# These will be implemented next
# from .monitoring_manager import MonitoringManager
# from .error_recovery import ErrorRecoveryManager

__all__ = [
    "ProxyManager",
    "LoggingService",
    "DevelopmentLogger",
    "initialize_development_logger",
    "get_development_logger",
    "track_development_operation",
    "SDKEventType",
    "SDKSeverity",
    "SDKContext",
    # "MonitoringManager",
    # "ErrorRecoveryManager",
]
