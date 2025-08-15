"""
HTTP client wrapper for UnrealOn SDK v1.0

Wraps the auto-generated HTTP client with SDK-specific functionality:
- Automatic retry with exponential backoff
- Connection pooling and keep-alive optimization
- Request/response logging with structured data
- Type-safe API integration
- SSL/TLS verification and security
"""

import asyncio
import logging
import aiohttp
from typing import Optional, Dict, Any, Callable, Awaitable
from datetime import datetime, timedelta

from unrealon_sdk.src.core.config import AdapterConfig
from unrealon_sdk.src.core.exceptions import ConnectionError, AuthenticationError, TimeoutError
from unrealon_sdk.src.clients.python_http.models import ServiceStatsResponse
from unrealon_sdk.src.clients.python_http.api_config import configure_global_api
from unrealon_sdk.src.clients.python_http.models import (
    ParserRegistrationRequest,
    ParserRegistrationResponse,
    HealthResponse,
    ErrorResponse,
)
from unrealon_sdk.src.clients.python_http.services.async_ParserManagement_service import (
    register_parser_api_v1_parsers_register_post,
)
from unrealon_sdk.src.clients.python_http.services.async_SystemHealth_service import (
    system_health_check_api_v1_health__get,
)
from unrealon_sdk.src.clients.python_http import api_config
from unrealon_sdk.src.clients.python_http.api_config import APIConfig
from unrealon_sdk.src.utils import generate_correlation_id, sanitize_log_data


