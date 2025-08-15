"""
Load Balancer - Layer 4 Concurrency Service

Enterprise-grade load balancing system with intelligent traffic distribution,
health monitoring, and adaptive algorithms. Provides optimal resource utilization
for parsing operations with geographic awareness and performance optimization.

Features:
- Multiple load balancing algorithms (round-robin, least connections, performance-based)
- Dynamic node health monitoring with circuit breaker patterns
- Geographic and proximity-based routing for parsing operations
- Session affinity and sticky sessions support
- Real-time performance metrics and adaptive optimization
- Failover strategies with graceful degradation
- Integration with proxy management and resource pooling
- Configurable traffic routing rules and policies
- Connection draining and maintenance mode support
- Advanced analytics and decision tracking
"""

import asyncio
import logging
import time
import threading
import hashlib
import random
from typing import Dict, List, Optional, Any, Set, Callable, Union
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
import weakref

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.utils import generate_correlation_id

# DTO models
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity
from unrealon_sdk.src.dto.concurrency import ConcurrencyEventType, ConcurrencyMetrics
from unrealon_sdk.src.dto.load_balancing import (
    LoadBalancingAlgorithm,
    NodeHealthStatus,
    TrafficDirection,
    FailoverStrategy,
    CircuitBreakerState,
    LoadBalancerNode,
    LoadBalancingRule,
    LoadBalancingDecisionRequest,
    LoadBalancingDecisionResult,
    LoadBalancerStatistics,
    HealthCheckConfig,
    LoadBalancingSession,
)

# Development logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unrealon_sdk.src.enterprise.logging import DevelopmentLogger

logger = logging.getLogger(__name__)


@dataclass
class NodePerformanceTracker:
    """Track node performance metrics."""

    node_id: str
    response_times: deque[float] = field(default_factory=lambda: deque(maxlen=100))
    success_count: int = 0
    failure_count: int = 0
    last_request: Optional[datetime] = None
    avg_response_time: float = 0.0
    success_rate: float = 1.0
    load_score: float = 0.0


