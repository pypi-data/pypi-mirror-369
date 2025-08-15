"""
Exception classes for UnrealOn Driver v3.0

Comprehensive error handling with detailed information and recovery suggestions.
"""

from typing import Any, Dict, List, Optional


class ParserError(Exception):
    """Base exception for all parser-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        context: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "PARSER_ERROR"
        self.suggestions = suggestions or []
        self.context = context or {}

    def to_dict(self) -> dict:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "suggestions": self.suggestions,
            "context": self.context,
        }


class ConfigurationError(ParserError):
    """Configuration and setup related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            suggestions=[
                "Check your configuration file",
                "Verify environment variables",
                "Review documentation for correct setup",
            ],
            **kwargs,
        )


class BrowserError(ParserError):
    """Browser automation related errors."""

    def __init__(
        self,
        message: str,
        page_url: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        **kwargs,
    ):
        context = kwargs.pop("context", {})  # Remove from kwargs to avoid duplicate
        context.update({"page_url": page_url, "screenshot_path": screenshot_path})

        super().__init__(
            message,
            error_code="BROWSER_ERROR",
            suggestions=[
                "Check if the website is accessible",
                "Verify CSS selectors are correct",
                "Try increasing timeout values",
                "Check if anti-bot protection is blocking requests",
            ],
            context=context,
            **kwargs,
        )


class LLMError(ParserError):
    """LLM and AI extraction related errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        cost_exceeded: bool = False,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        context.update(
            {"provider": provider, "model": model, "cost_exceeded": cost_exceeded}
        )

        suggestions = [
            "Check API key and quotas",
            "Verify model availability",
            "Review input data format",
        ]

        if cost_exceeded:
            suggestions.extend(
                [
                    "Check daily cost limits",
                    "Consider using caching",
                    "Switch to a cheaper model",
                ]
            )

        super().__init__(
            message,
            error_code="LLM_ERROR",
            suggestions=suggestions,
            context=context,
            **kwargs,
        )


class WebSocketError(ParserError):
    """WebSocket daemon mode related errors."""

    def __init__(
        self,
        message: str,
        server_url: Optional[str] = None,
        connection_status: Optional[str] = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        context.update(
            {"server_url": server_url, "connection_status": connection_status}
        )

        super().__init__(
            message,
            error_code="WEBSOCKET_ERROR",
            suggestions=[
                "Check server URL and connectivity",
                "Verify API key authentication",
                "Check firewall and network settings",
                "Review server status and availability",
            ],
            context=context,
            **kwargs,
        )


class SchedulingError(ParserError):
    """Scheduling and automation related errors."""

    def __init__(
        self, message: str, schedule_expression: Optional[str] = None, **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({"schedule_expression": schedule_expression})

        super().__init__(
            message,
            error_code="SCHEDULING_ERROR",
            suggestions=[
                "Check schedule expression format",
                "Verify time zone settings",
                "Review system permissions for scheduling",
                "Check available system resources",
            ],
            context=context,
            **kwargs,
        )


class ValidationError(ParserError):
    """Data validation related errors."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        context.update(
            {
                "field_name": field_name,
                "expected_type": expected_type,
                "actual_value": actual_value,
            }
        )

        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            suggestions=[
                "Check data format and types",
                "Verify schema definitions",
                "Review input validation rules",
            ],
            context=context,
            **kwargs,
        )


class NetworkError(ParserError):
    """Network and connectivity related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        context.update({"status_code": status_code, "response_body": response_body})

        super().__init__(
            message,
            error_code="NETWORK_ERROR",
            suggestions=[
                "Check internet connectivity",
                "Verify target URL accessibility",
                "Review rate limiting and quotas",
                "Check for temporary service outages",
            ],
            context=context,
            **kwargs,
        )


class TimeoutError(ParserError):
    """Timeout related errors."""

    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        operation_type: Optional[str] = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        context.update(
            {"timeout_duration": timeout_duration, "operation_type": operation_type}
        )

        super().__init__(
            message,
            error_code="TIMEOUT_ERROR",
            suggestions=[
                "Increase timeout values",
                "Check network connectivity",
                "Verify target website performance",
                "Consider breaking operation into smaller parts",
            ],
            context=context,
            **kwargs,
        )


# Convenience functions for creating errors with context


def create_browser_error(
    message: str, url: str, selector: Optional[str] = None, **kwargs
) -> BrowserError:
    """Create browser error with common context."""
    context = {"url": url}
    if selector:
        context["selector"] = selector

    return BrowserError(message, context=context, **kwargs)


def create_llm_error(
    message: str, provider: str, model: str, input_size: Optional[int] = None, **kwargs
) -> LLMError:
    """Create LLM error with common context."""
    context = {"input_size": input_size} if input_size else {}

    return LLMError(message, provider=provider, model=model, context=context, **kwargs)


def create_websocket_error(
    message: str, server_url: str, error_details: Optional[dict] = None, **kwargs
) -> WebSocketError:
    """Create WebSocket error with common context."""
    context = error_details or {}

    return WebSocketError(message, server_url=server_url, context=context, **kwargs)
