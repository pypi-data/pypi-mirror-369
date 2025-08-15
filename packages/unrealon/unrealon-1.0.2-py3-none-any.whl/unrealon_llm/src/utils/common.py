"""
Common Utilities

General-purpose utility functions for UnrealOn LLM including
ID generation, validation, and other common helpers.
"""

import uuid
import secrets
from typing import Optional


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for tracking operations."""
    return f"llm_{uuid.uuid4().hex[:16]}"


def generate_request_id() -> str:
    """Generate a unique request ID for API calls."""
    return f"req_{secrets.token_hex(8)}"


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"sess_{uuid.uuid4().hex[:12]}"


def sanitize_model_name(model_name: str) -> str:
    """Sanitize model name for logging and metrics."""
    return model_name.replace("/", "_").replace(":", "_").replace("-", "_")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text for logging purposes."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_bytes(bytes_count: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"


def format_duration_ms(duration_ms: float) -> str:
    """Format duration in milliseconds to human readable format."""
    if duration_ms < 1000:
        return f"{duration_ms:.1f}ms"
    elif duration_ms < 60000:
        return f"{duration_ms / 1000:.1f}s"
    else:
        minutes = int(duration_ms / 60000)
        seconds = (duration_ms % 60000) / 1000
        return f"{minutes}m{seconds:.1f}s"


def safe_get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get environment variable with optional default."""
    import os
    return os.getenv(key, default)
