"""
Logger Bridge - Integration bridge between unrealon_browser and unrealon_sdk loggers
Layer 2.5: Logging Integration - Connects independent browser module with SDK enterprise loggers
"""

from typing import Optional, Any, Dict
from datetime import datetime, timezone

# Browser DTOs
from unrealon_browser.src.dto import (
    BrowserSessionStatus,
    BrowserSession,
    CaptchaDetectionResult,
    # 🔥 StealthLevel removed - STEALTH ALWAYS ON!
)
from unrealon_sdk.src.enterprise.logging.development import get_development_logger
from unrealon_sdk.src.enterprise.logging import (
    LoggingService,
    StructuredLogger,
    LogLevel,
    DevelopmentLogger,
    SDKEventType,
    SDKSeverity,
    SDKContext,
)
from unrealon_sdk.src.utils import generate_correlation_id


class BrowserLoggerBridge:
    """
    Bridge between unrealon_browser and unrealon_sdk loggers

    Provides unified logging interface for browser operations while
    maintaining compatibility with both standalone and SDK-integrated usage.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        logging_service: Optional[LoggingService] = None,
        development_logger: Optional[DevelopmentLogger] = None,
        enable_console: bool = True,
    ):
        """Initialize logger bridge"""
        self.session_id = session_id or generate_correlation_id()
        self.enable_console = enable_console

        # SDK loggers (optional)
        self.logging_service = logging_service
        self.development_logger = development_logger
        self.structured_logger: Optional[StructuredLogger] = None

        # Initialize structured logger if logging service is available
        if self.logging_service:
            self.structured_logger = self.logging_service.get_logger("browser_automation")

        # Statistics
        self._events_logged = 0
        self._browser_events = {
            "browser_initialized": 0,
            "navigation_success": 0,
            "navigation_failed": 0,
            "stealth_applied": 0,
            "captcha_detected": 0,
            "captcha_solved": 0,
            "profile_created": 0,
            "cookies_saved": 0,
        }

        self._log_debug(
            "BROWSER_LOGGER_INITIALIZED",
            f"BrowserLoggerBridge initialized for session {self.session_id}",
        )

    def _log_console(self, level: str, message: str, **context: Any) -> None:
        """Fallback console logging"""
        if self.enable_console:
            timestamp = datetime.now().strftime("%H:%M:%S")
            context_str = f" {context}" if context else ""
            print(f"{timestamp} | BROWSER | {level} | {message}{context_str}")

    def _log_debug(self, event_type: str, message: str, **context: Any) -> None:
        """Debug level logging with fallbacks"""
        self._events_logged += 1

        # SDK Development Logger
        if self.development_logger:
            try:
                sdk_event = getattr(SDKEventType, event_type, SDKEventType.DEBUG_CHECKPOINT)
                sdk_context = SDKContext(
                    layer_name="Browser_Automation",
                    component_name="BrowserManager",
                    correlation_id=self.session_id,
                )
                self.development_logger.log_debug(sdk_event, message, context=sdk_context)
            except Exception as e:
                self._log_console("DEBUG", f"Development logger error: {e}")

        # Structured Logger
        if self.structured_logger:
            try:
                self.structured_logger.debug(message, **context)
            except Exception as e:
                self._log_console("DEBUG", f"Structured logger error: {e}")

        # Console fallback
        self._log_console("DEBUG", message, **context)

    def _log_info(
        self, event_type: str, message: str, success: bool = True, **context: Any
    ) -> None:
        """Info level logging with fallbacks"""
        self._events_logged += 1

        # SDK Development Logger
        if self.development_logger:
            try:
                sdk_event = getattr(SDKEventType, event_type, SDKEventType.COMPONENT_INTEGRATED)
                sdk_context = SDKContext(
                    layer_name="Browser_Automation",
                    component_name="BrowserManager",
                    correlation_id=self.session_id,
                )
                self.development_logger.log_info(
                    sdk_event, message, context=sdk_context, success=success
                )
            except Exception as e:
                self._log_console("INFO", f"Development logger error: {e}")

        # Structured Logger
        if self.structured_logger:
            try:
                self.structured_logger.info(message, success=success, **context)
            except Exception as e:
                self._log_console("INFO", f"Structured logger error: {e}")

        # Console fallback
        self._log_console("INFO", message, success=success, **context)

    def _log_warning(self, event_type: str, message: str, **context: Any) -> None:
        """Warning level logging with fallbacks"""
        self._events_logged += 1

        # SDK Development Logger
        if self.development_logger:
            try:
                sdk_event = getattr(
                    SDKEventType, event_type, SDKEventType.PERFORMANCE_THRESHOLD_EXCEEDED
                )
                sdk_context = SDKContext(
                    layer_name="Browser_Automation",
                    component_name="BrowserManager",
                    correlation_id=self.session_id,
                )
                self.development_logger.log_warning(sdk_event, message, context=sdk_context)
            except Exception as e:
                self._log_console("WARNING", f"Development logger error: {e}")

        # Structured Logger
        if self.structured_logger:
            try:
                self.structured_logger.warning(message, **context)
            except Exception as e:
                self._log_console("WARNING", f"Structured logger error: {e}")

        # Console fallback
        self._log_console("WARNING", message, **context)

    def _log_error(
        self, event_type: str, message: str, exception: Optional[Exception] = None, **context: Any
    ) -> None:
        """Error level logging with fallbacks"""
        self._events_logged += 1

        # SDK Development Logger
        if self.development_logger:
            try:
                sdk_event = getattr(SDKEventType, event_type, SDKEventType.COMPONENT_DEPRECATED)
                sdk_context = SDKContext(
                    layer_name="Browser_Automation",
                    component_name="BrowserManager",
                    correlation_id=self.session_id,
                )
                self.development_logger.log_error(
                    sdk_event, message, context=sdk_context, exception=exception
                )
            except Exception as e:
                self._log_console("ERROR", f"Development logger error: {e}")

        # Structured Logger
        if self.structured_logger:
            try:
                error_context = {**context}
                if exception:
                    error_context["exception_type"] = type(exception).__name__
                    error_context["exception_message"] = str(exception)
                self.structured_logger.error(message, **error_context)
            except Exception as e:
                self._log_console("ERROR", f"Structured logger error: {e}")

        # Console fallback
        error_context = {**context}
        if exception:
            error_context["exception"] = str(exception)
        self._log_console("ERROR", message, **error_context)

    # Browser-specific logging methods
    def log_browser_initialized(self, metadata: BrowserSession) -> None:
        """Log browser initialization"""
        self._browser_events["browser_initialized"] += 1
        self._log_info(
            "COMPONENT_INTEGRATED",
            f"Browser session initialized: {metadata.session_id}",
            session_id=metadata.session_id,
            parser_name=metadata.parser_name,
            browser_type=metadata.browser_type or "unknown",
            stealth_level="unknown",
            proxy_host=getattr(metadata.proxy, "host", None) if metadata.proxy else None,
            proxy_port=getattr(metadata.proxy, "port", None) if metadata.proxy else None,
        )

    def log_navigation_success(self, url: str, title: str, duration_ms: float) -> None:
        """Log successful navigation"""
        self._browser_events["navigation_success"] += 1
        self._log_info(
            "API_CALL_COMPLETED",
            f"Navigation successful: {title}",
            url=url,
            title=title,
            duration_ms=duration_ms,
            navigation_type="browser_navigation",
        )

    def log_navigation_failed(self, url: str, error: str, duration_ms: float) -> None:
        """Log failed navigation"""
        self._browser_events["navigation_failed"] += 1
        self._log_error(
            "API_CALL_FAILED",
            f"Navigation failed: {url}",
            url=url,
            error_message=error,
            duration_ms=duration_ms,
            navigation_type="browser_navigation",
        )

    def log_stealth_applied(self, stealth_level: str, success: bool) -> None:
        """Log stealth application - 🔥 STEALTH ALWAYS ON!"""
        self._browser_events["stealth_applied"] += 1

        if success:
            self._log_info(
                "COMPONENT_INTEGRATED",
                f"Stealth measures applied: {stealth_level}",
                stealth_level=stealth_level,
                stealth_success=True,
            )
        else:
            self._log_warning(
                "COMPONENT_DEPRECATED",
                f"Stealth application failed: {stealth_level}",
                stealth_level=stealth_level,
                stealth_success=False,
            )

    def log_captcha_detected(self, result: CaptchaDetectionResult) -> None:
        """Log captcha detection"""
        self._browser_events["captcha_detected"] += 1
        self._log_warning(
            "PERFORMANCE_THRESHOLD_EXCEEDED",
            f"Captcha detected: {result.captcha_type.value}",
            captcha_type=result.captcha_type.value,
            page_url=result.page_url,
            proxy_host=result.proxy_host,
            proxy_port=result.proxy_port,
            detected_at=result.detected_at.isoformat(),
        )

    def log_captcha_solved(self, proxy_host: str, proxy_port: int, manual: bool = True) -> None:
        """Log captcha resolution"""
        self._browser_events["captcha_solved"] += 1
        self._log_info(
            "COMPONENT_INTEGRATED",
            f"Captcha solved for proxy {proxy_host}:{proxy_port}",
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            resolution_method="manual" if manual else "automatic",
            cookies_will_be_saved=True,
        )

    def log_profile_created(
        self, profile_name: str, proxy_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log profile creation"""
        self._browser_events["profile_created"] += 1
        context = {"profile_name": profile_name}
        if proxy_info:
            context.update(proxy_info)

        self._log_info("COMPONENT_CREATED", f"Browser profile created: {profile_name}", **context)

    def log_cookies_saved(
        self, proxy_host: str, proxy_port: int, cookies_count: int, parser_name: str
    ) -> None:
        """Log cookie saving"""
        self._browser_events["cookies_saved"] += 1
        self._log_info(
            "DATA_STORED",
            f"Cookies saved for {proxy_host}:{proxy_port}",
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            cookies_count=cookies_count,
            parser_name=parser_name,
            storage_type="proxy_bound",
        )

    def log_performance_metric(
        self, metric_name: str, value: float, unit: str, threshold: Optional[float] = None
    ) -> None:
        """Log performance metrics"""
        # Use development logger for performance tracking if available
        if self.development_logger:
            try:
                self.development_logger.log_performance_metric(
                    metric_name=metric_name,
                    value=value,
                    unit=unit,
                    threshold=threshold,
                    context=SDKContext(
                        layer_name="Browser_Automation",
                        component_name="PerformanceMonitor",
                        correlation_id=self.session_id,
                    ),
                )
            except Exception as e:
                self._log_console("DEBUG", f"Performance metric error: {e}")
        else:
            # Fallback logging
            exceeded = threshold is not None and value > threshold
            level = "WARNING" if exceeded else "DEBUG"
            message = f"Performance: {metric_name} = {value} {unit}"
            if threshold:
                message += f" (threshold: {threshold})"
            self._log_console(level, message, metric=metric_name, value=value, unit=unit)

    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        return {
            "total_events_logged": self._events_logged,
            "browser_events": self._browser_events.copy(),
            "session_id": self.session_id,
            "loggers": {
                "logging_service": self.logging_service is not None,
                "development_logger": self.development_logger is not None,
                "structured_logger": self.structured_logger is not None,
                "console_enabled": self.enable_console,
            },
        }

    def print_statistics(self) -> None:
        """Print logging statistics"""
        stats = self.get_statistics()

        print("\n📊 Browser Logger Bridge Statistics:")
        print(f"   Total events logged: {stats['total_events_logged']}")
        print(f"   Session ID: {stats['session_id']}")

        print("   Browser events:")
        for event, count in stats["browser_events"].items():
            print(f"     {event}: {count}")

        print("   Logger availability:")
        for logger, available in stats["loggers"].items():
            print(f"     {logger}: {'✅' if available else '❌'}")


# Factory function for easy integration
def create_browser_logger_bridge(
    session_id: Optional[str] = None,
    enable_console: bool = True,
) -> BrowserLoggerBridge:
    """
    Create browser logger bridge with automatic SDK detection

    This function attempts to import and use SDK loggers if available,
    but works fine as standalone if SDK is not present.
    """
    logging_service = None
    development_logger = get_development_logger()

    return BrowserLoggerBridge(
        session_id=session_id,
        logging_service=logging_service,
        development_logger=development_logger,
        enable_console=enable_console,
    )
