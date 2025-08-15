"""
Utility functions for UnrealOn SDK v1.0

Provides common helper functions used throughout the SDK.
"""

import re
import uuid
import time
import platform
import sys
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from unrealon_sdk.src.core.metadata import EnvironmentMetadata


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not api_key:
        return False

    # Check if it matches the expected pattern
    pattern = r"^up_(dev|prod)_[a-zA-Z0-9_]{16,}$"
    return bool(re.match(pattern, api_key))


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Args:
        url: URL to extract domain from

    Returns:
        str: Domain name or None if invalid URL
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def calculate_success_rate(successful: int, total: int) -> float:
    """
    Calculate success rate percentage.

    Args:
        successful: Number of successful operations
        total: Total number of operations

    Returns:
        float: Success rate as percentage (0.0-100.0)
    """
    if total == 0:
        return 0.0
    return (successful / total) * 100.0


def format_duration(milliseconds: float) -> str:
    """
    Format duration in milliseconds to human-readable string.

    Args:
        milliseconds: Duration in milliseconds

    Returns:
        str: Formatted duration string
    """
    if milliseconds < 1000:
        return f"{milliseconds:.2f}ms"

    seconds = milliseconds / 1000
    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"

    hours = minutes / 60
    return f"{hours:.1f}h"


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for request tracking.

    Returns:
        str: Unique correlation ID
    """
    return str(uuid.uuid4())


def generate_session_id() -> str:
    """
    Generate a unique session ID.

    Returns:
        str: Unique session ID
    """
    timestamp = int(time.time() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    return f"sess_{timestamp}_{unique_id}"


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary with dot notation support.

    Args:
        data: Dictionary to get value from
        key: Key to get (supports dot notation like 'user.profile.name')
        default: Default value if key not found

    Returns:
        Any: Value at key or default
    """
    try:
        if "." not in key:
            return data.get(key, default)

        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    except Exception:
        return default


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries recursively.

    Args:
        base: Base configuration
        override: Configuration to merge on top

    Returns:
        Dict[str, Any]: Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize log data by removing sensitive information.

    Args:
        data: Data to sanitize

    Returns:
        Dict[str, Any]: Sanitized data
    """
    sensitive_keys = {
        "password",
        "token",
        "api_key",
        "secret",
        "auth",
        "authorization",
        "credentials",
        "key",
    }

    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_log_data(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def is_url_valid(url: str) -> bool:
    """
    Check if URL is valid.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_client_info() -> EnvironmentMetadata:
    """
    Get client information for debugging/monitoring.

    Returns:
        EnvironmentMetadata: Structured client information
    """
    return EnvironmentMetadata(
        environment="runtime",
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        platform=platform.platform(),
        architecture=platform.architecture()[0],
        sdk_version="1.0.0",
        correlation_id=generate_correlation_id(),
    )
