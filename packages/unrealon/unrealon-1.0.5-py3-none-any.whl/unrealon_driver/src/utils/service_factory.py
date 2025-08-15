"""
Modern Service Factory - UnrealOn Driver v3.0

Revolutionary service factory with Pydantic v2 integration and AutoConfig support.
Provides type-safe, zero-configuration service creation with enterprise defaults.

COMPLIANCE: 100% Pydantic v2 compliant, no Dict[str, Any] usage.
"""

from typing import Optional, TypeVar, Type
from pathlib import Path

from unrealon_driver.src.config.auto_config import AutoConfig
from unrealon_driver.src.core.parser import Parser
from unrealon_driver.src.services.browser_service import BrowserService
from unrealon_driver.src.services.llm import LLMService
from unrealon_driver.src.services.websocket_service import WebSocketService
from unrealon_driver.src.logging import DriverLogger, ensure_driver_logger
from unrealon_driver.src.services.metrics_service import MetricsService
from unrealon_driver.src.services.scheduler_service import SchedulerService
from unrealon_driver.src.dto.services import (
    DriverBrowserConfig,
    LLMConfig,
    WebSocketConfig,
    LoggerConfig,
    MetricsConfig,
    SchedulerConfig,
)

# Type variable for generic service creation
ServiceType = TypeVar("ServiceType")


