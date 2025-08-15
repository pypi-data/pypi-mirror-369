"""
🌐 UnrealOn Browser v1.0 - Enterprise Browser Automation

Enterprise-grade browser automation with stealth capabilities and proxy integration.
Service-based architecture following KISS principles.
"""

# Import everything from src
from .src import *

# Description
__description__ = "Enterprise browser automation with stealth capabilities"


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
