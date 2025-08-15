"""
🚀 Revolutionary Parser Class - UnrealOn Driver v3.0

Zero-configuration web automation with AI-first design and multiple execution modes.
Built from scratch for modern web automation without legacy complexity.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

# Core exceptions
from .exceptions import ParserError, ConfigurationError

# Service integrations
from unrealon_driver.src.services.browser_service import BrowserService
from unrealon_driver.src.services.llm import LLMService
from unrealon_driver.src.services.llm.browser_llm_service import BrowserLLMService
from unrealon_driver.src.services.websocket_service import WebSocketService
from unrealon_driver.src.logging import DriverLogger, ensure_driver_logger
from unrealon_driver.src.services.metrics_service import MetricsService

# Configuration system
from unrealon_driver.src.config.auto_config import AutoConfig

# Execution modes
from unrealon_driver.src.execution.test_mode import TestMode
from unrealon_driver.src.execution.daemon_mode import DaemonMode
from unrealon_driver.src.execution.scheduled_mode import ScheduledMode
from unrealon_driver.src.execution.interactive_mode import InteractiveMode

# Type-safe execution configuration
from unrealon_driver.src.dto.execution import (
    ParserTestConfig,
    DaemonModeConfig,
    ScheduledModeConfig,
    InteractiveModeConfig,
)


class Parser:
    """
    🚀 Revolutionary Parser Class

    Zero-configuration web automation with AI-first design.

    Features:
    - 🎯 Zero Configuration: Everything works out of the box
    - 🤖 AI-First Design: LLM integration as core feature
    - 🔌 Multiple Execution Modes: test, daemon, scheduled, interactive
    - 🌐 Smart Browser: Intelligent automation with stealth
    - ⏰ Human-Readable Scheduling: "30m", "1h", "daily"
    - 📊 Built-in Monitoring: Enterprise observability

    Quick Start:
        class MyParser(Parser):
            async def parse(self):
                # Simple browser extraction
                return await self.browser.extract("https://example.com", ".item")
                
                # AI-powered extraction (browser + LLM combined)
                return await self.browser_llm.extract("https://example.com", schema={
                    "products": [{"name": "string", "price": "number"}]
                })

        # Development testing
        result = await MyParser().test()

        # Production daemon (WebSocket service)
        await MyParser().daemon()

        # Automated scheduling
        await MyParser().schedule(every="30m")
    """

    def __init__(
        self,
        parser_id: Optional[str] = None,
        parser_name: Optional[str] = None,
        config: Optional[AutoConfig] = None,
        **kwargs,
    ):
        """
        Initialize parser with zero configuration.

        Args:
            parser_id: Unique identifier (auto-generated if not provided)
            parser_name: Human-readable name (auto-generated if not provided)
            config: Optional configuration override
            **kwargs: Additional configuration options
        """
        # Auto-generate identifiers
        self.parser_id = parser_id or self._generate_parser_id()
        self.parser_name = parser_name or self._generate_parser_name()

        # Initialize auto-configuration
        self._config: AutoConfig = AutoConfig.create_development(
            self.parser_id, config=config
        )

        # Service initialization (lazy-loaded)
        self._browser: BrowserService = None
        self._llm: LLMService = None
        self._browser_llm: BrowserLLMService = None
        self._websocket: WebSocketService = None
        self._logger: DriverLogger = None
        self._metrics: MetricsService = None

        # Execution mode handlers
        self._test_mode: TestMode = None
        self._daemon_mode: DaemonMode = None
        self._scheduled_mode: ScheduledMode = None
        self._interactive_mode: InteractiveMode = None

        # Runtime state
        self._is_initialized = False
        self._shutdown_event = asyncio.Event()

    # ==========================================
    # ZERO-CONFIG SERVICE PROPERTIES
    # ==========================================

    @property
    def browser(self) -> BrowserService:
        """Smart browser service with zero configuration."""
        if self._browser is None:
            self._browser = BrowserService(
                config=self._config.browser_config,
                logger=self.logger,
                metrics=self.metrics,
            )
        return self._browser

    @property
    def llm(self) -> LLMService:
        """AI-powered extraction service."""
        if self._llm is None:
            self._llm = LLMService(
                config=self._config.llm_config,
                logger=self.logger,
            )
        return self._llm

    @property
    def browser_llm(self) -> BrowserLLMService:
        """🔥 AI-powered browser service - auto-configured and ready to use."""
        if self._browser_llm is None:
            self._browser_llm = BrowserLLMService(
                auto_config=self._config,
                logger=self.logger,
                metrics=self.metrics,
            )
        return self._browser_llm

    @property
    def websocket(self) -> WebSocketService:
        """WebSocket service for daemon mode."""
        if self._websocket is None:
            self._websocket = WebSocketService(
                config=self._config.websocket_config,
                logger=self.logger,
                metrics=self.metrics,
                parser_id=self.parser_id,
            )
        return self._websocket

    @property
    def logger(self) -> DriverLogger:
        """Enterprise logging service with SDK integration."""
        if self._logger is None:
            self._logger = ensure_driver_logger(
                parser_id=self.parser_id,
                parser_name=self.parser_name,
                system_dir=str(self._config.system_dir) if self._config.system_dir else None,
            )
        return self._logger

    @property
    def metrics(self) -> MetricsService:
        """Built-in metrics and monitoring."""
        if self._metrics is None:
            self._metrics = MetricsService(
                config=self._config.metrics_config, parser_id=self.parser_id
            )
        return self._metrics

    # ==========================================
    # CORE PARSING METHOD
    # ==========================================

    async def parse(self) -> dict:
        """
        🎯 Main parsing method - OVERRIDE THIS

        This is where you implement your parsing logic.

        Returns:
            Dictionary containing parsed data

        Example:
            async def parse(self):
                # Simple extraction
                headlines = await self.browser.extract(
                    "https://news.com",
                    ".headline"
                )

                # AI-powered extraction
                products = await self.llm.extract(html, schema={
                    "products": [{"name": "string", "price": "number"}]
                })

                return {"headlines": headlines, "products": products}
        """
        raise NotImplementedError(
            f"Parser '{self.parser_name}' must implement the parse() method. "
            f"This is where you define your parsing logic."
        )

    # ==========================================
    # EXECUTION MODES
    # ==========================================

    async def test(self, **kwargs) -> dict:
        """
        🧪 Test Mode - Development and debugging

        Single execution for development and testing.

        Features:
        - Detailed logging and debugging
        - Error reporting with suggestions
        - Performance metrics
        - Results visualization

        Args:
            **kwargs: Test configuration options

        Returns:
            Parsed data with metadata

        Example:
            result = await parser.test()
            print(result)
        """
        if self._test_mode is None:
            # Create type-safe test configuration
            test_config = ParserTestConfig(
                verbose=kwargs.get("verbose", False),
                show_browser=kwargs.get("show_browser", False),
                save_screenshots=kwargs.get("save_screenshots", False),
                timeout_seconds=kwargs.get("timeout", 60),
            )

            self._test_mode = TestMode(parser=self, config=test_config)

        return await self._test_mode.execute(**kwargs)

    async def daemon(
        self, server: Optional[str] = None, api_key: Optional[str] = None, **kwargs
    ) -> None:
        """
        🔌 Daemon Mode - Production WebSocket service

        Connects to UnrealOn server as persistent WebSocket service.

        Features:
        - Auto-connection with reconnection
        - Command handling and response
        - Health monitoring and reporting
        - Graceful shutdown handling
        - Load balancing support

        Args:
            server: WebSocket server URL (auto-detected if not provided)
            api_key: Authentication key (auto-detected if not provided)
            **kwargs: Daemon configuration options

        Example:
            # Auto-configured daemon
            await parser.daemon()

            # Custom server
            await parser.daemon(
                server="wss://my-server.com",
                api_key="my_key"
            )
        """
        if self._daemon_mode is None:
            self._daemon_mode = DaemonMode(
                parser=self, config=self._config.daemon_config
            )

        await self._daemon_mode.start(server=server, api_key=api_key, **kwargs)

    async def schedule(self, every: str, at: Optional[str] = None, **kwargs) -> None:
        """
        ⏰ Scheduled Mode - Automated recurring execution

        Human-readable scheduling with enterprise monitoring.

        Features:
        - Natural language intervals ("30m", "1h", "daily")
        - Smart load balancing with jitter
        - Error recovery and retries
        - Health monitoring and alerting
        - Production-ready reliability

        Args:
            every: Human-readable interval ("30m", "1h", "daily", etc.)
            at: Specific time for daily/weekly schedules ("09:00")
            **kwargs: Scheduling configuration options

        Examples:
            # Every 30 minutes
            await parser.schedule(every="30m")

            # Daily at 9 AM
            await parser.schedule(every="daily", at="09:00")

            # Every hour with monitoring
            await parser.schedule(
                every="1h",
                monitoring=True,
                error_handling=True
            )
        """
        if self._scheduled_mode is None:
            self._scheduled_mode = ScheduledMode(
                parser=self, config=self._config.scheduled_config
            )

        await self._scheduled_mode.start(every=every, at=at, **kwargs)

    async def interactive(self, **kwargs) -> None:
        """
        🎮 Interactive Mode - Live development and debugging

        Interactive shell for live development and testing.

        Features:
        - Live parser execution
        - Real-time result inspection
        - Dynamic configuration changes
        - Browser debugging tools
        - Performance profiling

        Args:
            **kwargs: Interactive mode options

        Example:
            await parser.interactive()
        """
        if self._interactive_mode is None:
            self._interactive_mode = InteractiveMode(
                parser=self, config=self._config.interactive_config
            )

        await self._interactive_mode.start(**kwargs)

    # ==========================================
    # UTILITY METHODS
    # ==========================================

    def now(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()

    def get_system_info(self) -> dict:
        """Get system information for debugging."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        return {
            "parser_id": self.parser_id,
            "parser_name": self.parser_name,
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
            "memory_usage_mb": round(memory_mb, 2),
            "environment": dict(os.environ),
            "config": self._config.model_dump(),
        }

    async def health_check(self) -> dict:
        """Comprehensive health check."""
        health = {
            "status": "healthy",
            "timestamp": self.now(),
            "parser_id": self.parser_id,
            "services": {},
        }

        # Check each service individually
        service_errors = []

        # Check browser service
        if self._browser:
            try:
                health["services"]["browser"] = await self._browser.health_check()
            except Exception as e:
                health["services"]["browser"] = {"status": "error", "error": str(e)}
                service_errors.append(f"browser: {e}")

        # Check LLM service
        if self._llm:
            try:
                health["services"]["llm"] = await self._llm.health_check()
            except Exception as e:
                health["services"]["llm"] = {"status": "error", "error": str(e)}
                service_errors.append(f"llm: {e}")

        # Check Browser LLM service
        if self._browser_llm:
            try:
                health["services"]["browser_llm"] = await self._browser_llm.health_check()
            except Exception as e:
                health["services"]["browser_llm"] = {"status": "error", "error": str(e)}
                service_errors.append(f"browser_llm: {e}")

        # Check WebSocket service
        if self._websocket:
            try:
                health["services"]["websocket"] = await self._websocket.health_check()
            except Exception as e:
                health["services"]["websocket"] = {"status": "error", "error": str(e)}
                service_errors.append(f"websocket: {e}")

        # Check logger service
        if self._logger:
            try:
                health["services"]["logger"] = self._logger.health_check()
            except Exception as e:
                health["services"]["logger"] = {"status": "error", "error": str(e)}
                service_errors.append(f"logger: {e}")

        # Check metrics service
        if self._metrics:
            try:
                health["services"]["metrics"] = self._metrics.health_check()
            except Exception as e:
                health["services"]["metrics"] = {"status": "error", "error": str(e)}
                service_errors.append(f"metrics: {e}")

        # Determine overall status
        if service_errors:
            health["status"] = "degraded"  # Instead of "unhealthy"
            health["service_errors"] = service_errors

        # Add system info as expected by tests
        health["system_info"] = {
            "parser_version": "3.0",
            "environment": getattr(self._config, "environment", "development"),
            "active_services": len(health["services"]),
        }

        return health

    async def cleanup(self):
        """Clean up resources gracefully."""
        self.logger.info("Starting parser cleanup...")

        # Cleanup services (gracefully handle errors)
        cleanup_errors = []

        if self._browser:
            try:
                await self._browser.cleanup()
            except Exception as e:
                cleanup_errors.append(f"browser: {e}")

        if self._llm:
            try:
                await self._llm.cleanup()
            except Exception as e:
                cleanup_errors.append(f"llm: {e}")

        if self._browser_llm:
            try:
                await self._browser_llm.cleanup()
            except Exception as e:
                cleanup_errors.append(f"browser_llm: {e}")

        if self._websocket:
            try:
                await self._websocket.cleanup()
            except Exception as e:
                cleanup_errors.append(f"websocket: {e}")

        if self._logger:
            try:
                await self._logger.cleanup()
            except Exception as e:
                cleanup_errors.append(f"logger: {e}")

        if self._metrics:
            try:
                await self._metrics.cleanup()
            except Exception as e:
                cleanup_errors.append(f"metrics: {e}")

        # Log cleanup errors but don't raise
        if cleanup_errors:
            self.logger.warning(f"Cleanup errors: {'; '.join(cleanup_errors)}")

        self.logger.info("Parser cleanup completed")

    # ==========================================
    # PRIVATE METHODS
    # ==========================================

    def _generate_parser_id(self) -> str:
        """Generate unique parser ID."""
        class_name = self.__class__.__name__.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{class_name}_{timestamp}"

    def _generate_parser_name(self) -> str:
        """Generate human-readable parser name."""
        class_name = self.__class__.__name__
        if class_name.endswith("Parser"):
            class_name = class_name[:-6]  # Remove "Parser" suffix

        # Convert CamelCase to Title Case
        import re

        name = re.sub(r"([A-Z])", r" \1", class_name).strip()
        return name if name else f"UnrealOn Parser {self.parser_id[-8:]}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.parser_id}', name='{self.parser_name}')>"

    def __str__(self) -> str:
        return f"{self.parser_name} ({self.parser_id})"

    # ==========================================
    # CONTEXT MANAGER SUPPORT
    # ==========================================

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        # Return None/False to let exceptions propagate
        return False

    async def _initialize(self):
        """Initialize parser for context manager usage."""
        if not self._is_initialized:
            self.logger.info(f"Initializing parser: {self.parser_name}")
            self._is_initialized = True

    def _generate_parser_id(self) -> str:
        """Generate unique parser ID."""
        import time
        import uuid

        timestamp = int(time.time() * 1000000)  # Microseconds for uniqueness
        short_uuid = str(uuid.uuid4())[:8]
        return f"parser_{timestamp}_{short_uuid}"

    def _generate_parser_name(self) -> str:
        """Generate parser name."""
        return f"UnrealOn Parser {self.parser_id[-8:]}"


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================


async def quick_extract(url: str, selector: str, **kwargs) -> List[str]:
    """
    🚀 Quick extraction without creating parser class

    Convenience function for simple one-off extractions.

    Args:
        url: Target URL
        selector: CSS selector
        **kwargs: Additional options

    Returns:
        List of extracted text

    Example:
        headlines = await quick_extract(
            "https://news.com",
            ".headline"
        )
    """

    class QuickParser(Parser):
        async def parse(self):
            return await self.browser.extract(url, selector, **kwargs)

    result = await QuickParser().test()
    return result.get("data", [])


async def quick_extract_with_ai(url: str, schema: dict, **kwargs) -> dict:
    """
    🤖 Quick AI extraction without creating parser class

    Convenience function for AI-powered extractions.

    Args:
        url: Target URL
        schema: Data schema for AI extraction
        **kwargs: Additional options

    Returns:
        Structured data extracted by AI

    Example:
        products = await quick_extract_with_ai(
            "https://shop.com",
            schema={"products": [{"name": "string", "price": "number"}]}
        )
    """

    class QuickAIParser(Parser):
        async def parse(self):
            html = await self.browser.get_html(url)
            return await self.llm.extract(html, schema, **kwargs)

    result = await QuickAIParser().test()
    return result.get("data", {})