class ServiceFactory:
    """
    🎯 Modern Service Factory - UnrealOn Driver v3.0

    Revolutionary Simplicity meets Enterprise Power:
    - 🔧 Zero-configuration defaults via AutoConfig
    - 🎯 100% Pydantic v2 type safety
    - ⚡ Fluent API for service creation
    - 🚀 Enterprise-grade configurations
    - 🔄 Environment-aware settings

    Examples:
        # Quick development setup
        factory = ServiceFactory.for_development("my_parser")
        parser = factory.create_parser()
        browser = factory.create_browser_service()

        # Production setup with custom config
        factory = ServiceFactory.for_production("prod_parser")
        parser = factory.create_parser()
        llm = factory.create_llm_service()

        # Custom configuration
        factory = ServiceFactory(config=my_config)
        all_services = factory.create_all_services()
    """

    def __init__(self, config: Optional[AutoConfig] = None):
        """
        Initialize service factory with optional configuration.

        Args:
            config: AutoConfig instance. If None, creates default development config.
        """
        self.config = config or AutoConfig.create_development("factory_default")

    # ===========================================
    # FLUENT FACTORY CREATION METHODS
    # ===========================================

    @classmethod
    def for_development(cls, parser_id: str) -> "ServiceFactory":
        """Create factory for development environment with debug features."""
        config = AutoConfig.create_development(parser_id)
        return cls(config)

    @classmethod
    def for_production(cls, parser_id: str) -> "ServiceFactory":
        """Create factory for production environment with optimal settings."""
        config = AutoConfig.create_production(parser_id)
        return cls(config)

    @classmethod
    def for_testing(cls, parser_id: str) -> "ServiceFactory":
        """Create factory for testing environment with minimal settings."""
        config = AutoConfig.create_minimal(parser_id)
        return cls(config)

    @classmethod
    def with_custom_config(cls, config: AutoConfig) -> "ServiceFactory":
        """Create factory with custom AutoConfig."""
        return cls(config)
    
    @classmethod
    def from_config(cls, config: AutoConfig) -> "ServiceFactory":
        """Create factory from AutoConfig (alias for with_custom_config)."""
        return cls(config)

    # ===========================================
    # CORE SERVICE CREATION METHODS
    # ===========================================

    def create_parser(self, **overrides) -> Parser:
        """
        Create fully configured Parser instance.

        Args:
            **overrides: Override specific parser configuration options.

        Returns:
            Parser with all services auto-configured based on environment.
        """
        parser_id = overrides.get("parser_id", self.config.parser_id)
        parser_name = overrides.get("parser_name", self.config.parser_id.replace("_", " ").title())
        
        config = self.config.model_dump()
        if overrides:
            config.update(overrides)
            
        return Parser(
            parser_id=parser_id,
            parser_name=parser_name,
            config=config,
        )

    def create_browser_service(self, **overrides) -> BrowserService:
        """
        Create BrowserService with intelligent defaults.

        Args:
            **overrides: Override specific browser configuration options.

        Returns:
            Configured BrowserService instance.
        """
        browser_config = self.config.browser_config
        if overrides:
            browser_config = browser_config.model_copy(update=overrides)

        return BrowserService(
            config=browser_config,
            logger=self._create_service_logger("browser"),
            metrics=self._create_service_metrics("browser"),
        )

    def create_llm_service(self, **overrides) -> LLMService:
        """
        Create LLMService with AI-optimized defaults.

        Args:
            **overrides: Override specific LLM configuration options.

        Returns:
            Configured LLMService instance.
        """
        llm_config = self.config.llm_config
        if overrides:
            llm_config = llm_config.model_copy(update=overrides)

        return LLMService(
            config=llm_config,
            logger=self._create_service_logger("llm"),
        )

    def create_websocket_service(self, **overrides) -> WebSocketService:
        """
        Create WebSocketService for real-time communication.

        Args:
            **overrides: Override specific WebSocket configuration options.

        Returns:
            Configured WebSocketService instance.
        """
        websocket_config = self.config.websocket_config
        if overrides:
            websocket_config = websocket_config.model_copy(update=overrides)

        return WebSocketService(
            parser_id=self.config.parser_id,
            config=websocket_config,
            logger=self._create_service_logger("websocket"),
        )

    def create_driver_logger(self, **overrides) -> DriverLogger:
        """
        Create DriverLogger with enterprise SDK integration.

        Args:
            **overrides: Override specific logger configuration options.

        Returns:
            Configured DriverLogger instance with SDK integration.
        """
        # Extract relevant config from overrides
        log_level = overrides.get("log_level", self.config.logger_config.log_level.value)
        enable_console = overrides.get("enable_console", self.config.logger_config.console_output)
        enable_websocket = overrides.get("enable_websocket", False)  # Default off for performance
        
        return ensure_driver_logger(
            parser_id=self.config.parser_id,
            parser_name=self.config.parser_id.replace("_", " ").title(),
        )

    def create_metrics_service(self, **overrides) -> MetricsService:
        """
        Create MetricsService for performance monitoring.

        Args:
            **overrides: Override specific metrics configuration options.

        Returns:
            Configured MetricsService instance.
        """
        metrics_config = self.config.metrics_config
        if overrides:
            metrics_config = metrics_config.model_copy(update=overrides)

        return MetricsService(
            parser_id=self.config.parser_id,
            config=metrics_config,
        )

    def create_scheduler_service(self, **overrides) -> SchedulerService:
        """
        Create SchedulerService for task automation.

        Args:
            **overrides: Override specific scheduler configuration options.

        Returns:
            Configured SchedulerService instance.
        """
        scheduler_config = self.config.scheduler_config
        if overrides:
            scheduler_config = scheduler_config.model_copy(update=overrides)

        return SchedulerService(
            config=scheduler_config,
            logger=self._create_service_logger("scheduler"),
        )

    # ===========================================
    # CONVENIENCE METHODS
    # ===========================================

    def create_all_services(self) -> dict:
        """
        Create all services with consistent configuration.

        Returns:
            Dictionary with all configured services.
        """
        return {
            "parser": self.create_parser(),
            "browser": self.create_browser_service(),
            "llm": self.create_llm_service(),
            "websocket": self.create_websocket_service(),
            "logger": self.create_driver_logger(),
            "metrics": self.create_metrics_service(),
            "scheduler": self.create_scheduler_service(),
        }

    def create_core_services(self) -> dict:
        """
        Create essential services for basic parsing operations.

        Returns:
            Dictionary with core services (browser, llm, logger).
        """
        return {
            "parser": self.create_parser(),
            "browser": self.create_browser_service(),
            "llm": self.create_llm_service(),
            "logger": self.create_driver_logger(),
        }

    # ===========================================
    # INTERNAL HELPER METHODS
    # ===========================================

    def _create_service_logger(self, service_name: str) -> Optional[DriverLogger]:
        """Create a DriverLogger for a specific service (shared global instance)."""
        # Services now share the global DriverLogger instance for consistency
        return ensure_driver_logger(
            parser_id=self.config.parser_id,
            parser_name=self.config.parser_id.replace("_", " ").title(),
        )

    def _create_service_metrics(self, service_name: str) -> Optional[MetricsService]:
        """Create metrics collector for a specific service."""
        if not self.config.metrics_config:
            return None

        return MetricsService(
            config=self.config.metrics_config,
            parser_id=f"{self.config.parser_id}_{service_name}",
        )

    def update_config(self, **updates) -> "ServiceFactory":
        """
        Create new factory with updated configuration.

        Args:
            **updates: Configuration updates to apply.

        Returns:
            New ServiceFactory instance with updated config.
        """
        new_config = self.config.model_copy(update=updates)
        return ServiceFactory(new_config)

    def __repr__(self) -> str:
        return f"<ServiceFactory(parser_id={self.config.parser_id}, env={self.config.environment})>"
