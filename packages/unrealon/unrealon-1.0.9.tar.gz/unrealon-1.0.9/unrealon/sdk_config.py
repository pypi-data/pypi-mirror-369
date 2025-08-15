"""
UnrealOn SDK Simple Config

Simple centralized configuration with Pydantic v2 models.
"""

import os
from pydantic import BaseModel, Field, ConfigDict

# Simple version constants
VERSION = "1.0.9"

# Project info
AUTHOR = "UnrealOn Team"
AUTHOR_EMAIL = "dev@unrealon.com"
LICENSE = "MIT"
PROJECT_URL = "https://unrealon.com"


class VersionInfo(BaseModel):
    """Version information model."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    version: str = Field(default=VERSION)
    


class ProjectInfo(BaseModel):
    """Project information model."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    author: str = Field(default=AUTHOR)
    email: str = Field(default=AUTHOR_EMAIL)
    license: str = Field(default=LICENSE)
    url: str = Field(default=PROJECT_URL)


# Global instances
VERSION_INFO = VersionInfo()
PROJECT_INFO = ProjectInfo()


def get_version() -> str:
    """Get SDK version."""
    return VERSION


def is_debug_mode() -> bool:
    """Check if debug mode enabled."""
    return os.getenv("UNREALON_DEBUG", "").lower() in ("1", "true", "debug")


# Compatibility check
def check_compatibility(required_version: str) -> bool:
    """Check if SDK version is compatible with required version."""
    try:
        required = tuple(map(int, required_version.split(".")))
        current = tuple(map(int, VERSION.split(".")))
        return current >= required
    except (ValueError, AttributeError):
        return False


# Debug output
if os.getenv("UNREALON_DEBUG", "").lower() in ("1", "true", "debug"):
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 UnrealOn SDK v{VERSION} loaded")
    logger.info(f"   🎯 Service-based architecture")
    logger.info(f"   📦 KISS principle - simple & reliable")
    logger.info(f"   🔗 Available services: {', '.join(__all__)}")


__all__ = [
    "VERSION",
    "AUTHOR",
    "AUTHOR_EMAIL",
    "LICENSE",
    "PROJECT_URL",
    "VersionInfo",
    "ProjectInfo",
    "VERSION_INFO",
    "PROJECT_INFO",
    "get_version",
    "is_debug_mode",
    "check_compatibility",
]
