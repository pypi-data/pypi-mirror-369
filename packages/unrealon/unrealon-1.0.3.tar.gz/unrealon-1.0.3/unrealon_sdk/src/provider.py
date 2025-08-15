"""
🚀 UnrealOn SDK Driver - One-Stop Import for Parser Development

This module provides all necessary imports for developing parsers with the UnrealOn SDK.
Ensures Pydantic v2 compliance and follows REQUIREMENTS_COMPLETE.md standards.

Usage:
    from unrealon_sdk.src.provider import *
    
    # Or use specific groups:
    from unrealon_sdk.src.provider import Core, Enterprise, Models, Browser, Utils
    
    # Quick setup with global API configuration:
    Utils.set_global_api_key("your_api_key_here") 
    config = Utils.create_parser_config("my_parser")
    client = Core.AdapterClient(config)
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum

# =============================================================================
# Core SDK Components
# =============================================================================

# Core client and configuration
from unrealon_sdk.src.core.client import AdapterClient
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.core.exceptions import UnrealOnError, ConnectionError

# =============================================================================
# Enterprise Components
# =============================================================================

# Enterprise services
from unrealon_sdk.src.enterprise.proxy_manager import ProxyManager
from unrealon_sdk.src.enterprise.logging import LoggingService, get_logger
from unrealon_sdk.src.enterprise.performance_monitor import PerformanceMonitor
from unrealon_sdk.src.enterprise.health_monitor import HealthMonitor
from unrealon_sdk.src.enterprise.cache_manager import CacheManager
from unrealon_sdk.src.enterprise.rate_limiter import RateLimiter
from unrealon_sdk.src.enterprise.multithreading_manager import MultithreadingManager
from unrealon_sdk.src.enterprise.task_scheduler import TaskScheduler

# =============================================================================
# SDK Auto-Generated Models (Pydantic v2 Compliant)
# =============================================================================

# WebSocket types and events
from unrealon_sdk.src.clients.python_websocket.types import (
    # Enums
    ParserStatus,
    CommandType,
    CommandStatus,
    CommandPriority,
    ParserType,
    ProcessingPhase,
    ServiceStatus,
    ServiceType,
    ProxyProvider,
    ProxyStatus,
    ProxyProtocol,
    ProxyRotationStrategy,
    # Event Models
    ParserCommandEvent,
    ParserStatusEvent,
    ParserRegisteredEvent,
    ConnectionEvent,
    PongEvent,
    ErrorEvent,
    NotificationEvent,
    SystemEvent,
    # Message Models
    LogEntryMessage,
    CommandMessage,
    CommandCompletionMessage,
    AdminBroadcastMessage,
    MaintenanceNotificationMessage,
    # Connection Models
    ConnectionInfo,
    ConnectionStats,
    HealthStatus,
    WebSocketMetrics,
    # Response Models
    BroadcastResponse,
    ParserMessageResponse,
    DeveloperMessageResponse,
    ConnectionsResponse,
    SystemNotificationResponse,
    # Proxy Models
    Proxy,
    ProxyEndpoint,
    ProxyCredentials,
    ProxyUsageStats,
    ProxyAllocation,
    ProxySummary,
    ProxyDetails,
    ProxyStatistics,
    # Health Models
    ComponentHealth,
    SystemMetrics,
    SystemHealthReport,
    HealthStatsResponse,
    BroadcastDeliveryStats,
    # Metrics Models
    SystemMetricsPoint,
    SystemMetricsResponse,
    SystemMetricsWebSocketEvent,
    UserStatistics,
    SystemStatistics,
    RealTimeMetrics,
)

# HTTP models
from unrealon_sdk.src.clients.python_http.models import (
    SuccessResponse,
    ErrorResponse,
    ValidationErrorResponse,
    ParserRegistrationRequest,
    ParserRegistrationResponse,
    ParserCommandRequest,
    HealthResponse,
    LogLevel,
)

# Global API configuration
from unrealon_sdk.src.clients.python_http.api_config import (
    configure_global_api,
    set_global_api_key,
    set_global_base_url,
    get_global_config,
)

# =============================================================================
# Simple Aliases for Commonly Used Models
# =============================================================================

# Use the existing SDK models - no need for complex docs imports
DocParserCommand = ParserCommandEvent
DocParserResponse = SuccessResponse
DocParserStatus = ParserStatus
DocCommandType = CommandType

# =============================================================================
# Browser Integration (UnrealOn Browser - Always Available)
# =============================================================================

from unrealon_browser.src import (
    BrowserManager,
    BrowserConfig,
    BrowserType,
    BrowserMode,
    CookieManager,
    StealthManager,
    CaptchaDetector,
    CaptchaDetectionResult,
    CaptchaType,
    CaptchaStatus,
    BrowserSession,
    ProxyInfo,
)

# =============================================================================
# Helper Functions for Parser Development
# =============================================================================


def create_parser_config(
    parser_id: str,
    parser_name: str = None,
    api_key: str = None,
    server_url: str = "ws://localhost:8000",
    environment: str = "development",
) -> AdapterConfig:
    """
    Create a properly configured AdapterConfig for parser development.

    Args:
        parser_id: Unique parser identifier
        parser_name: Human-readable parser name (defaults to parser_id)
        api_key: UnrealOn API key (falls back to global config if not provided)
        server_url: WebSocket server URL
        environment: Environment name (development/production)

    Returns:
        Configured AdapterConfig instance

    Example:
        # With global API key set
        Utils.set_global_api_key("up_dev_test_integration_001")
        config = create_parser_config("amazon_scraper")

        # Or with explicit API key
        config = create_parser_config("amazon_scraper", api_key="up_dev_test_integration_001")
    """
    # Use provided api_key or fall back to global configuration
    if api_key is None:
        global_config = get_global_config()
        api_key = global_config.get_access_token()
        if api_key is None:
            api_key = "up_dev_test_integration_001"  # Default fallback

    return AdapterConfig(
        api_key=api_key,
        parser_id=parser_id,
        parser_name=parser_name or parser_id,
        server_url=server_url,
        environment=environment,
        enable_ssl=server_url.startswith("wss://"),
        connection_timeout=30,
        reconnect_attempts=5,
        heartbeat_interval=30,
        # Enable enterprise features
        enable_proxy_rotation=True,
        enable_monitoring=True,
        enable_logging=True,
    )


def create_browser_config(
    parser_name: str,
    browser_type: BrowserType = None,
    # 🔥 stealth_level removed - STEALTH ALWAYS ON!
    headless: bool = True,
) -> BrowserConfig:
    """
    Create a browser configuration for parsing with stealth features.
    🔥 STEALTH ALWAYS ON - NO CONFIG NEEDED!

    Args:
        parser_name: Parser identifier for browser sessions
        browser_type: Browser type (chromium, firefox, webkit)
        headless: Run in headless mode

    Returns:
        Configured BrowserConfig instance with STEALTH ALWAYS ON
    """
    return BrowserConfig(
        parser_name=parser_name,
        browser_type=browser_type or BrowserType.CHROMIUM,
        mode=BrowserMode.HEADLESS if headless else BrowserMode.HEADED,
        # 🔥 STEALTH ALWAYS ON - NO CONFIG NEEDED!
    )


def create_success_response(
    command_id: str, message: str, data: Optional[Dict[str, Any]] = None
) -> SuccessResponse:
    """
    Create a properly typed success response.

    Args:
        command_id: Original command identifier
        message: Success message
        data: Response data (optional)

    Returns:
        SuccessResponse instance
    """
    return SuccessResponse(
        success=True, message=message, data=data, timestamp=datetime.now(timezone.utc).isoformat()
    )


def create_error_response(
    message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    Create a properly typed error response.

    Args:
        message: Error message
        error_code: Error code for programmatic handling
        details: Additional error details

    Returns:
        ErrorResponse instance
    """
    return ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        details=details or {},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def get_system_metrics() -> Dict[str, Any]:
    """
    Get current system metrics for health monitoring.

    Returns:
        Dictionary with system metrics
    """
    try:
        import psutil

        process = psutil.Process()

        return {
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": round(process.cpu_percent(), 2),
            "connections": len(process.connections()),
            "threads": process.num_threads(),
            "uptime_seconds": int(
                (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds()
            ),
        }
    except ImportError:
        return {
            "memory_mb": 0.0,
            "cpu_percent": 0.0,
            "connections": 0,
            "threads": 1,
            "uptime_seconds": 0,
        }


# =============================================================================
# Grouped Imports for Easy Access
# =============================================================================


class Core:
    """Core SDK components."""

    AdapterClient = AdapterClient
    AdapterConfig = AdapterConfig
    UnrealOnError = UnrealOnError
    ConnectionError = ConnectionError


class Enterprise:
    """Enterprise services and managers."""

    ProxyManager = ProxyManager
    LoggingService = LoggingService
    PerformanceMonitor = PerformanceMonitor
    HealthMonitor = HealthMonitor
    CacheManager = CacheManager
    RateLimiter = RateLimiter
    MultithreadingManager = MultithreadingManager
    TaskScheduler = TaskScheduler


class Models:
    """All Pydantic models for events, commands, responses."""

    # Status and Commands
    ParserStatus = ParserStatus
    CommandType = CommandType
    CommandStatus = CommandStatus
    CommandPriority = CommandPriority

    # Events
    ParserCommandEvent = ParserCommandEvent
    ParserStatusEvent = ParserStatusEvent
    ParserRegisteredEvent = ParserRegisteredEvent
    ErrorEvent = ErrorEvent

    # Responses
    SuccessResponse = SuccessResponse
    ErrorResponse = ErrorResponse
    HealthResponse = HealthResponse

    # Registration
    ParserRegistrationRequest = ParserRegistrationRequest
    ParserRegistrationResponse = ParserRegistrationResponse

    # Proxy
    Proxy = Proxy
    ProxyUsageStats = ProxyUsageStats
    ProxyStatistics = ProxyStatistics

    # Health & Metrics
    SystemHealthReport = SystemHealthReport
    RealTimeMetrics = RealTimeMetrics
    SystemMetrics = SystemMetrics


class Browser:
    """Browser automation components."""

    BrowserManager = BrowserManager
    BrowserConfig = BrowserConfig
    BrowserType = BrowserType
    BrowserMode = BrowserMode
    # StealthLevel = StealthLevel 🔥 REMOVED - STEALTH ALWAYS ON!
    CookieManager = CookieManager
    StealthManager = StealthManager
    CaptchaDetector = CaptchaDetector
    CaptchaDetectionResult = CaptchaDetectionResult
    CaptchaType = CaptchaType
    CaptchaStatus = CaptchaStatus
    BrowserSession = BrowserSession
    ProxyInfo = ProxyInfo


class Utils:
    """Utility functions for parser development."""

    create_parser_config = staticmethod(create_parser_config)
    create_browser_config = staticmethod(create_browser_config)
    create_success_response = staticmethod(create_success_response)
    create_error_response = staticmethod(create_error_response)
    get_system_metrics = staticmethod(get_system_metrics)

    # Global API configuration helpers
    set_global_api_key = staticmethod(set_global_api_key)
    set_global_base_url = staticmethod(set_global_base_url)
    configure_global_api = staticmethod(configure_global_api)
    get_global_api_config = staticmethod(get_global_config)

    # Logging helper
    get_logger = staticmethod(get_logger)


# =============================================================================
# Export All for Easy Import
# =============================================================================

__all__ = [
    # Groups
    "Core",
    "Enterprise",
    "Models",
    "Browser",
    "Utils",
    # Individual imports (for backward compatibility)
    "AdapterClient",
    "AdapterConfig",
    "UnrealOnError",
    "ConnectionError",
    "ProxyManager",
    "LoggingService",
    "PerformanceMonitor",
    "HealthMonitor",
    "ParserStatus",
    "CommandType",
    "ParserCommandEvent",
    "ParserStatusEvent",
    "SuccessResponse",
    "ErrorResponse",
    "HealthResponse",
    "ParserRegistrationRequest",
    "ParserRegistrationResponse",
    "create_parser_config",
    "create_browser_config",
    "create_success_response",
    "create_error_response",
    "get_system_metrics",
]

# =============================================================================
# Module Information
# =============================================================================

__version__ = "1.0.0"
__author__ = "UnrealOn SDK Team"
__description__ = "Unified driver for UnrealOn SDK parser development"

# Print status when imported
if __name__ != "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"🚀 UnrealOn SDK Driver v{__version__} loaded")
    logger.info(f"   🌐 Browser integration: ✅ Available")
    logger.info(f"   📦 Total exports: {len(__all__)} classes/functions")
    logger.info(f"   📂 Groups: Core, Enterprise, Models, Browser, Utils")
