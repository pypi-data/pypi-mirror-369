"""
UnrealOn SDK - Main Package
"""

# Import from centralized config
from .sdk_config import (
    VERSION as __version__,
    AUTHOR as __author__,
    AUTHOR_EMAIL as __email__,
    LICENSE as __license__,
    PROJECT_URL as __url__,
    VERSION_INFO,
    PROJECT_INFO,
    get_version,
    is_debug_mode,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    "VERSION_INFO",
    "PROJECT_INFO",
    "get_version",
    "is_debug_mode",
]
