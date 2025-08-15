"""
🚀 UnrealOn SDK v1.0 - Enterprise Parsing Platform

The most advanced SDK for building enterprise-grade parsing solutions with:
- 90% code reduction through intelligent automation
- Type-safe operations with auto-generated models  
- Production-ready features out of the box
- Real-time communication and monitoring
"""

# Import everything from src
from .src import *

# Description
__description__ = "Enterprise Parsing Platform SDK for UnrealOn"


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
    check_compatibility,
)
