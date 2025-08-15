"""
Exception hierarchy for UnrealOn SDK v1.0

Provides comprehensive error handling with structured exception types
for different categories of errors that can occur in the SDK.
"""

from typing import Optional, Any


class UnrealOnError(Exception):
    """
    Base exception for all UnrealOn SDK errors.

    All SDK exceptions inherit from this base class to allow
    for comprehensive error handling.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNREALON_ERROR"
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConnectionError(UnrealOnError):
    """
    Raised when connection-related errors occur.

    This includes WebSocket connection failures, HTTP connection issues,
    network timeouts, and connection state errors.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "CONNECTION_ERROR", details)


class AuthenticationError(UnrealOnError):
    """
    Raised when authentication fails.

    This includes invalid API keys, expired tokens,
    permission denied, and other auth-related issues.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "AUTH_ERROR", details)


class ConfigurationError(UnrealOnError):
    """
    Raised when configuration is invalid or incomplete.

    This includes missing required fields, invalid values,
    incompatible settings, and configuration validation errors.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "CONFIG_ERROR", details)


class CommandError(UnrealOnError):
    """
    Raised when command processing fails.

    This includes unknown command types, command execution failures,
    timeout errors, and command validation issues.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "COMMAND_ERROR", details)


class ProxyError(UnrealOnError):
    """
    Raised when proxy-related errors occur.

    This includes proxy connection failures, proxy rotation issues,
    proxy authentication problems, and proxy health check failures.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "PROXY_ERROR", details)


class TimeoutError(UnrealOnError):
    """
    Raised when operations exceed their timeout limits.

    This includes command timeouts, connection timeouts,
    response timeouts, and other time-based failures.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "TIMEOUT_ERROR", details)


class ValidationError(UnrealOnError):
    """
    Raised when data validation fails.

    This includes Pydantic validation errors, schema validation,
    data format errors, and type validation issues.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "VALIDATION_ERROR", details)


class RegistrationError(UnrealOnError):
    """
    Raised when parser registration fails.

    This includes registration validation errors, duplicate parser IDs,
    service registration issues, and registration timeout errors.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "REGISTRATION_ERROR", details)


class WebSocketError(UnrealOnError):
    """
    Raised when WebSocket-specific errors occur.

    This includes WebSocket protocol errors, message format issues,
    event handling errors, and WebSocket state problems.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "WEBSOCKET_ERROR", details)


class MonitoringError(UnrealOnError):
    """
    Raised when monitoring system errors occur.

    This includes metrics collection failures, health check errors,
    monitoring configuration issues, and performance tracking problems.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "MONITORING_ERROR", details)


class LoggingError(UnrealOnError):
    """
    Raised when logging system errors occur.

    This includes log transmission failures, log format errors,
    logging configuration issues, and log destination problems.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, error_code or "LOGGING_ERROR", details)


class RateLimitError(UnrealOnError):
    """
    Raised when rate limits are exceeded.

    This includes API rate limiting, command throttling,
    resource usage limits, and quota exceeded errors.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, error_code or "RATE_LIMIT_ERROR", details)
        self.retry_after = retry_after
