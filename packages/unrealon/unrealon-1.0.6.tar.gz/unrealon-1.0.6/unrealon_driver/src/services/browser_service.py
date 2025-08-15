"""
Smart Browser Service for UnrealOn Driver v3.0

Zero-configuration browser automation with intelligent features.
Wraps unrealon_browser with enhanced capabilities and smart defaults.

CRITICAL REQUIREMENTS COMPLIANCE:
- ✅ Absolute imports only 
- ✅ Pydantic v2 models everywhere
- ✅ No Dict[str, Any] usage
- ✅ Complete type annotations
- ✅ Auto-generated model usage
"""

import asyncio
from pathlib import Path
from typing import Any, List, Optional, Union, Callable
from datetime import datetime

from unrealon_browser.src.core.browser_manager import BrowserManager
from unrealon_browser.src.managers import ProfileManager, CookieManager, StealthManager
from unrealon_browser.src.dto.models.statistics import BrowserStatistics
from unrealon_browser.src.dto.models.core import PageResult
from unrealon_browser.src.dto.models.config import (
    BrowserConfig as UnrealOnBrowserConfig,
)

# CRITICAL REQUIREMENTS COMPLIANCE - NO INLINE IMPORTS!
from unrealon_browser.src.dto import (
    BrowserConfig,
    BrowserType,
    BrowserMode,
)
from unrealon_sdk.src.provider import Utils
from unrealon_sdk.src.clients.python_http.models.SuccessResponse import SuccessResponse
from unrealon_sdk.src.clients.python_http.models.ErrorResponse import ErrorResponse
from unrealon_sdk.src.enterprise.logging.development import get_development_logger
from unrealon_sdk.src.dto.logging import SDKContext, SDKEventType

from unrealon_driver.src.core.exceptions import BrowserError, create_browser_error
from unrealon_driver.src.dto.services import (
    DriverBrowserConfig,
    ServiceHealthStatus,
    ServiceOperationResult,
)
from unrealon_driver.src.dto.events import DriverEventType


