"""
Resource Pooling DTOs - Data Transfer Objects for resource pool management.

This module contains all Pydantic models, enums, and dataclasses related to resource pooling,
separated from business logic for clean architecture and reusability.

Components:
- Resource lifecycle states and scaling strategies
- Pool configuration and resource metadata
- Resource management and monitoring models
- Performance tracking and metrics
"""

from typing import Dict, Optional, Any
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict

# Import from existing concurrency DTOs
from .concurrency import ResourceType


class ResourceLifecycleState(str, Enum):
    """Resource lifecycle states."""

    CREATING = "creating"
    INITIALIZING = "initializing"
    READY = "ready"
    IN_USE = "in_use"
    IDLE = "idle"
    VALIDATING = "validating"
    CLEANING = "cleaning"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"
    ERROR = "error"


class PoolScalingStrategy(str, Enum):
    """Pool scaling strategies."""

    FIXED = "fixed"  # Fixed pool size
    DYNAMIC = "dynamic"  # Dynamic scaling based on demand
    PREDICTIVE = "predictive"  # Predictive scaling based on patterns
    AGGRESSIVE = "aggressive"  # Aggressive scaling for high performance
    CONSERVATIVE = "conservative"  # Conservative scaling for stability


@dataclass
class ResourceMetadata:
    """Resource metadata and tracking information."""

    resource_id: str
    resource_type: ResourceType
    created_at: datetime
    last_used: datetime
    usage_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    lifecycle_state: ResourceLifecycleState = ResourceLifecycleState.CREATING
    tags: Dict[str, str] = field(default_factory=dict)
    health_score: float = 1.0  # 0.0 = unhealthy, 1.0 = perfect health
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class PoolConfig(BaseModel):
    """Resource pool configuration model."""

    model_config = ConfigDict(extra="forbid")

    # Pool identification
    pool_name: str = Field(..., description="Pool name")
    resource_type: ResourceType = Field(..., description="Type of resources in pool")

    # Size configuration
    min_size: int = Field(default=1, description="Minimum pool size")
    max_size: int = Field(default=10, description="Maximum pool size")
    initial_size: int = Field(default=2, description="Initial pool size")
    scaling_strategy: PoolScalingStrategy = Field(
        default=PoolScalingStrategy.DYNAMIC, description="Scaling strategy"
    )

    # Scaling parameters
    scale_up_threshold: float = Field(
        default=0.8, description="Scale up when utilization > threshold"
    )
    scale_down_threshold: float = Field(
        default=0.3, description="Scale down when utilization < threshold"
    )
    scale_factor: float = Field(default=1.5, description="Factor for scaling operations")

    # Timeout settings
    acquisition_timeout_seconds: float = Field(
        default=30.0, description="Resource acquisition timeout"
    )
    idle_timeout_seconds: float = Field(default=300.0, description="Resource idle timeout")
    max_lifetime_seconds: Optional[float] = Field(
        default=None, description="Maximum resource lifetime"
    )

    # Health and validation
    enable_health_checks: bool = Field(default=True, description="Enable health checks")
    health_check_interval_seconds: float = Field(default=60.0, description="Health check interval")
    validation_on_acquire: bool = Field(default=True, description="Validate on acquire")
    validation_on_return: bool = Field(default=False, description="Validate on return")

    # Performance features
    enable_warmup: bool = Field(default=True, description="Enable pool warmup")
    warmup_size: int = Field(default=2, description="Warmup pool size")
    enable_preallocation: bool = Field(default=False, description="Enable resource preallocation")

    # Monitoring and debugging
    enable_leak_detection: bool = Field(default=True, description="Enable leak detection")
    leak_detection_threshold_seconds: float = Field(
        default=3600.0, description="Leak detection threshold"
    )


__all__ = [
    # Enums
    "ResourceLifecycleState",
    "PoolScalingStrategy",
    # Data classes
    "ResourceMetadata",
    # Configuration models
    "PoolConfig",
]
