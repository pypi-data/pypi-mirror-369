"""
🤖 UnrealOn LLM v1.0 - Large Language Model Integration

Advanced LLM integration tools for AI-powered parsing and data processing.
Service-based architecture following KISS principles.
"""

# Import everything from src
from .src import *

# Description
__description__ = "Large Language Model integration tools for UnrealOn SDK"


# Import from centralized config
from unrealon.sdk_config import (
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
