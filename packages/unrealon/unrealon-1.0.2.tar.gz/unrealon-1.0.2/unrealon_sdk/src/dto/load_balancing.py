"""
Load Balancing DTOs - Data Transfer Objects for load balancing system.

This module contains all Pydantic models, enums, and dataclasses related to load balancing,
separated from business logic for clean architecture and reusability.

Components:
- Load balancing strategies and algorithms
- Node health and performance tracking
- Traffic distribution and routing models
- Circuit breaker and failover patterns
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ConfigDict


class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithms."""

    ROUND_ROBIN = "round_robin"  # Simple round-robin
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  # Weighted round-robin
    LEAST_CONNECTIONS = "least_connections"  # Least active connections
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"  # Weighted least connections
    LEAST_RESPONSE_TIME = "least_response_time"  # Fastest response time
    RESOURCE_BASED = "resource_based"  # Based on resource utilization
    GEOGRAPHIC = "geographic"  # Geographic proximity
    HASH_BASED = "hash_based"  # Consistent hashing
    RANDOM = "random"  # Random selection
    ADAPTIVE = "adaptive"  # Adaptive algorithm


class NodeHealthStatus(str, Enum):
    """Node health status."""

    HEALTHY = "healthy"  # Node is healthy and available
    DEGRADED = "degraded"  # Node is working but performance is degraded
    UNHEALTHY = "unhealthy"  # Node is unhealthy but still responding
    UNAVAILABLE = "unavailable"  # Node is not responding
    DRAINING = "draining"  # Node is draining connections
    MAINTENANCE = "maintenance"  # Node is under maintenance


class TrafficDirection(str, Enum):
    """Traffic direction for routing."""

    INBOUND = "inbound"  # Incoming traffic
    OUTBOUND = "outbound"  # Outgoing traffic
    BIDIRECTIONAL = "bidirectional"  # Both directions


class FailoverStrategy(str, Enum):
    """Failover strategies."""

    IMMEDIATE = "immediate"  # Immediate failover
    GRACEFUL = "graceful"  # Graceful failover with draining
    DELAYED = "delayed"  # Delayed failover with retry
    CIRCUIT_BREAKER = "circuit_breaker"  # Circuit breaker pattern


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit breaker is open (failing)
    HALF_OPEN = "half_open"  # Testing if service is back


class LoadBalancerNode(BaseModel):
    """Load balancer node configuration and status."""

    model_config = ConfigDict(extra="forbid")

    # Node identification
    node_id: str = Field(..., description="Unique node identifier")
    node_name: str = Field(..., description="Human-readable node name")
    host: str = Field(..., description="Node hostname or IP")
    port: int = Field(..., description="Node port")

    # Node configuration
    weight: int = Field(default=1, description="Node weight for weighted algorithms")
    priority: int = Field(default=1, description="Node priority (1=highest)")
    max_connections: Optional[int] = Field(default=None, description="Maximum connections")
    timeout_seconds: float = Field(default=30.0, description="Connection timeout")

    # Health and status
    health_status: NodeHealthStatus = Field(
        default=NodeHealthStatus.HEALTHY, description="Health status"
    )
    is_enabled: bool = Field(default=True, description="Whether node is enabled")
    last_health_check: Optional[datetime] = Field(
        default=None, description="Last health check time"
    )

    # Performance metrics
    current_connections: int = Field(default=0, description="Current active connections")
    total_requests: int = Field(default=0, description="Total requests handled")
    failed_requests: int = Field(default=0, description="Failed requests count")
    avg_response_time_ms: float = Field(default=0.0, description="Average response time")

    # Geographic and metadata
    region: Optional[str] = Field(default=None, description="Geographic region")
    zone: Optional[str] = Field(default=None, description="Availability zone")
    tags: Dict[str, str] = Field(default_factory=dict, description="Node tags")

    # Circuit breaker
    circuit_breaker_state: CircuitBreakerState = Field(
        default=CircuitBreakerState.CLOSED, description="Circuit breaker state"
    )
    failure_count: int = Field(default=0, description="Consecutive failure count")
    last_failure: Optional[datetime] = Field(default=None, description="Last failure time")


class LoadBalancingRule(BaseModel):
    """Load balancing rule configuration."""

    model_config = ConfigDict(extra="forbid")

    # Rule identification
    rule_id: str = Field(..., description="Rule identifier")
    rule_name: str = Field(..., description="Rule name")

    # Rule configuration
    algorithm: LoadBalancingAlgorithm = Field(..., description="Load balancing algorithm")
    traffic_direction: TrafficDirection = Field(
        default=TrafficDirection.INBOUND, description="Traffic direction"
    )
    priority: int = Field(default=1, description="Rule priority")

    # Conditions
    source_patterns: List[str] = Field(
        default_factory=list, description="Source IP/hostname patterns"
    )
    destination_patterns: List[str] = Field(
        default_factory=list, description="Destination patterns"
    )
    port_ranges: List[str] = Field(default_factory=list, description="Port ranges")
    path_patterns: List[str] = Field(default_factory=list, description="URL path patterns")

    # Target nodes
    target_nodes: List[str] = Field(default_factory=list, description="Target node IDs")
    backup_nodes: List[str] = Field(default_factory=list, description="Backup node IDs")

    # Failover configuration
    failover_strategy: FailoverStrategy = Field(
        default=FailoverStrategy.GRACEFUL, description="Failover strategy"
    )
    health_check_interval_seconds: float = Field(default=30.0, description="Health check interval")
    failure_threshold: int = Field(default=3, description="Failure threshold for marking unhealthy")
    recovery_threshold: int = Field(default=2, description="Recovery threshold for marking healthy")

    # Advanced settings
    session_affinity: bool = Field(default=False, description="Enable session affinity")
    connection_draining_timeout_seconds: float = Field(
        default=300.0, description="Connection draining timeout"
    )
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker")


