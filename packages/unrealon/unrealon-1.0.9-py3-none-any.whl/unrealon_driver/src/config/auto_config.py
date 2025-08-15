"""
Auto-configuration system for UnrealOn Driver v3.0

Intelligent configuration with zero setup required.
Automatically detects environment and applies optimal settings.
COMPLIANCE: 100% Pydantic v2 compliant, no Dict[str, Any] usage.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, ConfigDict, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from unrealon_driver.src.core.exceptions import ConfigurationError
from unrealon_driver.src.dto.services import (
    DriverBrowserConfig,
    LLMConfig,
    WebSocketConfig,
    LoggerConfig,
    MetricsConfig,
    SchedulerConfig,
)
from unrealon_driver.src.dto.execution import (
    ParserTestConfig,
    DaemonModeConfig,
    ScheduledModeConfig,
    InteractiveModeConfig,
)
from unrealon_driver.src.dto.config import LogLevel


class AutoConfigBase(BaseModel):
    """Base configuration without environment variables."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Base configuration
    parser_id: str = Field(default="auto_parser", description="Parser identifier")

    # Environment detection
    environment: str = Field(default_factory=lambda: AutoConfig._detect_environment())
    debug_mode: bool = Field(default_factory=lambda: AutoConfig._is_debug_mode())

    # Service configurations (type-safe)
    browser_config: Optional[DriverBrowserConfig] = Field(
        default=None, description="Browser service config"
    )
    llm_config: Optional[LLMConfig] = Field(
        default=None, description="LLM service config"
    )
    websocket_config: Optional[WebSocketConfig] = Field(
        default=None, description="WebSocket service config"
    )
    logger_config: Optional[LoggerConfig] = Field(
        default=None, description="Logger service config"
    )
    metrics_config: Optional[MetricsConfig] = Field(
        default=None, description="Metrics service config"
    )
    scheduler_config: Optional[SchedulerConfig] = Field(
        default=None, description="Scheduler service config"
    )

    # Execution mode configurations (type-safe)
    test_config: Optional[ParserTestConfig] = Field(
        default=None, description="Test mode config"
    )
    daemon_config: Optional[DaemonModeConfig] = Field(
        default=None, description="Daemon mode config"
    )
    scheduled_config: Optional[ScheduledModeConfig] = Field(
        default=None, description="Scheduled mode config"
    )
    interactive_config: Optional[InteractiveModeConfig] = Field(
        default=None, description="Interactive mode config"
    )

    # System paths
    project_root: Optional[Path] = Field(default=None, description="Project root path")
    system_dir: Optional[Path] = Field(
        default=None, description="System directory path"
    )
    logs_dir: Optional[Path] = Field(default=None, description="Logs directory path")
    data_dir: Optional[Path] = Field(default=None, description="Data directory path")

    def model_post_init(self, __context) -> None:
        """Initialize all configurations after model creation."""
        self._initialize_configs()

    def _initialize_configs(self) -> None:
        """Initialize all configurations. Can be called manually."""
        # Force reset all configs to None to ensure they're recreated
        self.browser_config = None
        self.llm_config = None
        self.websocket_config = None
        self.logger_config = None
        self.metrics_config = None
        self.scheduler_config = None
        self.test_config = None
        self.daemon_config = None
        self.scheduled_config = None
        self.interactive_config = None

        self._setup_directories()
        self._setup_service_configs()
        self._setup_execution_configs()

    def _setup_directories(self):
        """Setup system directories."""
        if not self.project_root:
            self.project_root = self._detect_project_root()

        if not self.system_dir:
            self.system_dir = self._get_system_dir()

        if not self.logs_dir:
            self.logs_dir = self._get_logs_dir()

        if not self.data_dir:
            self.data_dir = self._get_data_dir()

        # Ensure directories exist
        for dir_path in [self.system_dir, self.logs_dir, self.data_dir]:
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)

    def _setup_service_configs(self):
        """Setup all service configurations."""
        if not self.browser_config:
            self.browser_config = self._create_browser_config()

        if not self.llm_config:
            self.llm_config = self._create_llm_config()

        if not self.websocket_config:
            self.websocket_config = self._create_websocket_config()

        if not self.logger_config:
            self.logger_config = self._create_logger_config()

        if not self.metrics_config:
            self.metrics_config = self._create_metrics_config()

        if not self.scheduler_config:
            self.scheduler_config = self._create_scheduler_config()

    def _create_browser_config(self) -> DriverBrowserConfig:
        """Create browser configuration with STEALTH ALWAYS ENABLED."""
        return DriverBrowserConfig(
            headless=self.environment == "production",  # Headless in production
            timeout=60 if self.environment == "production" else 30,
            user_data_dir=(
                str(self.system_dir / "browser_data") if self.system_dir else None
            ),
            parser_id=self.parser_id,
            # 🔥 STEALTH ALWAYS ON - NO CONFIG NEEDED!
            page_load_strategy="normal",
            wait_for_selector_timeout=10,
            network_idle_timeout=3,
            enable_javascript=True,
            enable_images=True,
            enable_css=True,
            debug_mode=self.debug_mode,
            save_screenshots=self.debug_mode,  # Save screenshots in debug mode
            log_level=LogLevel.DEBUG if self.debug_mode else LogLevel.INFO,
        )

    def _setup_execution_configs(self):
        """Setup all execution mode configurations."""
        if not self.test_config:
            self.test_config = self._create_test_config()

        if not self.daemon_config:
            self.daemon_config = self._create_daemon_config()

        if not self.scheduled_config:
            self.scheduled_config = self._create_scheduled_config()

        if not self.interactive_config:
            self.interactive_config = self._create_interactive_config()

    def _create_llm_config(self) -> LLMConfig:
        """Create LLM configuration."""
        return LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=2048 if self.environment == "development" else 4096,
            temperature=0.1,
            timeout=30 if self.environment == "development" else 60,
            max_retries=2 if self.environment == "development" else 3,
            enable_caching=True,
            enable_cost_tracking=True,
            log_level=LogLevel.DEBUG if self.debug_mode else LogLevel.INFO,
        )

    def _create_websocket_config(self) -> WebSocketConfig:
        """Create WebSocket configuration."""
        return WebSocketConfig(
            server_url=os.getenv("SERVER_URL"),
            api_key=os.getenv("API_KEY"),
            parser_name=self.parser_id,
            auto_reconnect=True,
            max_reconnect_attempts=10 if self.environment == "production" else 5,
            reconnect_delay=1.0,
            health_check_interval=30,
            heartbeat_interval=30,
            connection_timeout=10,
        )

    def _create_logger_config(self) -> LoggerConfig:
        """Create logger configuration."""
        return LoggerConfig(
            log_level=LogLevel.DEBUG if self.debug_mode else LogLevel.INFO,
            console_output=True,
            file_output=True,
            log_file=f"{self.parser_id}.log",
            log_dir=str(self.logs_dir) if self.logs_dir else None,
        )

    def _create_metrics_config(self) -> MetricsConfig:
        """Create metrics configuration."""
        return MetricsConfig(
            parser_id=self.parser_id,
            enable_metrics=True,
            collect_performance=True,
            collect_errors=True,
            collect_usage=True,
            retention_days=30 if self.environment == "production" else 7,
            export_format="json",
            batch_size=100,
            flush_interval=60,
        )

    def _create_scheduler_config(self) -> SchedulerConfig:
        """Create scheduler configuration."""
        return SchedulerConfig(
            parser_id=self.parser_id,
            max_concurrent_tasks=5 if self.environment == "development" else 10,
            enable_jitter=True,
            jitter_range=0.1,
            default_timeout=300,
            default_retries=3,
            cleanup_interval=3600,
            enable_task_monitoring=True,
            health_check_interval=60,
        )

    def _create_test_config(self) -> ParserTestConfig:
        """Create test mode configuration."""
        return ParserTestConfig(
            verbose=self.debug_mode,
            show_browser=self.debug_mode,
            save_screenshots=self.debug_mode,
            timeout_seconds=60 if self.environment == "development" else 120,
        )

    def _create_daemon_config(self) -> DaemonModeConfig:
        """Create daemon mode configuration."""
        return DaemonModeConfig(
            server_url=os.getenv("SERVER_URL"),
            api_key=os.getenv("API_KEY"),
            auto_reconnect=True,
            connection_timeout=30,
            heartbeat_interval=30,
            max_reconnect_attempts=10,
            health_check_interval=60,
            enable_metrics=True,
        )

    def _create_scheduled_config(self) -> ScheduledModeConfig:
        """Create scheduled mode configuration."""
        return ScheduledModeConfig(
            every="1h",  # Default schedule
            timeout=600,
            retry_attempts=3,
            max_concurrent=1,
            jitter=True,
            jitter_range=0.1,
            error_handling="retry",
        )

    def _create_interactive_config(self) -> InteractiveModeConfig:
        """Create interactive mode configuration."""
        return InteractiveModeConfig(
            enable_debugger=True,
            show_browser=True,
            auto_reload=self.debug_mode,
            log_level=LogLevel.DEBUG,
            enable_profiling=self.debug_mode,
            save_session=True,
        )

    @staticmethod
    def _detect_environment() -> str:
        """Detect runtime environment."""
        if os.getenv("ENV") == "production":
            return "production"
        elif os.getenv("ENV") == "staging":
            return "staging"
        elif os.getenv("ENV") == "testing":
            return "testing"
        else:
            return "development"

    @staticmethod
    def _is_debug_mode() -> bool:
        """Check if debug mode is enabled."""
        return os.getenv("DEBUG", "false").lower() in ["true", "1", "yes"]

    def _detect_project_root(self) -> Path:
        """Detect project root directory."""
        current = Path.cwd()

        # Look for common project markers
        markers = ["pyproject.toml", "setup.py", "requirements.txt", ".git"]

        for parent in [current] + list(current.parents):
            if any((parent / marker).exists() for marker in markers):
                return parent

        return current

    def _get_system_dir(self) -> Path:
        """Get system directory for storing parser data."""
        # 🔥 If system_dir is already set (from Parser), use it
        if self.system_dir:
            return self.system_dir

        # Otherwise generate default path
        if self.project_root:
            return self.project_root / ".unrealon" / self.parser_id
        else:
            return Path.home() / ".unrealon" / self.parser_id

    def _get_logs_dir(self) -> Path:
        """Get logs directory."""
        return self.system_dir / "logs" if self.system_dir else Path.cwd() / "logs"

    def _get_data_dir(self) -> Path:
        """Get data directory."""
        return self.system_dir / "data" if self.system_dir else Path.cwd() / "data"

    # Type-safe configuration updates using Pydantic v2 model_copy
    def update_browser_config(self, **updates) -> None:
        """Update browser configuration with type safety."""
        if self.browser_config:
            self.browser_config = self.browser_config.model_copy(update=updates)
        else:
            raise ConfigurationError("Browser config not initialized")

    def update_llm_config(self, **updates) -> None:
        """Update LLM configuration with type safety."""
        if self.llm_config:
            self.llm_config = self.llm_config.model_copy(update=updates)
        else:
            raise ConfigurationError("LLM config not initialized")

    def update_websocket_config(self, **updates) -> None:
        """Update WebSocket configuration with type safety."""
        if self.websocket_config:
            self.websocket_config = self.websocket_config.model_copy(update=updates)
        else:
            raise ConfigurationError("WebSocket config not initialized")


