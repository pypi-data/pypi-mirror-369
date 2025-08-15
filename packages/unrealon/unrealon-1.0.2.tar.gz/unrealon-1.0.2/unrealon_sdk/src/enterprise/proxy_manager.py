"""
ProxyManager - Intelligent Proxy Management for Enterprise Parsing

Layer 3: Infrastructure Services - Core proxy management with:
- Geographic rotation and health checking
- Automatic failover and recovery
- Integration with multiple proxy providers
- Performance monitoring and optimization
- Type-safe operations with Pydantic v2

Enterprise Features:
- Smart proxy rotation based on success rates
- Geographic targeting for region-specific parsing
- Health monitoring with automatic blacklisting
- Provider failover and load balancing
- Real-time proxy performance metrics
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import random

# Pydantic v2 for all data models
from pydantic import BaseModel, Field, ConfigDict

# Auto-generated models from the API - HTTP models
from unrealon_sdk.src.clients.python_http.models import (
    ProxyListResponse,
    ProxyUsageStatsResponse,
    ProxyRotationRequest,
    ProxyPurchaseRequest,
    ProxyBlockRequest,
    ProxyEndpointResponse,
    ProxyResponse,
    ErrorResponse,
)

# Auto-generated models from WebSocket types
from unrealon_sdk.src.clients.python_websocket.types import (
    ProxyProvider,
    ProxyStatus,
    ProxyProtocol,
    ProxyRotationStrategy,
    Proxy,
    ProxyEndpoint,
    ProxyCredentials,
    ProxyUsageStats,
    ProxyAllocation,
    ProxySummary,
    ProxyDetails,
    ProxyStatistics,
)

# Import auto-generated proxy management services
from unrealon_sdk.src.clients.python_http.services.async_ProxyManagement_service import (
    list_proxies_api_v1_proxies__get,
    get_proxy_statistics_api_v1_proxies_statistics_get,
    record_proxy_usage_api_v1_proxies__proxy_id__usage_post,
    report_blocked_proxy_api_v1_proxies_rotation_block_post,
    request_proxy_rotation_api_v1_proxies_rotation_request_post,
)

# Core SDK components
from unrealon_sdk.src.core.config import AdapterConfig, ProxyConfig
from unrealon_sdk.src.core.exceptions import ProxyError, ConnectionError
from unrealon_sdk.src.utils import generate_correlation_id

# Development logging
from .logging.development import (
    get_development_logger,
    SDKEventType,
    SDKContext,
    track_development_operation,
)

logger = logging.getLogger(__name__)


# Use auto-generated ProxyUsageStats but extend with helper methods
class ExtendedProxyUsageStats(ProxyUsageStats):
    """Extended proxy usage stats with helper methods."""

    @property
    def success_rate_percentage(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def is_healthy(self) -> bool:
        """Check if proxy usage indicates healthy status."""
        return self.consecutive_failures < 3 and self.success_rate >= 70.0


# Extended proxy model with management features
class ManagedProxy(Proxy):
    """Extended Proxy model with management features."""

    # Management fields
    is_active: bool = Field(default=True, description="Whether proxy is currently active")
    last_health_check: Optional[datetime] = Field(
        default=None, description="Last health check timestamp"
    )
    blacklisted_until: Optional[datetime] = Field(
        default=None, description="Blacklist expiration time"
    )

    @property
    def proxy_url(self) -> str:
        """Generate proxy URL for HTTP clients."""
        if self.credentials:
            auth = f"{self.credentials.username}:{self.credentials.password}@"
        else:
            auth = ""
        protocol = (
            self.endpoint.protocol.value
            if hasattr(self.endpoint.protocol, "value")
            else str(self.endpoint.protocol)
        )
        return f"{protocol}://{auth}{self.endpoint.host}:{self.endpoint.port}"

    @property
    def identifier(self) -> str:
        """Unique identifier for this proxy."""
        return f"{self.endpoint.host}:{self.endpoint.port}"

    @property
    def is_blacklisted(self) -> bool:
        """Check if proxy is currently blacklisted."""
        if self.blacklisted_until is None:
            return False
        return datetime.now(timezone.utc) < self.blacklisted_until


class ProxyPool:
    """Manages a pool of proxy endpoints with intelligent selection using auto-generated models."""

    def __init__(self, strategy: ProxyRotationStrategy = ProxyRotationStrategy.SUCCESS_RATE):
        self.proxies: Dict[str, ManagedProxy] = {}
        self.strategy = strategy
        self._rotation_index = 0

    def add_proxy(self, proxy: ManagedProxy) -> None:
        """Add a proxy to the pool."""
        self.proxies[proxy.identifier] = proxy
        logger.debug(f"Added proxy {proxy.identifier} to pool")

    def remove_proxy(self, proxy_id: str) -> None:
        """Remove a proxy from the pool."""
        if proxy_id in self.proxies:
            del self.proxies[proxy_id]
            logger.debug(f"Removed proxy {proxy_id} from pool")

    def blacklist_proxy(self, proxy_id: str, duration_minutes: int = 30) -> None:
        """Temporarily blacklist a proxy."""
        if proxy_id in self.proxies:
            blacklist_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
            self.proxies[proxy_id].blacklisted_until = blacklist_until
            self.proxies[proxy_id].is_active = False

        logger.warning(f"Blacklisted proxy {proxy_id} for {duration_minutes} minutes")

        # Schedule automatic removal from blacklist
        asyncio.create_task(self._remove_from_blacklist_later(proxy_id, duration_minutes))

    async def _remove_from_blacklist_later(self, proxy_id: str, minutes: int) -> None:
        """Remove proxy from blacklist after specified time."""
        await asyncio.sleep(minutes * 60)
        if proxy_id in self.proxies:
            self.proxies[proxy_id].blacklisted_until = None
            self.proxies[proxy_id].is_active = True
        logger.info(f"Proxy {proxy_id} removed from blacklist")

    def get_available_proxies(self) -> List[ManagedProxy]:
        """Get list of available (non-blacklisted, healthy) proxies."""
        return [
            proxy
            for proxy in self.proxies.values()
            if proxy.is_active and not proxy.is_blacklisted and proxy.usage_stats.is_healthy
        ]

    def select_proxy(self, region: Optional[str] = None) -> Optional[ManagedProxy]:
        """Select best proxy based on strategy."""
        available = self.get_available_proxies()

        if not available:
            logger.warning("No available proxies in pool")
            return None

        # Filter by region if specified
        if region:
            regional = [p for p in available if p.region == region or p.country == region]
            if regional:
                available = regional

        if self.strategy == ProxyRotationStrategy.ROUND_ROBIN:
            return self._select_round_robin(available)
        elif self.strategy == ProxyRotationStrategy.SUCCESS_RATE:
            return self._select_by_success_rate(available)
        elif self.strategy == ProxyRotationStrategy.WEIGHTED_RANDOM:
            return self._select_weighted_random(available)
        elif self.strategy == ProxyRotationStrategy.LEAST_FAILURES:
            return self._select_least_failures(available)
        elif self.strategy == ProxyRotationStrategy.LEAST_USED:
            return self._select_least_used(available)
        else:
            return available[0]  # Fallback

    def _select_round_robin(self, available: List[ManagedProxy]) -> ManagedProxy:
        """Round-robin selection."""
        proxy = available[self._rotation_index % len(available)]
        self._rotation_index += 1
        return proxy

    def _select_by_success_rate(self, available: List[ManagedProxy]) -> ManagedProxy:
        """Select proxy with highest success rate."""
        return max(available, key=lambda p: p.usage_stats.success_rate)

    def _select_weighted_random(self, available: List[ManagedProxy]) -> ManagedProxy:
        """Weighted random selection based on success rate."""
        weights = [max(p.usage_stats.success_rate, 0.1) for p in available]
        return random.choices(available, weights=weights)[0]

    def _select_least_failures(self, available: List[ManagedProxy]) -> ManagedProxy:
        """Select proxy with least consecutive failures."""
        return min(available, key=lambda p: p.usage_stats.consecutive_failures)

    def _select_least_used(self, available: List[ManagedProxy]) -> ManagedProxy:
        """Select proxy used least recently."""

        def last_used_timestamp(proxy: ManagedProxy) -> float:
            if proxy.usage_stats.last_used_at:
                # Convert string timestamp to comparable format
                try:
                    dt = datetime.fromisoformat(
                        proxy.usage_stats.last_used_at.replace("Z", "+00:00")
                    )
                    return dt.timestamp()
                except:
                    return 0.0
            return 0.0

        return min(available, key=last_used_timestamp)


class ProxyManager:
    """
    Enterprise-grade proxy management with intelligent rotation and health monitoring.

    Features:
    - Multiple proxy provider integration
    - Smart rotation strategies
    - Health monitoring and automatic failover
    - Performance metrics and optimization
    - Geographic targeting
    """

    def __init__(self, config: AdapterConfig):
        """
        Initialize ProxyManager with configuration.

        Args:
            config: Adapter configuration containing proxy settings
        """
        self.config = config
        self.proxy_config = config.proxy_config
        self.logger = logger

        # Development logging
        self.dev_logger = get_development_logger()
        if self.dev_logger:
            self.dev_logger.set_component_context("ProxyManager")
            self.dev_logger.log_info(
                SDKEventType.PROXY_MANAGER_INITIALIZED,
                f"ProxyManager initialization started with strategy: {self.proxy_config.rotation_strategy}",
                context=SDKContext(
                    component_name="ProxyManager",
                    metadata={
                        "rotation_strategy": self.proxy_config.rotation_strategy,
                        "enabled": self.proxy_config.enabled,
                        "max_retries": self.proxy_config.max_retries,
                    },
                ),
            )

        # Initialize proxy pool with configured strategy
        strategy = ProxyRotationStrategy(self.proxy_config.rotation_strategy)
        self.pool = ProxyPool(strategy)

        # Health monitoring
        self._health_check_interval = 300  # 5 minutes
        self._health_check_task: Optional[asyncio.Task] = None

        # Statistics
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0

        # HTTP client for proxy API calls (will be injected)
        self._http_client = None

        self.logger.info(f"ProxyManager initialized with strategy: {strategy.value}")

        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.COMPONENT_CREATED,
                "ProxyManager initialization completed successfully",
                success=True,
                context=SDKContext(component_name="ProxyManager"),
            )

    async def initialize(self, http_client) -> None:
        """Initialize proxy manager with HTTP client."""
        self._http_client = http_client

        if self.proxy_config.enabled:
            await self._load_initial_proxies()
            await self._start_health_monitoring()

        self.logger.info("ProxyManager initialization complete")

    async def shutdown(self) -> None:
        """Shutdown proxy manager and cleanup resources."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        self.logger.info("ProxyManager shutdown complete")

    async def _load_initial_proxies(self) -> None:
        """Load initial proxy list from configured providers using real API."""
        try:
            if not self._http_client:
                raise ProxyError("HTTP client not initialized")

            self.logger.info("Loading initial proxy list from providers via API...")

            # Call the real proxy list API
            proxy_list_response = await list_proxies_api_v1_proxies__get(
                healthy_only=True, limit=100, api_config_override=self._http_client._api_config
            )

            if not proxy_list_response or not proxy_list_response.items:
                self.logger.warning("No proxies returned from API")
                return

            # Convert API response to ManagedProxy objects
            for proxy_response in proxy_list_response.items:
                managed_proxy = self._convert_api_proxy_to_managed(proxy_response)
                self.pool.add_proxy(managed_proxy)

            self.logger.info(f"Loaded {len(proxy_list_response.items)} proxies into pool")

        except Exception as e:
            self.logger.error(f"Failed to load initial proxies: {e}")
            raise ProxyError(f"Failed to initialize proxy pool: {e}")

    def _convert_api_proxy_to_managed(self, proxy_response: ProxyResponse) -> ManagedProxy:
        """Convert API ProxyResponse to ManagedProxy."""
        return ManagedProxy(
            proxy_id=proxy_response.proxy_id,
            provider=proxy_response.provider,
            provider_proxy_id=proxy_response.provider_proxy_id,
            endpoint=ProxyEndpoint(
                host=proxy_response.endpoint.host,
                port=proxy_response.endpoint.port,
                protocol=ProxyProtocol(proxy_response.endpoint.protocol),
            ),
            credentials=(
                ProxyCredentials(username="", password="")  # Will be populated from provider config
                if proxy_response.endpoint.connection_string
                else None
            ),
            country=proxy_response.country or "Unknown",
            region=proxy_response.region,
            city=proxy_response.city,
            status=ProxyStatus(proxy_response.status),
            created_at=proxy_response.created_at,
            expires_at=proxy_response.expires_at,
            last_validated_at=None,  # Not in API response
            usage_stats=ExtendedProxyUsageStats(
                total_requests=proxy_response.usage_stats.total_requests,
                successful_requests=proxy_response.usage_stats.successful_requests,
                failed_requests=proxy_response.usage_stats.failed_requests,
                consecutive_failures=proxy_response.usage_stats.consecutive_failures,
                avg_response_time_ms=proxy_response.usage_stats.avg_response_time_ms or 0.0,
                last_used_at=proxy_response.usage_stats.last_used_at,
                blocked_count=0,  # Not in current API
            ),
            shared=False,  # Default
            tags=proxy_response.tags or [],
            metadata=proxy_response.metadata or {},
            # Management fields
            is_active=proxy_response.is_healthy or False,
            last_health_check=datetime.now(timezone.utc),
            blacklisted_until=None,
        )

    async def _start_health_monitoring(self) -> None:
        """Start background health monitoring task."""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_monitor_loop())
            self.logger.info("Started proxy health monitoring")

    async def _health_monitor_loop(self) -> None:
        """Background task for monitoring proxy health."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all proxies."""
        self.logger.debug("Performing proxy health checks...")

        for proxy_id, proxy in self.pool.proxies.items():
            try:
                await self._check_proxy_health(proxy)
            except Exception as e:
                self.logger.warning(f"Health check failed for proxy {proxy_id}: {e}")
                proxy.metrics.health_status = ProxyHealthStatus.FAILING

    async def _check_proxy_health(self, proxy: ProxyEndpoint) -> None:
        """Check health of a specific proxy."""
        # Simple health check - in production this would make actual HTTP requests
        proxy.last_health_check = datetime.now()

        # Simulate health check logic
        if proxy.metrics.consecutive_failures >= 5:
            proxy.metrics.health_status = ProxyHealthStatus.BLOCKED
        elif proxy.metrics.consecutive_failures >= 3:
            proxy.metrics.health_status = ProxyHealthStatus.FAILING
        elif proxy.metrics.success_rate < 50:
            proxy.metrics.health_status = ProxyHealthStatus.DEGRADED
        else:
            proxy.metrics.health_status = ProxyHealthStatus.HEALTHY

    @track_development_operation("Proxy Selection", SDKEventType.PROXY_ALLOCATED)
    def get_proxy(self, region: Optional[str] = None) -> Optional[ManagedProxy]:
        """
        Get next proxy for use based on rotation strategy.

        Args:
            region: Optional region preference for geographic routing

        Returns:
            ManagedProxy if available, None if no proxies available
        """
        if not self.proxy_config.enabled:
            if self.dev_logger:
                self.dev_logger.log_warning(
                    SDKEventType.PROXY_ALLOCATED,
                    "Proxy allocation requested but proxy management is disabled",
                    context=SDKContext(component_name="ProxyManager"),
                )
            return None

        proxy = self.pool.select_proxy(region)
        if proxy:
            # Update last used timestamp
            proxy.usage_stats.last_used_at = datetime.now(timezone.utc).isoformat()
            self.logger.debug(f"Selected proxy {proxy.identifier} for use")

            if self.dev_logger:
                self.dev_logger.log_info(
                    SDKEventType.PROXY_ALLOCATED,
                    f"Proxy allocated: {proxy.identifier}",
                    context=SDKContext(
                        component_name="ProxyManager",
                        metadata={
                            "proxy_id": proxy.proxy_id,
                            "region": proxy.region,
                            "country": proxy.country,
                            "provider": (
                                proxy.provider.value
                                if hasattr(proxy.provider, "value")
                                else str(proxy.provider)
                            ),
                            "success_rate": proxy.usage_stats.success_rate,
                            "requested_region": region,
                        },
                    ),
                )
        else:
            if self.dev_logger:
                self.dev_logger.log_error(
                    SDKEventType.PROXY_ALLOCATED,
                    f"No available proxies for region: {region or 'any'}",
                    context=SDKContext(
                        component_name="ProxyManager",
                        metadata={
                            "requested_region": region,
                            "total_proxies": len(self.pool.proxies),
                            "available_proxies": len(self.pool.get_available_proxies()),
                        },
                    ),
                )

        return proxy

    async def record_success(self, proxy: ManagedProxy, response_time_ms: float) -> None:
        """Record successful proxy usage and sync with API."""
        # Update local stats
        proxy.usage_stats.total_requests += 1
        proxy.usage_stats.successful_requests += 1
        proxy.usage_stats.consecutive_failures = 0

        # Update rolling average response time
        if proxy.usage_stats.avg_response_time_ms == 0:
            proxy.usage_stats.avg_response_time_ms = response_time_ms
        else:
            # Simple moving average
            proxy.usage_stats.avg_response_time_ms = (
                proxy.usage_stats.avg_response_time_ms * 0.8 + response_time_ms * 0.2
            )

        proxy.usage_stats.last_used_at = datetime.now(timezone.utc).isoformat()

        # Update global stats
        self._successful_requests += 1
        self._total_requests += 1

        # Sync with API (non-blocking)
        if self._http_client:
            try:
                # Use auto-generated API service
                from unrealon_sdk.src.clients.python_http.models.ProxyUsageRequest import (
                    ProxyUsageRequest,
                )

                usage_request = ProxyUsageRequest(
                    successful=True,
                    response_time_ms=response_time_ms,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                await record_proxy_usage_api_v1_proxies__proxy_id__usage_post(
                    proxy_id=proxy.proxy_id,
                    body=usage_request,
                    api_config_override=self._http_client._api_config,
                )
            except Exception as e:
                self.logger.warning(f"Failed to sync success with API: {e}")

        self.logger.debug(
            f"Recorded success for proxy {proxy.identifier} ({response_time_ms:.2f}ms)"
        )

        if self.dev_logger:
            self.dev_logger.log_performance_metric(
                "proxy_response_time",
                response_time_ms,
                "ms",
                threshold=5000.0,  # 5 second threshold
                context=SDKContext(
                    component_name="ProxyManager",
                    metadata={
                        "proxy_id": proxy.proxy_id,
                        "proxy_identifier": proxy.identifier,
                        "success_rate": proxy.usage_stats.success_rate,
                        "total_requests": proxy.usage_stats.total_requests,
                    },
                ),
            )

    async def record_failure(self, proxy: ManagedProxy, error: str) -> None:
        """Record failed proxy usage and sync with API."""
        # Update local stats
        proxy.usage_stats.total_requests += 1
        proxy.usage_stats.failed_requests += 1
        proxy.usage_stats.consecutive_failures += 1
        proxy.usage_stats.last_used_at = datetime.now(timezone.utc).isoformat()

        # Update global stats
        self._failed_requests += 1
        self._total_requests += 1

        # Auto-blacklist if too many consecutive failures
        if proxy.usage_stats.consecutive_failures >= 5:
            self.pool.blacklist_proxy(proxy.identifier, duration_minutes=60)

            # Report blocked proxy to API
            if self._http_client:
                try:
                    block_request = ProxyBlockRequest(
                        proxy_id=proxy.proxy_id,
                        reason=f"Consecutive failures: {error}",
                        block_duration_minutes=60,
                    )

                    await report_blocked_proxy_api_v1_proxies_rotation_block_post(
                        body=block_request, api_config_override=self._http_client._api_config
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to report blocked proxy to API: {e}")

        # Sync usage with API (non-blocking)
        if self._http_client:
            try:
                from unrealon_sdk.src.clients.python_http.models.ProxyUsageRequest import (
                    ProxyUsageRequest,
                )

                usage_request = ProxyUsageRequest(
                    successful=False,
                    error_message=error,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                await record_proxy_usage_api_v1_proxies__proxy_id__usage_post(
                    proxy_id=proxy.proxy_id,
                    body=usage_request,
                    api_config_override=self._http_client._api_config,
                )
            except Exception as e:
                self.logger.warning(f"Failed to sync failure with API: {e}")

        self.logger.warning(f"Recorded failure for proxy {proxy.identifier}: {error}")

    def get_statistics(self) -> ProxyStatistics:
        """Get comprehensive proxy usage statistics using auto-generated model."""
        available_proxies = self.pool.get_available_proxies()
        blacklisted_count = len([p for p in self.pool.proxies.values() if p.is_blacklisted])

        # Use the auto-generated ProxyStatistics model
        return ProxyStatistics(
            success=True,
            message="Proxy statistics retrieved successfully",
            data=None,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=generate_correlation_id(),
            total_proxies=len(self.pool.proxies),
            active_proxies=len(available_proxies),
            inactive_proxies=len(self.pool.proxies) - len(available_proxies),
            blocked_proxies=blacklisted_count,
            expired_proxies=0,  # TODO: Calculate from expiry dates
            error_proxies=0,  # TODO: Calculate from error states
            healthy_proxies=len([p for p in available_proxies if p.usage_stats.is_healthy]),
            degraded_proxies=len([p for p in available_proxies if not p.usage_stats.is_healthy]),
            critical_proxies=blacklisted_count,
            provider_breakdown={},  # TODO: Calculate provider stats
            country_breakdown={},  # TODO: Calculate country stats
            overall_success_rate=(
                self._successful_requests / self._total_requests * 100
                if self._total_requests > 0
                else 0.0
            ),
            avg_response_time_ms=0.0,  # TODO: Calculate average from all proxies
            total_requests_last_24h=self._total_requests,  # Simplified for now
            successful_requests_last_24h=self._successful_requests,
            expiring_in_24h=0,  # TODO: Calculate from expiry dates
            expiring_in_7d=0,
            expiring_in_30d=0,
            most_used_providers=[],  # TODO: Calculate top providers
            most_active_countries=[],  # TODO: Calculate top countries
            proxies_added_last_24h=0,  # TODO: Track new additions
            proxies_blocked_last_24h=blacklisted_count,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    async def rotate_proxies(self, provider: Optional[str] = None) -> int:
        """
        Force rotation of proxies from provider.

        Args:
            provider: Optional provider to rotate, None for all providers

        Returns:
            Number of proxies rotated
        """
        rotated = 0

        for proxy_id in list(self.pool.proxies.keys()):
            proxy = self.pool.proxies[proxy_id]
            if provider is None or proxy.provider == provider:
                self.pool.remove_proxy(proxy_id)
                rotated += 1

        # Reload proxies from providers
        await self._load_initial_proxies()

        self.logger.info(f"Rotated {rotated} proxies")
        return rotated