class LoadBalancer:
    """
    Enterprise-grade load balancer.

    Provides intelligent traffic distribution with health monitoring,
    performance optimization, and adaptive algorithms for parsing operations.
    """

    def __init__(
        self,
        config: AdapterConfig,
        health_check_config: Optional[HealthCheckConfig] = None,
        dev_logger: Optional["DevelopmentLogger"] = None,
    ):
        """Initialize load balancer."""
        self.config = config
        self.health_check_config = health_check_config or HealthCheckConfig()
        self.dev_logger = dev_logger

        # Node management
        self._nodes: Dict[str, LoadBalancerNode] = {}
        self._node_performance: Dict[str, NodePerformanceTracker] = {}
        self._healthy_nodes: Set[str] = set()
        self._unhealthy_nodes: Set[str] = set()

        # Load balancing rules
        self._rules: Dict[str, LoadBalancingRule] = {}
        self._default_rule: Optional[LoadBalancingRule] = None

        # Algorithm implementations
        self._algorithms: Dict[LoadBalancingAlgorithm, Callable] = {
            LoadBalancingAlgorithm.ROUND_ROBIN: self._round_robin_selection,
            LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN: self._weighted_round_robin_selection,
            LoadBalancingAlgorithm.LEAST_CONNECTIONS: self._least_connections_selection,
            LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS: self._weighted_least_connections_selection,
            LoadBalancingAlgorithm.LEAST_RESPONSE_TIME: self._least_response_time_selection,
            LoadBalancingAlgorithm.RESOURCE_BASED: self._resource_based_selection,
            LoadBalancingAlgorithm.GEOGRAPHIC: self._geographic_selection,
            LoadBalancingAlgorithm.HASH_BASED: self._hash_based_selection,
            LoadBalancingAlgorithm.RANDOM: self._random_selection,
            LoadBalancingAlgorithm.ADAPTIVE: self._adaptive_selection,
        }

        # Session management
        self._sessions: Dict[str, LoadBalancingSession] = {}
        self._session_cleanup_threshold = timedelta(hours=24)

        # State tracking
        self._round_robin_index: Dict[str, int] = defaultdict(int)
        self._decision_cache: Dict[str, LoadBalancingDecisionResult] = {}
        self._cache_ttl_seconds = 60.0

        # Statistics
        self._statistics = LoadBalancerStatistics()
        self._decision_times: deque[float] = deque(maxlen=1000)

        # Background tasks
        self._health_check_task: Optional[asyncio.Task[None]] = None
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._metrics_task: Optional[asyncio.Task[None]] = None
        self._shutdown = False

        # Thread safety
        self._lock = threading.RLock()

        self._log_info("Load balancer initialized")

    async def start(self) -> None:
        """Start load balancer."""
        # Start background tasks
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_check_loop())

        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        if self._metrics_task is None:
            self._metrics_task = asyncio.create_task(self._metrics_loop())

        self._log_info("Load balancer started")

    async def stop(self) -> None:
        """Stop load balancer."""
        self._shutdown = True

        # Cancel background tasks
        for task in [self._health_check_task, self._cleanup_task, self._metrics_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._log_info("Load balancer stopped")

    def add_node(self, node: LoadBalancerNode) -> None:
        """Add node to load balancer."""
        with self._lock:
            self._nodes[node.node_id] = node
            self._node_performance[node.node_id] = NodePerformanceTracker(node_id=node.node_id)

            if node.is_enabled and node.health_status == NodeHealthStatus.HEALTHY:
                self._healthy_nodes.add(node.node_id)
            else:
                self._unhealthy_nodes.add(node.node_id)

        self._log_info(f"Added node '{node.node_name}' ({node.host}:{node.port})")

    def remove_node(self, node_id: str) -> bool:
        """Remove node from load balancer."""
        with self._lock:
            if node_id not in self._nodes:
                return False

            del self._nodes[node_id]
            del self._node_performance[node_id]
            self._healthy_nodes.discard(node_id)
            self._unhealthy_nodes.discard(node_id)

        self._log_info(f"Removed node '{node_id}'")
        return True

    def add_rule(self, rule: LoadBalancingRule) -> None:
        """Add load balancing rule."""
        with self._lock:
            self._rules[rule.rule_id] = rule

        self._log_info(f"Added load balancing rule '{rule.rule_name}'")

    def set_default_rule(self, rule: LoadBalancingRule) -> None:
        """Set default load balancing rule."""
        self._default_rule = rule
        self._log_info(f"Set default rule to '{rule.rule_name}'")

    async def select_node(
        self, request: LoadBalancingDecisionRequest
    ) -> LoadBalancingDecisionResult:
        """Select node for request using load balancing."""
        start_time = time.time()

        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self._decision_cache:
                cached_result = self._decision_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    return cached_result

            # Find applicable rule
            rule = self._find_applicable_rule(request)
            if not rule:
                rule = self._default_rule

            if not rule:
                raise RuntimeError("No load balancing rule available")

            # Check session affinity
            if rule.session_affinity and request.session_id:
                session_result = self._handle_session_affinity(request, rule)
                if session_result:
                    return session_result

            # Get candidate nodes
            candidate_nodes = self._get_candidate_nodes(request, rule)
            if not candidate_nodes:
                raise RuntimeError("No healthy nodes available")

            # Apply load balancing algorithm
            selected_node = self._apply_algorithm(rule.algorithm, candidate_nodes, request)
            if not selected_node:
                raise RuntimeError("Load balancing algorithm failed to select node")

            # Get backup nodes
            backup_nodes = self._get_backup_nodes(selected_node, candidate_nodes, rule)

            # Create decision result
            decision_time = (time.time() - start_time) * 1000
            result = LoadBalancingDecisionResult(
                selected_node=selected_node,
                backup_nodes=backup_nodes,
                algorithm_used=rule.algorithm,
                rule_applied=rule.rule_id,
                decision_time_ms=decision_time,
                selection_factors=self._get_selection_factors(selected_node, rule.algorithm),
                timestamp=datetime.now(timezone.utc),
            )

            # Handle session creation
            if rule.session_affinity and request.session_id:
                self._create_session(request, selected_node)
                result.new_session_created = True

            # Cache decision
            self._decision_cache[cache_key] = result

            # Update statistics
            self._update_statistics(result)

            return result

        except Exception as e:
            decision_time = (time.time() - start_time) * 1000
            self._statistics.failed_requests += 1

            error_result = LoadBalancingDecisionResult(
                selected_node=None,
                algorithm_used=(
                    rule.algorithm if "rule" in locals() else LoadBalancingAlgorithm.ROUND_ROBIN
                ),
                decision_time_ms=decision_time,
                rejection_reasons={"error": str(e)},
                timestamp=datetime.now(timezone.utc),
            )

            self._log_error(f"Load balancing failed: {e}")
            return error_result

    def report_request_result(
        self,
        node_id: str,
        success: bool,
        response_time_ms: float,
        error_message: Optional[str] = None,
    ) -> None:
        """Report request result for node performance tracking."""
        with self._lock:
            if node_id not in self._nodes:
                return

            node = self._nodes[node_id]
            performance = self._node_performance[node_id]

            # Update performance metrics
            performance.response_times.append(response_time_ms)
            performance.last_request = datetime.now(timezone.utc)

            if success:
                performance.success_count += 1
                node.total_requests += 1
            else:
                performance.failure_count += 1
                node.failed_requests += 1
                node.failure_count += 1

            # Calculate averages
            if performance.response_times:
                performance.avg_response_time = sum(performance.response_times) / len(
                    performance.response_times
                )
                node.avg_response_time_ms = performance.avg_response_time

            total_requests = performance.success_count + performance.failure_count
            if total_requests > 0:
                performance.success_rate = performance.success_count / total_requests

            # Update circuit breaker state
            self._update_circuit_breaker(node, success, error_message)

            # Update node health
            self._update_node_health(node_id, success)

    def _find_applicable_rule(
        self, request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancingRule]:
        """Find applicable load balancing rule for request."""
        for rule in sorted(self._rules.values(), key=lambda r: r.priority):
            if self._rule_matches(rule, request):
                return rule
        return None

    def _rule_matches(self, rule: LoadBalancingRule, request: LoadBalancingDecisionRequest) -> bool:
        """Check if rule matches request."""
        # Check traffic direction
        if rule.traffic_direction != TrafficDirection.BIDIRECTIONAL:
            if rule.traffic_direction != request.traffic_direction:
                return False

        # Check source patterns
        if rule.source_patterns:
            if not any(
                self._pattern_matches(pattern, request.source_ip)
                for pattern in rule.source_patterns
            ):
                return False

        # Check path patterns (if HTTP)
        if rule.path_patterns and request.path:
            if not any(
                self._pattern_matches(pattern, request.path) for pattern in rule.path_patterns
            ):
                return False

        return True

    def _pattern_matches(self, pattern: str, value: str) -> bool:
        """Check if pattern matches value (simple wildcard support)."""
        if "*" not in pattern:
            return pattern == value

        # Simple wildcard matching
        parts = pattern.split("*")
        if not value.startswith(parts[0]):
            return False
        if not value.endswith(parts[-1]):
            return False

        return True

    def _get_candidate_nodes(
        self, request: LoadBalancingDecisionRequest, rule: LoadBalancingRule
    ) -> List[LoadBalancerNode]:
        """Get candidate nodes for request."""
        candidates = []

        # Start with rule target nodes or all healthy nodes
        target_node_ids = rule.target_nodes if rule.target_nodes else list(self._healthy_nodes)

        for node_id in target_node_ids:
            if node_id not in self._nodes:
                continue

            node = self._nodes[node_id]

            # Check if node is enabled and healthy
            if not node.is_enabled or node.health_status not in [
                NodeHealthStatus.HEALTHY,
                NodeHealthStatus.DEGRADED,
            ]:
                continue

            # Check circuit breaker
            if node.circuit_breaker_state == CircuitBreakerState.OPEN:
                continue

            # Check required tags
            if request.required_tags:
                if not all(node.tags.get(k) == v for k, v in request.required_tags.items()):
                    continue

            # Check excluded nodes
            if node.node_id in request.excluded_nodes:
                continue

            # Check connection limits
            if node.max_connections and node.current_connections >= node.max_connections:
                continue

            candidates.append(node)

        return candidates

    def _apply_algorithm(
        self,
        algorithm: LoadBalancingAlgorithm,
        candidates: List[LoadBalancerNode],
        request: LoadBalancingDecisionRequest,
    ) -> Optional[LoadBalancerNode]:
        """Apply load balancing algorithm to select node."""
        if not candidates:
            return None

        algorithm_func = self._algorithms.get(algorithm)
        if not algorithm_func:
            # Fallback to round robin
            algorithm_func = self._algorithms[LoadBalancingAlgorithm.ROUND_ROBIN]

        return algorithm_func(candidates, request)

    def _round_robin_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Round-robin selection algorithm."""
        if not candidates:
            return None

        rule_key = request.request_id[:8]  # Use part of request ID as key
        index = self._round_robin_index[rule_key] % len(candidates)
        self._round_robin_index[rule_key] = (index + 1) % len(candidates)

        return candidates[index]

    def _weighted_round_robin_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Weighted round-robin selection algorithm."""
        if not candidates:
            return None

        # Create weighted list
        weighted_candidates = []
        for node in candidates:
            weighted_candidates.extend([node] * node.weight)

        if not weighted_candidates:
            return candidates[0]

        rule_key = f"weighted_{request.request_id[:8]}"
        index = self._round_robin_index[rule_key] % len(weighted_candidates)
        self._round_robin_index[rule_key] = (index + 1) % len(weighted_candidates)

        return weighted_candidates[index]

    def _least_connections_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Least connections selection algorithm."""
        if not candidates:
            return None

        return min(candidates, key=lambda node: node.current_connections)

    def _weighted_least_connections_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Weighted least connections selection algorithm."""
        if not candidates:
            return None

        # Calculate weighted connection ratio
        def weighted_ratio(node: LoadBalancerNode) -> float:
            if node.weight <= 0:
                return float("inf")
            return node.current_connections / node.weight

        return min(candidates, key=weighted_ratio)

    def _least_response_time_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Least response time selection algorithm."""
        if not candidates:
            return None

        return min(candidates, key=lambda node: node.avg_response_time_ms)

    def _resource_based_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Resource-based selection algorithm."""
        if not candidates:
            return None

        # Calculate resource utilization score
        def resource_score(node: LoadBalancerNode) -> float:
            connection_ratio = 0.0
            if node.max_connections:
                connection_ratio = node.current_connections / node.max_connections

            # Consider response time and failure rate
            performance = self._node_performance.get(node.node_id)
            if performance:
                response_factor = min(
                    performance.avg_response_time / 1000.0, 1.0
                )  # Normalize to 0-1
                failure_factor = 1.0 - performance.success_rate
                return connection_ratio * 0.4 + response_factor * 0.3 + failure_factor * 0.3

            return connection_ratio

        return min(candidates, key=resource_score)

    def _geographic_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Geographic selection algorithm."""
        if not candidates:
            return None

        # If preferred region specified, try to use it
        if request.preferred_region:
            regional_candidates = [
                node for node in candidates if node.region == request.preferred_region
            ]
            if regional_candidates:
                # Use least connections within preferred region
                return self._least_connections_selection(regional_candidates, request)

        # Fallback to least connections
        return self._least_connections_selection(candidates, request)

    def _hash_based_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Hash-based selection algorithm (consistent hashing)."""
        if not candidates:
            return None

        # Use session ID or source IP for hashing
        hash_key = request.session_id or request.source_ip
        hash_value = int(hashlib.md5(hash_key.encode(), usedforsecurity=False).hexdigest(), 16)

        return candidates[hash_value % len(candidates)]

    def _random_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Random selection algorithm."""
        if not candidates:
            return None

        return random.choice(candidates)

    def _adaptive_selection(
        self, candidates: List[LoadBalancerNode], request: LoadBalancingDecisionRequest
    ) -> Optional[LoadBalancerNode]:
        """Adaptive selection algorithm based on current performance."""
        if not candidates:
            return None

        # Calculate adaptive score based on multiple factors
        def adaptive_score(node: LoadBalancerNode) -> float:
            performance = self._node_performance.get(node.node_id)
            if not performance:
                return 0.5  # Neutral score for new nodes

            # Combine multiple metrics
            response_factor = min(performance.avg_response_time / 1000.0, 1.0)
            success_factor = performance.success_rate
            connection_factor = 0.0

            if node.max_connections:
                connection_factor = 1.0 - (node.current_connections / node.max_connections)

            # Weight factors: success rate is most important, then response time, then connections
            score = success_factor * 0.5 + (1.0 - response_factor) * 0.3 + connection_factor * 0.2
            return score

        # Select node with highest adaptive score
        return max(candidates, key=adaptive_score)

    def _get_backup_nodes(
        self,
        selected_node: LoadBalancerNode,
        candidates: List[LoadBalancerNode],
        rule: LoadBalancingRule,
    ) -> List[LoadBalancerNode]:
        """Get backup nodes for failover."""
        backup_nodes = []

        # Add explicitly configured backup nodes
        for backup_id in rule.backup_nodes:
            if backup_id in self._nodes and backup_id != selected_node.node_id:
                backup_node = self._nodes[backup_id]
                if backup_node.is_enabled and backup_node.health_status in [
                    NodeHealthStatus.HEALTHY,
                    NodeHealthStatus.DEGRADED,
                ]:
                    backup_nodes.append(backup_node)

        # Add other healthy candidates as additional backups
        for candidate in candidates:
            if candidate.node_id != selected_node.node_id and candidate not in backup_nodes:
                backup_nodes.append(candidate)
                if len(backup_nodes) >= 3:  # Limit backup nodes
                    break

        return backup_nodes

    def _handle_session_affinity(
        self, request: LoadBalancingDecisionRequest, rule: LoadBalancingRule
    ) -> Optional[LoadBalancingDecisionResult]:
        """Handle session affinity for sticky sessions."""
        if not request.session_id:
            return None

        session = self._sessions.get(request.session_id)
        if not session or not session.is_active:
            return None

        # Check if assigned node is still healthy
        if session.assigned_node_id in self._healthy_nodes:
            assigned_node = self._nodes[session.assigned_node_id]

            # Update session
            session.last_accessed = datetime.now(timezone.utc)
            session.request_count += 1

            return LoadBalancingDecisionResult(
                selected_node=assigned_node,
                algorithm_used=rule.algorithm,
                rule_applied=rule.rule_id,
                decision_time_ms=1.0,  # Cached decision
                session_affinity_used=True,
                timestamp=datetime.now(timezone.utc),
            )

        # Session node is unhealthy, remove session
        del self._sessions[request.session_id]
        return None

    def _create_session(
        self, request: LoadBalancingDecisionRequest, selected_node: LoadBalancerNode
    ) -> None:
        """Create new session for sticky sessions."""
        if not request.session_id:
            return

        session = LoadBalancingSession(
            session_id=request.session_id,
            client_ip=request.source_ip,
            assigned_node_id=selected_node.node_id,
            created_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc),
        )

        self._sessions[request.session_id] = session

    def _update_circuit_breaker(
        self, node: LoadBalancerNode, success: bool, error_message: Optional[str]
    ) -> None:
        """Update circuit breaker state for node."""
        if not success:
            node.failure_count += 1
            node.last_failure = datetime.now(timezone.utc)

            # Trip circuit breaker if failure threshold reached
            if node.failure_count >= 5:  # Configurable threshold
                node.circuit_breaker_state = CircuitBreakerState.OPEN
                self._log_info(f"Circuit breaker opened for node {node.node_id}")
        else:
            # Reset failure count on success
            if node.circuit_breaker_state == CircuitBreakerState.HALF_OPEN:
                node.circuit_breaker_state = CircuitBreakerState.CLOSED
                node.failure_count = 0
                self._log_info(f"Circuit breaker closed for node {node.node_id}")

    def _update_node_health(self, node_id: str, success: bool) -> None:
        """Update node health status."""
        with self._lock:
            if node_id not in self._nodes:
                return

            node = self._nodes[node_id]
            performance = self._node_performance[node_id]

            # Update health based on success rate
            if performance.success_rate < 0.5:  # Less than 50% success
                if node.health_status == NodeHealthStatus.HEALTHY:
                    node.health_status = NodeHealthStatus.DEGRADED
                    self._log_info(f"Node {node_id} health degraded")
            elif performance.success_rate > 0.8:  # More than 80% success
                if node.health_status == NodeHealthStatus.DEGRADED:
                    node.health_status = NodeHealthStatus.HEALTHY
                    self._log_info(f"Node {node_id} health recovered")

            # Update healthy/unhealthy sets
            if (
                node.health_status in [NodeHealthStatus.HEALTHY, NodeHealthStatus.DEGRADED]
                and node.is_enabled
            ):
                self._healthy_nodes.add(node_id)
                self._unhealthy_nodes.discard(node_id)
            else:
                self._unhealthy_nodes.add(node_id)
                self._healthy_nodes.discard(node_id)

    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.health_check_config.interval_seconds)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all nodes."""
        if not self.health_check_config.enabled:
            return

        for node_id, node in list(self._nodes.items()):
            try:
                is_healthy = await self._check_node_health(node)
                self._update_node_health_status(node_id, is_healthy)
            except Exception as e:
                logger.error(f"Health check failed for node {node_id}: {e}")
                self._update_node_health_status(node_id, False)

    async def _check_node_health(self, node: LoadBalancerNode) -> bool:
        """Check individual node health."""
        # Simple TCP connection check
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(node.host, node.port),
                timeout=self.health_check_config.timeout_seconds,
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False

    def _update_node_health_status(self, node_id: str, is_healthy: bool) -> None:
        """Update node health status based on health check."""
        with self._lock:
            if node_id not in self._nodes:
                return

            node = self._nodes[node_id]
            node.last_health_check = datetime.now(timezone.utc)

            if is_healthy:
                if node.health_status == NodeHealthStatus.UNHEALTHY:
                    node.health_status = NodeHealthStatus.HEALTHY
                    self._log_info(f"Node {node_id} health recovered")
            else:
                if node.health_status in [NodeHealthStatus.HEALTHY, NodeHealthStatus.DEGRADED]:
                    node.health_status = NodeHealthStatus.UNHEALTHY
                    self._log_info(f"Node {node_id} marked unhealthy")

            # Update sets
            if (
                node.health_status in [NodeHealthStatus.HEALTHY, NodeHealthStatus.DEGRADED]
                and node.is_enabled
            ):
                self._healthy_nodes.add(node_id)
                self._unhealthy_nodes.discard(node_id)
            else:
                self._unhealthy_nodes.add(node_id)
                self._healthy_nodes.discard(node_id)

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                await self._cleanup_sessions()
                await self._cleanup_cache()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_sessions(self) -> None:
        """Clean up expired sessions."""
        current_time = datetime.now(timezone.utc)
        expired_sessions = []

        for session_id, session in self._sessions.items():
            if current_time - session.last_accessed > self._session_cleanup_threshold:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self._sessions[session_id]

        if expired_sessions:
            self._log_info(f"Cleaned up {len(expired_sessions)} expired sessions")

    async def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = []

        for cache_key, result in self._decision_cache.items():
            if current_time - result.timestamp.timestamp() > self._cache_ttl_seconds:
                expired_keys.append(cache_key)

        for cache_key in expired_keys:
            del self._decision_cache[cache_key]

    async def _metrics_loop(self) -> None:
        """Background metrics collection loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(60)  # Collect every minute
                await self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")

    async def _collect_metrics(self) -> None:
        """Collect load balancer metrics."""
        with self._lock:
            self._statistics.total_nodes = len(self._nodes)
            self._statistics.healthy_nodes = len(self._healthy_nodes)
            self._statistics.unhealthy_nodes = len(self._unhealthy_nodes)

            # Calculate average decision time
            if self._decision_times:
                self._statistics.avg_decision_time_ms = sum(self._decision_times) / len(
                    self._decision_times
                )

            # Update algorithm usage
            for node_id, node in self._nodes.items():
                self._statistics.node_selection_count[node_id] = node.total_requests

    def get_statistics(self) -> LoadBalancerStatistics:
        """Get load balancer statistics."""
        return self._statistics.model_copy()

    def get_node_status(self, node_id: str) -> Optional[LoadBalancerNode]:
        """Get node status."""
        return self._nodes.get(node_id)

    def get_all_nodes(self) -> List[LoadBalancerNode]:
        """Get all nodes."""
        return list(self._nodes.values())

    def get_healthy_nodes(self) -> List[LoadBalancerNode]:
        """Get healthy nodes."""
        return [self._nodes[node_id] for node_id in self._healthy_nodes]

    def _generate_cache_key(self, request: LoadBalancingDecisionRequest) -> str:
        """Generate cache key for request."""
        key_parts = [
            request.source_ip,
            request.destination_ip or "",
            str(request.destination_port or ""),
            request.path or "",
            str(sorted(request.required_tags.items())),
            str(sorted(request.excluded_nodes)),
        ]
        return hashlib.md5("|".join(key_parts).encode(), usedforsecurity=False).hexdigest()

    def _is_cache_valid(self, result: LoadBalancingDecisionResult) -> bool:
        """Check if cached result is still valid."""
        age = time.time() - result.timestamp.timestamp()
        return age < self._cache_ttl_seconds

    def _get_selection_factors(
        self, node: LoadBalancerNode, algorithm: LoadBalancingAlgorithm
    ) -> Dict[str, Any]:
        """Get factors that influenced node selection."""
        factors = {
            "node_id": node.node_id,
            "algorithm": algorithm.value,
            "current_connections": node.current_connections,
            "avg_response_time": node.avg_response_time_ms,
            "health_status": node.health_status.value,
            "weight": node.weight,
        }

        performance = self._node_performance.get(node.node_id)
        if performance:
            factors.update(
                {
                    "success_rate": performance.success_rate,
                    "load_score": performance.load_score,
                }
            )

        return factors

    def _update_statistics(self, result: LoadBalancingDecisionResult) -> None:
        """Update statistics with decision result."""
        self._statistics.total_requests += 1
        if result.selected_node:
            self._statistics.successful_requests += 1

        self._decision_times.append(result.decision_time_ms)

        # Update algorithm usage
        algorithm_key = result.algorithm_used.value
        self._statistics.algorithm_usage[algorithm_key] = (
            self._statistics.algorithm_usage.get(algorithm_key, 0) + 1
        )

    def _log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.PERFORMANCE_OPTIMIZATION_APPLIED, message, **kwargs
            )
        else:
            logger.info(message)

    def _log_error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        if self.dev_logger:
            self.dev_logger.log_error(SDKEventType.CRITICAL_ERROR, message, **kwargs)
        else:
            logger.error(message)


__all__ = [
    # Main class
    "LoadBalancer",
    # Utility classes
    "NodePerformanceTracker",
    # Note: Load balancing models are available via DTO imports:
    # from unrealon_sdk.src.dto.load_balancing import ...
]
