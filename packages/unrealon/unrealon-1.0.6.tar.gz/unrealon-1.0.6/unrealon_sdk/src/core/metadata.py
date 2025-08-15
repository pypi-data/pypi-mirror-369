"""
Structured metadata models for UnrealOn SDK v1.0

These Pydantic v2 models replace ALL Dict[str, Any] usage throughout the SDK,
ensuring 100% type safety and validation for metadata objects.

CRITICAL: These models are mandatory - NO raw dictionaries allowed!
"""

from datetime import datetime
from typing import Optional, List, Dict, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class SDKMetadata(BaseModel):
    """Base metadata model for SDK components."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=True
    )
    
    sdk_version: str = Field(default="1.0.0", description="SDK version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    correlation_id: Optional[str] = Field(default=None, description="Request correlation ID")


class RegistrationMetadata(SDKMetadata):
    """Metadata for parser registration operations."""
    
    parser_id: str = Field(..., description="Unique parser identifier")
    parser_name: str = Field(..., description="Human-readable parser name")
    parser_type: str = Field(..., description="Type of parser")
    environment: str = Field(..., description="Environment (development, staging, production)")
    features_enabled: List[str] = Field(default_factory=list, description="List of enabled features")


class CommandExecutionMetadata(SDKMetadata):
    """Metadata for command execution operations."""
    
    command_id: str = Field(..., description="Unique command identifier")
    command_type: str = Field(..., description="Type of command being executed")
    parser_id: str = Field(..., description="Parser handling the command")
    execution_start: datetime = Field(default_factory=datetime.utcnow, description="Execution start time")
    timeout_ms: int = Field(default=30000, ge=1000, description="Command timeout in milliseconds")


class LoggingContextMetadata(SDKMetadata):
    """Metadata for logging context."""
    
    component_name: str = Field(..., description="Component generating the log")
    log_level: str = Field(..., description="Log level")
    function_name: Optional[str] = Field(default=None, description="Function name")
    operation_type: Optional[str] = Field(default=None, description="Type of operation")


class EnvironmentMetadata(SDKMetadata):
    """Metadata about the runtime environment."""
    
    environment: str = Field(..., description="Environment name (development, staging, production)")
    python_version: str = Field(..., description="Python version")
    platform: str = Field(..., description="Operating system platform")
    architecture: str = Field(..., description="System architecture")


class ProxyOperationMetadata(SDKMetadata):
    """Metadata for proxy operations."""
    
    proxy_id: str = Field(..., description="Unique proxy identifier")
    proxy_identifier: str = Field(..., description="Human-readable proxy identifier")
    operation_type: str = Field(..., description="Type of proxy operation")
    region: Optional[str] = Field(default=None, description="Proxy region/location")


class ExecutionInfo(BaseModel):
    """Information about command execution."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    command_id: str = Field(..., description="Command identifier")
    command_type: str = Field(..., description="Command type")
    status: str = Field(..., description="Execution status")
    start_time: datetime = Field(..., description="Execution start time")
    duration_ms: Optional[float] = Field(default=None, description="Execution duration")


class RouterStatistics(BaseModel):
    """Command router statistics."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    total_commands: int = Field(..., ge=0, description="Total commands processed")
    successful_commands: int = Field(..., ge=0, description="Successful commands")
    failed_commands: int = Field(..., ge=0, description="Failed commands")
    average_execution_time_ms: float = Field(..., ge=0, description="Average execution time")
    active_executions: int = Field(..., ge=0, description="Currently executing commands")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")


class DevelopmentLoggerStatistics(BaseModel):
    """Development logger statistics."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    total_events: int = Field(..., ge=0, description="Total events logged")
    events_by_type: Dict[str, int] = Field(default_factory=dict, description="Events count by type")
    events_by_severity: Dict[str, int] = Field(default_factory=dict, description="Events count by severity")
    buffer_size: int = Field(..., ge=0, description="Current buffer size")
    websocket_connected: bool = Field(..., description="WebSocket connection status")
    startup_time: datetime = Field(..., description="Logger startup time")


class LoggingServiceStatistics(BaseModel):
    """Logging service statistics."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    total_logs: int = Field(..., ge=0, description="Total logs processed")
    logs_by_level: Dict[str, int] = Field(default_factory=dict, description="Logs count by level")
    websocket_logs: int = Field(..., ge=0, description="WebSocket logs sent")
    buffer_size: int = Field(..., ge=0, description="Current buffer size")
    failed_sends: int = Field(..., ge=0, description="Failed WebSocket sends")
    last_flush: datetime = Field(..., description="Last buffer flush time")


class HTTPClientStatistics(BaseModel):
    """HTTP client statistics."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    total_requests: int = Field(..., ge=0, description="Total HTTP requests made")
    successful_requests: int = Field(..., ge=0, description="Successful requests")
    failed_requests: int = Field(..., ge=0, description="Failed requests")
    average_response_time_ms: float = Field(..., ge=0, description="Average response time")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")


class WebSocketClientStatistics(BaseModel):
    """WebSocket client statistics."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    connection_state: str = Field(..., description="Current connection state")
    total_messages: int = Field(..., ge=0, description="Total messages sent/received")
    reconnect_count: int = Field(..., ge=0, description="Number of reconnections")
    last_ping_ms: Optional[float] = Field(default=None, description="Last ping response time")
    uptime_seconds: float = Field(..., ge=0, description="Connection uptime in seconds")


class WebSocketHealthInfo(BaseModel):
    """WebSocket client health information."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    connected: bool = Field(..., description="Is currently connected")
    reconnect_count: int = Field(..., ge=0, description="Number of reconnections")
    last_ping: Optional[str] = Field(default=None, description="Last ping timestamp")
    connection_state: 'WebSocketConnectionState' = Field(..., description="Detailed connection state")


class WebSocketConnectionState(BaseModel):
    """WebSocket connection state details."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=True)
    
    connected: bool = Field(..., description="Connection established")
    connecting: bool = Field(..., description="Currently connecting")
    error: Optional[str] = Field(default=None, description="Connection error if any")
    last_connected: Optional[str] = Field(default=None, description="Last connection timestamp")
    reconnect_count: int = Field(..., ge=0, description="Reconnection attempts")


__all__ = [
    "SDKMetadata",
    "RegistrationMetadata", 
    "CommandExecutionMetadata",
    "LoggingContextMetadata",
    "EnvironmentMetadata",
    "ProxyOperationMetadata",
    "ExecutionInfo",
    "RouterStatistics",
    "DevelopmentLoggerStatistics",
    "LoggingServiceStatistics",
    "HTTPClientStatistics",
    "WebSocketClientStatistics",
    "WebSocketHealthInfo",
    "WebSocketConnectionState",
]