class LoadBalancingDecisionRequest(BaseModel):
    """Request for load balancing decision."""

    model_config = ConfigDict(extra="forbid")

    # Request identification
    request_id: str = Field(..., description="Request identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

    # Request details
    source_ip: str = Field(..., description="Source IP address")
    source_port: Optional[int] = Field(default=None, description="Source port")
    destination_ip: Optional[str] = Field(default=None, description="Destination IP")
    destination_port: Optional[int] = Field(default=None, description="Destination port")

    # HTTP-specific (if applicable)
    http_method: Optional[str] = Field(default=None, description="HTTP method")
    path: Optional[str] = Field(default=None, description="Request path")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")

    # Context
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Request timestamp"
    )
    traffic_direction: TrafficDirection = Field(
        default=TrafficDirection.INBOUND, description="Traffic direction"
    )
    priority: int = Field(default=1, description="Request priority")

    # Constraints
    required_tags: Dict[str, str] = Field(default_factory=dict, description="Required node tags")
    excluded_nodes: Set[str] = Field(default_factory=set, description="Nodes to exclude")
    preferred_region: Optional[str] = Field(default=None, description="Preferred geographic region")


class LoadBalancingDecisionResult(BaseModel):
    """Result of load balancing decision."""

    model_config = ConfigDict(extra="forbid")

    # Decision result
    selected_node: Optional[LoadBalancerNode] = Field(default=None, description="Selected node")
    backup_nodes: List[LoadBalancerNode] = Field(default_factory=list, description="Backup nodes")

    # Decision metadata
    algorithm_used: LoadBalancingAlgorithm = Field(..., description="Algorithm used")
    rule_applied: Optional[str] = Field(default=None, description="Rule ID applied")
    decision_time_ms: float = Field(..., description="Time taken to make decision")

    # Reasoning
    selection_factors: Dict[str, Any] = Field(
        default_factory=dict, description="Factors in selection"
    )
    rejected_nodes: List[str] = Field(default_factory=list, description="Rejected node IDs")
    rejection_reasons: Dict[str, str] = Field(default_factory=dict, description="Rejection reasons")

    # Session affinity
    session_affinity_used: bool = Field(
        default=False, description="Whether session affinity was used"
    )
    new_session_created: bool = Field(default=False, description="Whether new session was created")

    # Timing
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Decision timestamp"
    )


class LoadBalancerStatistics(BaseModel):
    """Load balancer statistics and metrics."""

    model_config = ConfigDict(extra="forbid")

    # Request metrics
    total_requests: int = Field(default=0, description="Total requests processed")
    successful_requests: int = Field(default=0, description="Successful requests")
    failed_requests: int = Field(default=0, description="Failed requests")
    avg_response_time_ms: float = Field(default=0.0, description="Average response time")

    # Node metrics
    total_nodes: int = Field(default=0, description="Total configured nodes")
    healthy_nodes: int = Field(default=0, description="Healthy nodes")
    unhealthy_nodes: int = Field(default=0, description="Unhealthy nodes")

    # Algorithm metrics
    algorithm_usage: Dict[str, int] = Field(
        default_factory=dict, description="Usage count by algorithm"
    )
    node_selection_count: Dict[str, int] = Field(
        default_factory=dict, description="Selection count by node"
    )

    # Circuit breaker metrics
    circuit_breaker_trips: int = Field(default=0, description="Circuit breaker trip count")
    failover_events: int = Field(default=0, description="Failover events")

    # Performance metrics
    decisions_per_second: float = Field(
        default=0.0, description="Load balancing decisions per second"
    )
    avg_decision_time_ms: float = Field(default=0.0, description="Average decision time")

    # Time range
    start_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Statistics start time"
    )
    end_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Statistics end time"
    )


class HealthCheckConfig(BaseModel):
    """Health check configuration."""

    model_config = ConfigDict(extra="forbid")

    # Basic settings
    enabled: bool = Field(default=True, description="Enable health checks")
    interval_seconds: float = Field(default=30.0, description="Health check interval")
    timeout_seconds: float = Field(default=10.0, description="Health check timeout")

    # Thresholds
    failure_threshold: int = Field(default=3, description="Failures before marking unhealthy")
    success_threshold: int = Field(default=2, description="Successes before marking healthy")

    # Check configuration
    check_type: str = Field(default="tcp", description="Health check type (tcp, http, https)")
    check_path: str = Field(default="/health", description="Health check path (for HTTP)")
    expected_status_codes: List[int] = Field(
        default_factory=lambda: [200], description="Expected HTTP status codes"
    )
    expected_response_body: Optional[str] = Field(
        default=None, description="Expected response body pattern"
    )

    # Advanced settings
    follow_redirects: bool = Field(default=False, description="Follow HTTP redirects")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    custom_headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")


@dataclass
class LoadBalancingSession:
    """Load balancing session for sticky sessions."""

    session_id: str
    client_ip: str
    assigned_node_id: str
    created_at: datetime
    last_accessed: datetime
    request_count: int = 0
    is_active: bool = True
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    # Enums
    "LoadBalancingAlgorithm",
    "NodeHealthStatus",
    "TrafficDirection",
    "FailoverStrategy",
    "CircuitBreakerState",
    # Core models
    "LoadBalancerNode",
    "LoadBalancingRule",
    "LoadBalancingDecisionRequest",
    "LoadBalancingDecisionResult",
    "LoadBalancerStatistics",
    "HealthCheckConfig",
    # Data classes
    "LoadBalancingSession",
]
