"""
Logging Configuration for UnrealOn LLM

Provides configuration management for the integrated SDK logging system.
Handles environment variables, default settings, and initialization.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from unrealon_sdk.src.dto.logging import SDKSeverity
from unrealon_llm.src.llm_logging import initialize_llm_logger, get_llm_logger, LLMLogger


class LoggingConfig(BaseModel):
    """Configuration for UnrealOn LLM logging system."""
    
    # Basic logging settings
    log_level: str = Field(default="INFO", description="Logging level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    enable_console: bool = Field(default=True, description="Enable console logging output")
    enable_websocket: bool = Field(default=True, description="Enable WebSocket logging for real-time streaming")
    
    # Session management
    session_id: Optional[str] = Field(default=None, description="Custom session ID for tracking")
    
    # Log filtering and performance
    min_cost_threshold_usd: float = Field(default=0.0001, description="Minimum cost to log (filters micro-transactions)")
    log_token_details: bool = Field(default=True, description="Include token count details in logs")
    log_html_size_details: bool = Field(default=True, description="Include HTML size details in logs")
    
    # Development settings
    verbose_errors: bool = Field(default=True, description="Include full error traces in logs")
    log_cache_operations: bool = Field(default=True, description="Log cache hits/misses/stores")
    log_performance_metrics: bool = Field(default=True, description="Log performance metrics and thresholds")
    
    model_config = ConfigDict(
        env_prefix="UNREALON_LLM_LOG_",
        extra="ignore"
    )


def get_logging_config_from_env() -> LoggingConfig:
    """
    Create logging configuration from environment variables.
    
    Environment variables:
    - UNREALON_LLM_LOG_LEVEL: Logging level (default: INFO)
    - UNREALON_LLM_LOG_ENABLE_CONSOLE: Enable console output (default: true)
    - UNREALON_LLM_LOG_ENABLE_WEBSOCKET: Enable WebSocket output (default: true)
    - UNREALON_LLM_LOG_SESSION_ID: Custom session ID
    - UNREALON_LLM_LOG_MIN_COST_THRESHOLD_USD: Minimum cost to log (default: 0.0001)
    - UNREALON_LLM_LOG_TOKEN_DETAILS: Log token details (default: true)
    - UNREALON_LLM_LOG_HTML_SIZE_DETAILS: Log HTML size details (default: true)
    - UNREALON_LLM_LOG_VERBOSE_ERRORS: Include full error traces (default: true)
    - UNREALON_LLM_LOG_CACHE_OPERATIONS: Log cache operations (default: true)
    - UNREALON_LLM_LOG_PERFORMANCE_METRICS: Log performance metrics (default: true)
    """
    
    # Helper function to parse boolean env vars
    def parse_bool(value: str) -> bool:
        return value.lower() in ("true", "1", "yes", "on")
    
    config_data = {}
    
    # Get values from environment
    if log_level := os.getenv("UNREALON_LLM_LOG_LEVEL"):
        config_data["log_level"] = log_level.upper()
    
    if enable_console := os.getenv("UNREALON_LLM_LOG_ENABLE_CONSOLE"):
        config_data["enable_console"] = parse_bool(enable_console)
    
    if enable_websocket := os.getenv("UNREALON_LLM_LOG_ENABLE_WEBSOCKET"):
        config_data["enable_websocket"] = parse_bool(enable_websocket)
    
    if session_id := os.getenv("UNREALON_LLM_LOG_SESSION_ID"):
        config_data["session_id"] = session_id
    
    if min_cost_threshold := os.getenv("UNREALON_LLM_LOG_MIN_COST_THRESHOLD_USD"):
        try:
            config_data["min_cost_threshold_usd"] = float(min_cost_threshold)
        except ValueError:
            pass  # Use default if invalid
    
    if log_token_details := os.getenv("UNREALON_LLM_LOG_TOKEN_DETAILS"):
        config_data["log_token_details"] = parse_bool(log_token_details)
    
    if log_html_size_details := os.getenv("UNREALON_LLM_LOG_HTML_SIZE_DETAILS"):
        config_data["log_html_size_details"] = parse_bool(log_html_size_details)
    
    if verbose_errors := os.getenv("UNREALON_LLM_LOG_VERBOSE_ERRORS"):
        config_data["verbose_errors"] = parse_bool(verbose_errors)
    
    if log_cache_operations := os.getenv("UNREALON_LLM_LOG_CACHE_OPERATIONS"):
        config_data["log_cache_operations"] = parse_bool(log_cache_operations)
    
    if log_performance_metrics := os.getenv("UNREALON_LLM_LOG_PERFORMANCE_METRICS"):
        config_data["log_performance_metrics"] = parse_bool(log_performance_metrics)
    
    return LoggingConfig(**config_data)


def setup_llm_logging(config: Optional[LoggingConfig] = None) -> LLMLogger:
    """
    Set up UnrealOn LLM logging with the given configuration.
    
    Args:
        config: Logging configuration. If None, loads from environment.
        
    Returns:
        Initialized LLM logger instance.
        
    Example:
        >>> from unrealon_llm.src.llm_config import setup_llm_logging
        >>> logger = setup_llm_logging()
        >>> # Now all LLM operations will be logged
    """
    if config is None:
        config = get_logging_config_from_env()
    
    # Check if logger is already initialized
    existing_logger = get_llm_logger()
    if existing_logger:
        return existing_logger
    
    # Initialize with config
    return initialize_llm_logger(
        session_id=config.session_id,
        log_level=config.log_level,
        enable_console=config.enable_console,
        enable_websocket=config.enable_websocket,
    )


def configure_llm_logging(
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_websocket: bool = True,
    session_id: Optional[str] = None,
) -> LLMLogger:
    """
    Quick configuration function for UnrealOn LLM logging.
    
    Args:
        log_level: Logging level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Enable console output
        enable_websocket: Enable WebSocket output  
        session_id: Custom session ID
        
    Returns:
        Initialized LLM logger instance.
        
    Example:
        >>> from unrealon_llm.src.llm_config import configure_llm_logging
        >>> logger = configure_llm_logging(log_level="DEBUG", session_id="my-session")
    """
    config = LoggingConfig(
        log_level=log_level,
        enable_console=enable_console,
        enable_websocket=enable_websocket,
        session_id=session_id,
    )
    
    return setup_llm_logging(config)


# Auto-initialize logging if environment variables are present
def _auto_initialize():
    """Auto-initialize logging if environment variables indicate it should be enabled."""
    if os.getenv("UNREALON_LLM_AUTO_INIT_LOGGING", "false").lower() in ("true", "1", "yes", "on"):
        try:
            setup_llm_logging()
        except Exception:
            # Silently fail auto-initialization to avoid breaking imports
            pass


# Run auto-initialization on module import
_auto_initialize()
