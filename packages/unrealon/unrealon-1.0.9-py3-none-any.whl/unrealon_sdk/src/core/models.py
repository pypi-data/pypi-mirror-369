"""
Core data models for UnrealOn SDK.

This module provides the foundational Pydantic models that form the backbone
of the SDK's type-safe architecture. All models use Pydantic v2 with strict
validation and zero tolerance for Dict[str, Any] patterns.

CRITICAL REQUIREMENTS COMPLIANCE:
- NO relative imports (absolute imports only)
- NO Dict[str, Any] usage (Pydantic models only)
- NO Python 3.10+ union syntax (Union[X, Y] only)
- 100% type annotation coverage
- Strict Pydantic v2 compliance

NOTE: Some models have been moved to /dto/ for better organization.
This module focuses on core SDK models, while /dto/ contains specialized DTOs.
"""

from typing import Dict, Optional, Union, Any, List
from pydantic import BaseModel, Field, ConfigDict

# Import DTO models for backward compatibility
from unrealon_sdk.src.dto.health import ConnectionHealthStatus as DTOConnectionHealthStatus
from unrealon_sdk.src.dto.health import ComponentStatus as DTOComponentStatus


class AdapterStatus(BaseModel):
    """
    Current operational status of the adapter.

    This model tracks the adapter's connection state, session information,
    and health metrics in a type-safe manner.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    is_connected: bool = Field(
        False, description="Whether the adapter is currently connected to UnrealOn services."
    )
    session_id: Optional[str] = Field(None, description="Current session ID if connected.")
    last_error: Optional[str] = Field(None, description="Last error message encountered.")
    connection_attempts: int = Field(0, description="Number of connection attempts made.")


class CommandMetadata(BaseModel):
    """
    Metadata for parser commands with strict type validation.

    Replaces any Dict[str, Any] usage with properly typed fields.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    command_id: str = Field(..., description="Unique command identifier")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    source: str = Field(..., description="Command source identifier")
    priority: int = Field(default=0, description="Command priority level")
    retry_count: int = Field(default=0, description="Number of retry attempts")


class ErrorDetails(BaseModel):
    """
    Structured error information replacing Dict[str, Any] patterns.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    error_code: str = Field(..., description="Error classification code")
    message: str = Field(..., description="Human-readable error message")
    context: Optional[str] = Field(None, description="Additional error context")
    is_recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_action: Optional[str] = Field(None, description="Suggested recovery action")


class HealthCheckResult(BaseModel):
    """
    Health check response model with strict typing.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    status: str = Field(..., description="Health status: 'healthy', 'degraded', or 'unhealthy'")
    timestamp: str = Field(..., description="ISO 8601 timestamp of check")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    services: List[str] = Field(default_factory=list, description="List of healthy services")
    errors: List[ErrorDetails] = Field(default_factory=list, description="Any detected errors")


class WebSocketEventBase(BaseModel):
    """
    Base model for all WebSocket events with strict validation.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    event_type: str = Field(..., description="Type of WebSocket event")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    metadata: Optional[CommandMetadata] = Field(None, description="Event metadata")


class ConnectionHealthStatus(BaseModel):
    """
    Connection health status model with strict validation.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    is_healthy: bool = Field(..., description="Overall health status")
    connection_quality: float = Field(..., ge=0.0, le=1.0, description="Connection quality (0-1)")
    latency_ms: float = Field(..., ge=0.0, description="Connection latency in milliseconds")
    uptime_seconds: float = Field(..., ge=0.0, description="Connection uptime in seconds")
    last_heartbeat: str = Field(..., description="ISO 8601 timestamp of last heartbeat")


class ComponentStatus(BaseModel):
    """
    Individual component status with strict typing.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    component_name: str = Field(..., description="Name of the component")
    status: str = Field(..., description="Status: 'active', 'inactive', 'error', 'degraded'")
    last_update: str = Field(..., description="ISO 8601 timestamp of last status update")
    error_details: Optional[ErrorDetails] = Field(
        None, description="Error information if status is 'error'"
    )
    metrics: Optional[Dict[str, Union[int, float, str]]] = Field(
        None, description="Component-specific metrics"
    )


# Migration aliases - Use DTO models instead of duplicating here
# These provide backward compatibility while encouraging DTO usage

# Alias to DTO model for new code
ConnectionHealthStatusDTO = DTOConnectionHealthStatus
ComponentStatusDTO = DTOComponentStatus

# Note: For new development, import directly from unrealon_sdk.src.dto.health
# This ensures proper separation of concerns and avoids model duplication