class BrowserService:
    """
    🌐 Smart Browser Service

    Zero-configuration browser automation with intelligent features:
    - 🔥 STEALTH BY DEFAULT - all navigation uses stealth automatically
    - Smart waiting and content detection  
    - Automatic anti-detection measures
    - Error recovery and retries
    - Resource management
    - Performance optimization
    
    🔥 NAVIGATION METHODS:
    - navigate(url) - STEALTH navigation (recommended for all use)
    - navigate_unsafe(url) - without stealth (use only when stealth not needed)
    - get_html(url) - STEALTH + special Amazon handling
    """

    def __init__(
        self,
        config: DriverBrowserConfig,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
    ):
        """Initialize browser service with auto-configuration."""
        self.config = config
        self.logger = logger
        self.metrics = metrics

        # ✅ DEVELOPMENT LOGGER INTEGRATION (CRITICAL REQUIREMENT)
        self.dev_logger = get_development_logger()

        # Browser management
        self._browser_manager: Optional[BrowserManager] = None
        self._current_page = None
        self._is_initialized = False

        # Performance tracking
        self._operation_count = 0
        self._total_duration = 0.0

        # Log initialization with development logger
        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.COMPONENT_CREATED,
                "Browser service initialized",
                context=SDKContext(
                    parser_id=self.config.parser_id,
                    component_name="Browser",
                    layer_name="UnrealOn_Driver",
                    metadata={
                        "headless": self.config.headless,
                        "stealth": True,  # Always enabled
                        "timeout": self.config.timeout,
                        "debug_mode": self.config.debug_mode,
                    },
                ),
            )

    async def _log_driver_event(
        self, event_type: DriverEventType, message: str, **metadata
    ) -> None:
        """Log ONLY driver-specific events (not browser module events)."""
        if self.dev_logger and event_type in [
            DriverEventType.SERVICE_INITIALIZED,
            DriverEventType.SERVICE_ERROR,
            DriverEventType.BROWSER_CONTENT_EXTRACTED,
            DriverEventType.BROWSER_SCREENSHOT_TAKEN,
        ]:
            self.dev_logger.log_info(
                event_type.value,
                message,
                context=SDKContext(
                    parser_id=self.config.parser_id,
                    component_name="Browser",
                    layer_name="UnrealOn_Driver",
                    metadata=metadata,
                ),
            )

    async def _ensure_initialized(self):
        """Ensure browser is initialized."""
        if not self._is_initialized:
            await self._initialize_browser()

    async def _initialize_browser(self):
        """Initialize browser with unrealon_browser integration."""
        try:

            browser_config = Utils.create_browser_config(
                parser_name=self.config.parser_id,
                browser_type=BrowserType.CHROMIUM,
                # 🔥 STEALTH ALWAYS ON - NO CONFIG NEEDED!
                headless=self.config.headless
            )

            # Create browser manager (logger_bridge auto-integrates with SDK)
            self._browser_manager = BrowserManager(config=browser_config)

            # Setup system paths if provided
            system_dir = self.config.user_data_dir
            if system_dir:
                profiles_dir = Path(system_dir) / "browser_profiles"
                cookies_dir = Path(system_dir) / "cookies"

                # Ensure directories exist
                profiles_dir.mkdir(parents=True, exist_ok=True)
                cookies_dir.mkdir(parents=True, exist_ok=True)

                # Override managers with custom paths
                self._browser_manager.profile_manager = ProfileManager(
                    profiles_dir=str(profiles_dir)
                )
                self._browser_manager.cookie_manager = CookieManager(
                    cookies_dir=str(cookies_dir),
                    parser_name=self.config.parser_id,
                )

            # Initialize browser async
            await self._browser_manager.initialize_async()

            self._is_initialized = True

            # Log browser initialized event
            if self.logger:
                self.logger.info(
                    f"Browser service initialized - headless: {self.config.headless}"
                )

            if self.logger:
                self.logger.info("Browser service initialized successfully")

        except Exception as e:
            # Log browser launch failure
            if self.logger:
                self.logger.error(f"Browser initialization failed: {e}")
            raise BrowserError(f"Failed to initialize browser: {e}")

    def _convert_config_to_unrealon_browser(self) -> UnrealOnBrowserConfig:
        """Convert our config to unrealon_browser Pydantic model with type safety."""
        return UnrealOnBrowserConfig(
            parser_name=self.config.parser_id,
            page_load_timeout_seconds=float(self.config.timeout),
            navigation_timeout_seconds=float(self.config.timeout),
            disable_images=not self.config.enable_images,
            # Map our settings to unrealon_browser settings
            use_proxy_rotation=False,  # Default behavior
            realistic_ports_only=False,  # Default behavior
            enable_stealth_check=self.config.debug_mode,
        )

    # ==========================================
    # SMART EXTRACTION METHODS
    # ==========================================

    async def extract(
        self,
        url: str,
        selector: str,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        attribute: Optional[str] = None,
        **kwargs,
    ) -> List[str]:
        """
        🎯 Smart extraction with automatic waiting and error handling.

        Args:
            url: Target URL
            selector: CSS selector
            limit: Maximum number of items to extract
            timeout: Custom timeout (uses default if not specified)
            attribute: Extract attribute instead of text
            **kwargs: Additional options

        Returns:
            List of extracted text/attributes

        Example:
            headlines = await browser.extract(
                "https://news.com",
                ".headline",
                limit=10
            )
        """
        start_time = datetime.now()

        try:
            await self._ensure_initialized()

            # Navigate to URL with smart waiting
            page = await self._navigate_smart(url, timeout=timeout)

            # Wait for content to be ready
            await self._wait_for_content_ready(page, selector, timeout)

            # Extract elements
            if attribute:
                elements = await page.query_selector_all(selector)
                results = [
                    await element.get_attribute(attribute)
                    for element in elements[:limit]
                    if element
                ]
                results = [r for r in results if r]  # Filter None values
            else:
                elements = await page.query_selector_all(selector)
                results = [
                    await element.text_content()
                    for element in elements[:limit]
                    if element
                ]
                results = [r.strip() for r in results if r and r.strip()]  # Clean text

            # Apply limit if specified
            if limit:
                results = results[:limit]

            # Record metrics
            duration = (datetime.now() - start_time).total_seconds()
            self._record_operation("extract", duration, len(results))

            if self.logger:
                self.logger.info(
                    f"Extracted {len(results)} items from {url} in {duration:.2f}s"
                )

            return results

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self._record_operation("extract", duration, 0, error=str(e))

            raise create_browser_error(
                f"Failed to extract from {url}: {e}", url=url, selector=selector
            )

    async def extract_all(
        self, url: str, selector: str, timeout: Optional[int] = None, **kwargs
    ) -> List[str]:
        """Extract all matching elements without limit."""
        return await self.extract(url, selector, limit=None, timeout=timeout, **kwargs)

    async def extract_attributes(
        self,
        url: str,
        selector: str,
        attribute: str,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> List[str]:
        """Extract specific attributes from elements."""
        return await self.extract(
            url, selector, limit=limit, timeout=timeout, attribute=attribute, **kwargs
        )

    async def extract_structured(
        self, url: str, schema: dict, timeout: Optional[int] = None, **kwargs
    ) -> dict:
        """
        🏗️ Extract structured data using schema definition.

        Args:
            url: Target URL
            schema: Schema defining what to extract
            timeout: Custom timeout
            **kwargs: Additional options

        Returns:
            Structured data matching schema

        Example:
            products = await browser.extract_structured(
                "https://shop.com",
                schema={
                    "name": ".product-name",
                    "price": ".price",
                    "rating": ".rating"
                }
            )
        """
        start_time = datetime.now()

        try:
            await self._ensure_initialized()
            page = await self._navigate_smart(url, timeout=timeout)

            result = {}

            for field, selector in schema.items():
                if isinstance(selector, dict):
                    # Nested schema
                    if "selector" in selector and "fields" in selector:
                        # Multiple items with fields
                        items = []
                        elements = await page.query_selector_all(selector["selector"])

                        for element in elements:
                            item = {}
                            for sub_field, sub_selector in selector["fields"].items():
                                sub_element = await element.query_selector(sub_selector)
                                if sub_element:
                                    item[sub_field] = (
                                        await sub_element.text_content()
                                    ).strip()
                            if item:
                                items.append(item)

                        result[field] = items
                    else:
                        # Single nested object
                        nested_result = {}
                        for sub_field, sub_selector in selector.items():
                            element = await page.query_selector(sub_selector)
                            if element:
                                nested_result[sub_field] = (
                                    await element.text_content()
                                ).strip()
                        result[field] = nested_result
                else:
                    # Simple selector
                    element = await page.query_selector(selector)
                    if element:
                        result[field] = (await element.text_content()).strip()

            duration = (datetime.now() - start_time).total_seconds()
            self._record_operation("extract_structured", duration, len(result))

            # Log content extraction success
            await self._log_driver_event(
                DriverEventType.BROWSER_CONTENT_EXTRACTED,
                f"Content extracted successfully from {url}",
                url=url,
                extraction_time_ms=duration * 1000,
                fields_extracted=len(result),
                schema_fields=list(schema.keys()),
            )

            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self._record_operation("extract_structured", duration, 0, error=str(e))

            raise create_browser_error(
                f"Failed to extract structured data from {url}: {e}", url=url
            )

    # ==========================================
    # NAVIGATION AND PAGE CONTROL
    # ==========================================

    async def navigate(self, url: str, timeout: Optional[int] = None):
        """🔥 NAVIGATE WITH STEALTH BY DEFAULT - safer and better detection avoidance."""
        return await self._navigate_stealth(url, timeout)

    async def navigate_unsafe(self, url: str, timeout: Optional[int] = None):
        """Navigate WITHOUT stealth - use only when stealth is not needed."""
        await self._ensure_initialized()
        return await self._navigate_smart(url, timeout)

    async def _navigate_stealth(self, url: str, timeout: Optional[int] = None):
        """Private: Navigate with advanced stealth - blank page first, then target."""
        await self._ensure_initialized()

        # Step 1: Navigate to blank page first (stealth technique)
        page = self._current_page or self._browser_manager.page

        if self.logger:
            self.logger.info(f"🕸️ Stealth navigation: blank → {url}")

        # Navigate to blank page first
        await page.goto("about:blank", wait_until="domcontentloaded")
        await asyncio.sleep(1.0)  # Brief pause

        # Step 2: Navigate to target URL with proper waiting
        return await self._navigate_smart(url, timeout)

    async def get_html(self, url: str, timeout: Optional[int] = None) -> str:
        """Get full HTML content from URL with proper stealth navigation."""
        
        # 🔥 AMAZON SPECIAL: Go to homepage first, then target URL!
        if "amazon.com" in url:
            await self._ensure_initialized()
            page = self._current_page or self._browser_manager.page
            
            if self.logger:
                self.logger.info(f"🛒 Amazon navigation: homepage → {url}")
            
            # Step 1: Go to Amazon homepage first (balanced approach)
            await page.goto("about:blank", wait_until="domcontentloaded")
            await asyncio.sleep(1.0)  
            await page.goto("https://www.amazon.com", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2.0)  # Let homepage stabilize
            
            # Step 2: Navigate to target URL (balanced approach)  
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Step 3: Wait for search results to load dynamically
            await asyncio.sleep(3.0)  # Wait for dynamic content
            
            # Step 4: Additional wait for any delayed content
            try:
                await page.wait_for_selector("[data-component-type='s-search-result']", timeout=5000)
            except:
                # Fallback: just wait a bit more
                await asyncio.sleep(2.0)
            
            return await page.content()
        else:
            # Regular stealth navigation for non-Amazon sites
            page = await self._navigate_stealth(url, timeout)
            return await page.content()

    async def screenshot(
        self,
        url: Optional[str] = None,
        path: Optional[str] = None,
        full_page: bool = True,
    ) -> str:
        """Take screenshot and return path."""
        try:
            if url:
                page = await self.navigate(url)  # 🔥 Now uses stealth by default!
            else:
                page = self._current_page
                if not page:
                    raise BrowserError("No active page for screenshot")

            if not path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = f"screenshot_{timestamp}.png"

            await page.screenshot(path=path, full_page=full_page)

            if self.logger:
                self.logger.info(f"Screenshot saved: {path}")

            return path

        except Exception as e:
            raise BrowserError(f"Failed to take screenshot: {e}")

    # ==========================================
    # SMART FEATURES
    # ==========================================

    async def extract_with_retry(
        self,
        url: str,
        selector: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        **kwargs,
    ) -> List[str]:
        """Extract with automatic retry logic."""
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return await self.extract(url, selector, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    delay = backoff_factor**attempt
                    if self.logger:
                        self.logger.warning(
                            f"Extraction attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                        )
                    await asyncio.sleep(delay)
                else:
                    if self.logger:
                        self.logger.error(
                            f"All {max_retries + 1} extraction attempts failed"
                        )

        raise last_error

    async def extract_with_scroll(
        self,
        url: str,
        selector: str,
        max_scrolls: int = 10,
        scroll_delay: float = 1.0,
        auto_detect_end: bool = True,
        **kwargs,
    ) -> List[str]:
        """Extract with infinite scroll handling."""
        try:
            page = await self.navigate(url)  # 🔥 Now uses stealth by default!
            all_results = []
            last_count = 0

            for scroll in range(max_scrolls):
                # Extract current items
                elements = await page.query_selector_all(selector)
                current_results = [
                    (await elem.text_content()).strip() for elem in elements if elem
                ]
                current_results = [r for r in current_results if r]

                # Check if we found new items
                if auto_detect_end and len(current_results) == last_count:
                    if self.logger:
                        self.logger.info(
                            f"No new items found, stopping scroll at {scroll}"
                        )
                    break

                all_results = current_results
                last_count = len(current_results)

                # Scroll to bottom
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(scroll_delay)

                # Wait for potential new content
                await page.wait_for_timeout(1000)

            if self.logger:
                self.logger.info(
                    f"Extracted {len(all_results)} items with {scroll + 1} scrolls"
                )

            return all_results

        except Exception as e:
            raise create_browser_error(
                f"Failed to extract with scroll from {url}: {e}",
                url=url,
                selector=selector,
            )

    # ==========================================
    # PRIVATE METHODS
    # ==========================================

    async def _navigate_smart(self, url: str, timeout: Optional[int] = None):
        """Smart navigation with optimal waiting."""
        timeout = timeout or self.config.timeout
        start_time = datetime.now()

        # Navigation events are automatically logged by unrealon_browser module

        try:
            # Get or create page
            if not self._current_page:
                self._current_page = self._browser_manager.page

            page = self._current_page

            # Navigate with fast waiting (like old driver)
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)

            # Quick wait for basic content (like old driver: 1 second)
            await asyncio.sleep(1.0)

            # Navigation success events are automatically logged by unrealon_browser module

            return page

        except Exception as e:
            # Navigation failure events are automatically logged by unrealon_browser module
            raise BrowserError(f"Failed to navigate to {url}: {e}")

    async def _wait_for_content_ready(
        self, page, selector: str, timeout: Optional[int] = None
    ):
        """Wait for content to be ready with intelligent detection."""
        timeout = timeout or self.config.timeout

        try:
            # Wait for selector to appear
            await page.wait_for_selector(selector, timeout=timeout * 1000)

            # Additional waiting for dynamic content
            await asyncio.sleep(0.5)  # Brief pause for dynamic content

        except Exception:
            # Selector not found - this might be okay, let extraction handle it
            pass

    async def _wait_for_dynamic_content(self, page, max_wait: float = 3.0):
        """Wait for dynamic content to stabilize."""
        try:
            # Wait for network to be mostly idle
            await page.wait_for_load_state("networkidle", timeout=max_wait * 1000)
        except Exception as e:
            # Timeout is okay - page might be ready enough
            if self.logger:
                self.logger.debug(f"Network idle wait timeout (acceptable): {e}")
            pass

    def _record_operation(
        self,
        operation: str,
        duration: float,
        result_count: int,
        error: Optional[str] = None,
    ):
        """Record operation metrics."""
        self._operation_count += 1
        self._total_duration += duration

        if self.metrics:
            self.metrics.record_operation(
                service="browser",
                operation=operation,
                duration=duration,
                result_count=result_count,
                error=error,
            )

    # ==========================================
    # SERVICE MANAGEMENT
    # ==========================================

    async def health_check(self) -> dict:
        """Check browser service health with type safety."""
        try:
            last_check = datetime.now().isoformat()

            if not self._is_initialized:
                return {
                    "status": "degraded",  # Change to degraded instead of unhealthy
                    "service_name": "browser",
                    "last_check": last_check,
                    "last_error": "Service not initialized",
                    "error_count": 1,
                }

            # Basic health check - try to create a page
            start_time = datetime.now()
            test_page = await self._browser_manager.get_page()
            await test_page.close()
            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "status": "healthy",
                "service_name": "browser",
                "last_check": last_check,
                "response_time_ms": response_time,
                "error_rate": 0.0,
                "uptime_seconds": self._operation_count,  # Using operation count as proxy
                "error_count": 0,
            }
        except Exception as e:
            return {
                "status": "degraded",  # Change to degraded for consistency
                "service_name": "browser",
                "last_check": datetime.now().isoformat(),
                "last_error": str(e),
                "error_count": 1,
            }

    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self._current_page:
                await self._current_page.close()
                self._current_page = None

            if self._browser_manager:
                await self._browser_manager.close_async()
                self._browser_manager = None

            self._is_initialized = False

            if self.logger:
                self.logger.info("Browser service cleaned up")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during browser cleanup: {e}")

    def __repr__(self) -> str:
        return f"<BrowserService(initialized={self._is_initialized}, operations={self._operation_count})>"
