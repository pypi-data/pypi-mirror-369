"""
UnrealOn SDK - Main Package
"""

# Import from centralized config
from sdk_config import (
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

# Import main modules
import unrealon_sdk
import unrealon_browser
import unrealon_driver
import unrealon_llm

__all__ = [
    "unrealon_sdk",
    "unrealon_browser", 
    "unrealon_driver",
    "unrealon_llm",
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