class HTTPClientWrapper:
    """
    Wrapper for auto-generated HTTP client.

    Provides SDK-specific functionality while using the generated client
    for actual HTTP communication.

    Features:
    - Automatic retry with exponential backoff
    - Connection pooling with keep-alive optimization
    - Comprehensive request/response logging
    - SSL/TLS verification and security
    - Type-safe API integration using generated services
    - Performance monitoring and metrics
    """

    def __init__(self, config: AdapterConfig, logger: logging.Logger):
        """
        Initialize HTTP client wrapper.

        Args:
            config: Adapter configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

        # HTTP client session
        self._session: Optional[aiohttp.ClientSession] = None

        # Performance tracking
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0

        # Connection health
        self._last_successful_request: Optional[datetime] = None
        self._consecutive_failures = 0

        self.logger.debug("HTTPClientWrapper initialized")

    async def connect(self) -> None:
        """
        Initialize HTTP client session with optimal configuration.

        Raises:
            ConnectionError: If session creation fails
        """
        try:
            # Create connector with connection pooling
            connector = aiohttp.TCPConnector(
                limit=self.config.connection_pool_size,
                limit_per_host=20,
                ttl_dns_cache=300,  # 5 minutes DNS cache
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                ssl=True,  # Enforce SSL verification
            )

            # Create timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=self.config.request_timeout_ms / 1000,
                connect=10,  # 10 seconds connect timeout
                sock_read=30,  # 30 seconds socket read timeout
            )

            # Create session with optimal settings
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": f"UnrealOn-SDK/1.0 Parser/{self.config.parser_id}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.config.api_key}",
                },
                raise_for_status=False,  # We handle status codes manually
            )

            # Configure the generated API client
            self._configure_api_client()

            self.logger.info("HTTP client session initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize HTTP client: {e}")
            raise ConnectionError(f"HTTP client initialization failed: {e}")

    def _configure_api_client(self) -> None:
        """Configure the auto-generated API client using global configuration."""
        # Extract base URL from server URL (convert ws:// to http://)
        base_url = self.config.server_url.replace("wss://", "https://").replace("ws://", "http://")

        # Remove WebSocket path if present
        if base_url.endswith("/ws"):
            base_url = base_url[:-3]

        # Configure global API settings - this will be used by all generated API functions
        configure_global_api(
            api_key=self.config.api_key,
            base_url=base_url,
            verify=True
        )
        
        self.logger.info(f"Global API client configured: {base_url} with API key: {self.config.api_key[:15]}...")

    async def disconnect(self) -> None:
        """Close HTTP client session."""
        if self._session and not self._session.closed:
            try:
                await self._session.close()
                self.logger.info("HTTP client session closed")
            except Exception as e:
                self.logger.error(f"Error closing HTTP session: {e}")

        self._session = None

    async def register_parser(
        self, request: ParserRegistrationRequest
    ) -> ParserRegistrationResponse:
        """
        Register parser with the server using generated API client.

        Args:
            request: Parser registration request

        Returns:
            Parser registration response

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If request fails
        """
        correlation_id = generate_correlation_id()
        start_time = datetime.utcnow()

        try:
            self.logger.info(
                f"Registering parser {request.parser_id}", extra={"correlation_id": correlation_id}
            )

            # Use the generated API service
            response = await self._make_request_with_retry(
                register_parser_api_v1_parsers_register_post, 
                data=request
            )

            # Track successful request
            self._track_request_success(start_time)

            if response.success:
                self._last_successful_request = datetime.utcnow()
                self._consecutive_failures = 0

                self.logger.info(
                    f"Parser {request.parser_id} registered successfully",
                    extra={
                        "correlation_id": correlation_id,
                        "response_time_ms": self._calculate_response_time(start_time),
                    },
                )
            else:
                self.logger.error(
                    f"Parser registration failed: {response.error or response.message}",
                    extra={"correlation_id": correlation_id},
                )

            # Ensure type safety - API should return ParserRegistrationResponse
            assert isinstance(response, ParserRegistrationResponse)
            return response

        except Exception as e:
            self._track_request_error(start_time)

            # Determine error type for proper exception
            if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise AuthenticationError(f"Parser registration authentication failed: {e}")

            self.logger.error(
                f"Parser registration failed: {e}", extra={"correlation_id": correlation_id}
            )
            raise ConnectionError(f"Parser registration failed: {e}")

    async def health_check(self) -> HealthResponse:
        """
        Perform health check using generated API client.

        Returns:
            Health check response

        Raises:
            ConnectionError: If health check fails
        """
        correlation_id = generate_correlation_id()
        start_time = datetime.utcnow()

        try:
            self.logger.debug("Performing health check", extra={"correlation_id": correlation_id})

            # Use the generated API service
            response = await self._make_request_with_retry(system_health_check_api_v1_health__get)

            self._track_request_success(start_time)

            self.logger.debug(
                f"Health check completed: {response.status}",
                extra={
                    "correlation_id": correlation_id,
                    "response_time_ms": self._calculate_response_time(start_time),
                },
            )

            # Ensure type safety - API should return HealthResponse
            assert isinstance(response, HealthResponse)
            return response

        except Exception as e:
            self._track_request_error(start_time)

            self.logger.error(f"Health check failed: {e}", extra={"correlation_id": correlation_id})
            raise ConnectionError(f"Health check failed: {e}")

    async def _make_request_with_retry(
        self, api_function: Callable[..., Awaitable[Any]], **kwargs: Any
    ) -> Any:
        """
        Make API request with automatic retry and exponential backoff.

        Args:
            api_function: Generated API function to call
            **kwargs: Arguments to pass to the API function

        Returns:
            API response

        Raises:
            ConnectionError: If all retries fail
            TimeoutError: If request times out
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    # Calculate backoff delay
                    delay = min(2**attempt, 30)  # Max 30 seconds
                    self.logger.debug(f"Retrying request in {delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)

                # Make the actual API call
                if self._session is None:
                    raise ConnectionError("HTTP session not initialized")

                # Create APIConfig with current configuration
                base_url = self.config.server_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/ws")
                current_api_config = APIConfig(
                    base_path=base_url,
                    access_token=self.config.api_key,
                    verify=True
                )

                # Debug logging
                self.logger.debug(f"Making request with API config: base_path={current_api_config.base_path}, access_token={current_api_config.access_token[:15] if current_api_config.access_token else None}...")
                self.logger.debug(f"Original config API key: {self.config.api_key[:15] if self.config.api_key else None}...")
                self.logger.debug(f"get_access_token() returns: {current_api_config.get_access_token()[:15] if current_api_config.get_access_token() else None}...")

                # Pass api_config_override to ensure proper authentication  
                # Note: Temporary fix for None header values - should be fixed in generator
                response = await api_function(api_config_override=current_api_config, **kwargs)

                # Request successful
                return response

            except asyncio.TimeoutError as e:
                last_exception = TimeoutError(f"Request timed out: {e}")
                self.logger.warning(f"Request timeout on attempt {attempt + 1}")

            except aiohttp.ClientError as e:
                last_exception = ConnectionError(f"HTTP client error: {e}")
                self.logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")

            except Exception as e:
                last_exception = ConnectionError(f"Unexpected error: {e}")
                self.logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
                self.logger.debug(f"Full exception details: {type(e).__name__}: {e}", exc_info=True)

        # All retries failed
        self._consecutive_failures += 1
        if last_exception is not None:
            raise last_exception
        else:
            raise ConnectionError("Request failed with unknown error")

    def _track_request_success(self, start_time: datetime) -> None:
        """Track successful request metrics."""
        self._request_count += 1
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._total_response_time += response_time
        self._last_successful_request = datetime.utcnow()
        self._consecutive_failures = 0

    def _track_request_error(self, start_time: datetime) -> None:
        """Track failed request metrics."""
        self._request_count += 1
        self._error_count += 1
        self._consecutive_failures += 1
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._total_response_time += response_time

    def _calculate_response_time(self, start_time: datetime) -> float:
        """Calculate response time in milliseconds."""
        return (datetime.utcnow() - start_time).total_seconds() * 1000

    def is_healthy(self) -> bool:
        """Check if HTTP client is healthy."""
        if self._session is None or self._session.closed:
            return False

        # Consider unhealthy if too many consecutive failures
        if self._consecutive_failures >= 5:
            return False

        # Consider unhealthy if no successful requests in last 5 minutes
        if (
            self._last_successful_request is None
            or datetime.utcnow() - self._last_successful_request > timedelta(minutes=5)
        ):
            return False

        return True

    async def health_check_detailed(self) -> HealthResponse:
        """
        Perform detailed health check with client metrics.

        Returns:
            Health response with detailed information
        """
        try:
            # Perform actual health check
            health_response = await self.health_check()

            # Add client-specific health information
            client_metrics = {
                "session_active": self._session is not None and not self._session.closed,
                "request_count": self._request_count,
                "error_count": self._error_count,
                "error_rate": self._error_count / max(self._request_count, 1),
                "average_response_time_ms": self._total_response_time / max(self._request_count, 1),
                "consecutive_failures": self._consecutive_failures,
                "last_successful_request": (
                    self._last_successful_request.isoformat()
                    if self._last_successful_request
                    else None
                ),
                "is_healthy": self.is_healthy(),
            }

            # Create enhanced health response (if needed, extend the model)
            # For now, use the original response
            return health_response

        except Exception as e:
            # Return error health response
            return HealthResponse(
                status="error",
                service="http_client",
                version="1.0.0",
                timestamp=datetime.utcnow().isoformat(),
                components={"error": f"Health check failed: {e}"},
            )

    def get_statistics(self) -> ServiceStatsResponse:
        """
        Get HTTP client statistics.

        Returns:
            ServiceStatsResponse with typed client statistics
        """
        return ServiceStatsResponse(
            service_name="http_client",
            initialized=True,
            status="healthy" if self.is_healthy() else "unhealthy",
            operations_performed=self._request_count,
            errors_encountered=self._error_count,
            error_rate=(self._error_count / max(self._request_count, 1)) * 100,
            last_operation=(
                self._last_successful_request.isoformat() if self._last_successful_request else None
            ),
            uptime_seconds=(
                datetime.utcnow() - getattr(self, "_start_time", datetime.utcnow())
            ).total_seconds(),
            additional_metrics={
                "average_response_time_ms": self._total_response_time / max(self._request_count, 1),
                "consecutive_failures": self._consecutive_failures,
            },
        )

    # Context manager support
    async def __aenter__(self) -> "HTTPClientWrapper":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()
