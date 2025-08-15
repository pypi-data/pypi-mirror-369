"""
CLI Configuration Models for UnrealOn Driver v3.0

Type-safe configuration for CLI interface.
COMPLIANCE: 100% Pydantic v2 compliant.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any

from .config import LogLevel


class ParserInstanceConfig(BaseModel):
    """
    Pydantic configuration model for Parser initialization.
    COMPLIANCE: CRITICAL_REQUIREMENTS.md - Pydantic v2 validation.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core identity
    parser_id: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Unique parser identifier (snake_case)",
    )
    parser_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Human-readable parser name (auto-generated if None)",
    )

    # System configuration
    system_dir: str = Field(
        default="system",
        min_length=1,
        description="System directory for logs and files",
    )
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")

    # Optional metadata
    description: Optional[str] = Field(
        default=None, max_length=200, description="Parser description"
    )
    version: str = Field(
        default="1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Parser version (semantic versioning)",
    )

    @field_validator("parser_name")
    @classmethod
    def generate_parser_name(cls, v: Optional[str], info) -> str:
        """Auto-generate parser_name from parser_id if not provided."""
        if v is None and "parser_id" in info.data:
            parser_id = info.data["parser_id"]
            return parser_id.replace("_", " ").title()
        return v or "Unknown Parser"

    def to_parser_config(self) -> dict:
        """Convert to dict for Parser initialization."""
        return {
            "parser_id": self.parser_id,
            "parser_name": self.parser_name,
            "debug_mode": self.log_level in {LogLevel.DEBUG, LogLevel.TRACE},
            "system_dir": self.system_dir,
            "environment": (
                "development"
                if self.log_level in {LogLevel.DEBUG, LogLevel.TRACE}
                else "production"
            ),
            "logger": {"log_level": self.log_level.value},
        }


def create_parser_config(
    parser_id: str,
    parser_name: Optional[str] = None,
    system_dir: str = "system",
    log_level: str = "INFO",
    **kwargs,
) -> ParserInstanceConfig:
    """
    Factory function for creating ParserInstanceConfig.
    COMPLIANCE: CRITICAL_REQUIREMENTS.md - Factory for clean instantiation.

    Args:
        parser_id: Unique parser identifier
        parser_name: Human-readable name (auto-generated if None)
        system_dir: System directory
        log_level: Logging level
        **kwargs: Additional parameters

    Returns:
        Validated ParserInstanceConfig

    Example:
        config = create_parser_config(
            parser_id="simple_extractor",
            system_dir="system",
            log_level="DEBUG"
        )
        parser = SimpleParser(config)
    """
    return ParserInstanceConfig(
        parser_id=parser_id,
        parser_name=parser_name,
        system_dir=system_dir,
        log_level=LogLevel(log_level.upper()),
        **kwargs,
    )