class AutoConfigWithEnv(BaseSettings, AutoConfigBase):
    """Configuration with .env file support."""

    model_config = SettingsConfigDict(
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_prefix="UNREALON_",
        case_sensitive=False,
    )


# Smart configuration selection
def _should_use_env_config() -> bool:
    """Determine if we should use .env configuration."""
    # Use env config if .env file exists or UNREALON_ vars are set
    env_file_exists = Path(".env").exists()
    has_unrealon_vars = any(key.startswith("UNREALON_") for key in os.environ)
    return env_file_exists or has_unrealon_vars


# Dynamic class selection
if _should_use_env_config():
    AutoConfig = AutoConfigWithEnv
else:
    AutoConfig = AutoConfigBase

# Add type hints
AutoConfig.__doc__ = """
🎯 Zero-Configuration System with Smart .env Support

Automatically configures all services with intelligent defaults.
Environment-aware with seamless development-to-production transitions.
Supports .env files with UNREALON_ prefix when available.
COMPLIANCE: 100% Pydantic v2 compliant, no Dict[str, Any] usage.
"""


# Add class methods to AutoConfigBase so they work for both variants
def _add_class_methods_to_base():
    """Add class methods to AutoConfigBase."""

    @classmethod
    def create_minimal(
        cls, parser_id: str = "minimal_parser", config: AutoConfigBase = None
    ):
        """Create minimal configuration for testing."""
        # If config is provided, use it directly (for extended configs like AmazonAutoConfig)
        if config is not None:
            return config

        # Create instance with default values
        instance = cls()
        instance.parser_id = parser_id
        instance.environment = "testing"
        instance.debug_mode = False
        # Reinitialize configs with new parser_id
        instance._initialize_configs()
        return instance

    @classmethod
    def create_development(
        cls, parser_id: str = "dev_parser", config: AutoConfigBase = None
    ):
        """Create development configuration."""
        # If config is provided, use it directly (for extended configs like AmazonAutoConfig)
        if config is not None:
            return config

        # Create instance with default values
        instance = cls()
        instance.parser_id = parser_id
        instance.environment = "development"
        instance.debug_mode = True
        # Reinitialize configs with new parser_id
        instance._initialize_configs()
        return instance

    @classmethod
    def create_production(
        cls, parser_id: str = "prod_parser", config: AutoConfigBase = None
    ):
        """Create production configuration."""
        # If config is provided, use it directly (for extended configs like AmazonAutoConfig)
        if config is not None:
            return config

        # Create instance with default values
        instance = cls()
        instance.parser_id = parser_id
        instance.environment = "production"
        instance.debug_mode = False
        # Reinitialize configs with new parser_id
        instance._initialize_configs()
        return instance

    # Add methods to AutoConfigBase
    AutoConfigBase.create_minimal = create_minimal
    AutoConfigBase.create_development = create_development
    AutoConfigBase.create_production = create_production


# Execute the method addition
_add_class_methods_to_base()
