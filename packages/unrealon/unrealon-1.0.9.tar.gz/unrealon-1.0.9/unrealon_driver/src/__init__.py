"""
🚀 UnrealOn Driver v3.0 - Revolutionary Web Automation

Zero-configuration web automation framework with AI-first design,
multiple execution modes, and enterprise-ready features.

Key Features:
- 🎯 Zero Configuration - Everything works out of the box
- 🤖 AI-First Design - LLM integration as core feature
- 🔌 Daemon Mode - Production WebSocket services
- ⏰ Smart Scheduling - Human-readable intervals
- 🌐 Modern Browser - Intelligent automation
- 📊 Built-in Monitoring - Enterprise observability

Quick Start:
    from unrealon_driver import Parser
    
    class MyParser(Parser):
        async def parse(self):
            return await self.browser.extract("https://example.com", ".item")
    
    # Multiple execution modes
    await MyParser().test()        # Development
    await MyParser().daemon()      # Production WebSocket service
    await MyParser().schedule(every="30m")  # Automated execution
"""

# Core exports
from .core.parser import Parser
from .core.exceptions import *

# Enhanced CLI support (NEW - like old driver)
from .cli.simple import SimpleParser, create_click_parser_cli

# Execution mode utilities
from .execution.modes import ExecutionMode

# Configuration utilities (for advanced users)
from .config.auto_config import AutoConfig

# Services (for advanced usage)
from .services import BrowserService, LLMService, WebSocketService, LoggerService, MetricsService, BrowserLLMService

# Utils (factory)
from .utils.service_factory import ServiceFactory

# Version information
__version__ = "3.0.0"
__author__ = "UnrealOn Team"
__license__ = "MIT"

# Main exports
__all__ = [
    # Core classes
    "Parser",
    
    # Enhanced CLI (NEW)
    "SimpleParser",
    "create_click_parser_cli",
    
    # Execution modes
    "ExecutionMode",
    
    # Configuration (optional)
    "AutoConfig",
    
    # Services (advanced usage)
    "BrowserService",
    "LLMService", 
    "WebSocketService",
    "LoggerService",
    "MetricsService",
    "BrowserLLMService",
    
    # Utils
    "ServiceFactory",
    
    # Exceptions
    "ParserError",
    "ConfigurationError",
    "BrowserError",
    "LLMError",
    "WebSocketError",
    "SchedulingError",
]

# Package metadata
__description__ = "Revolutionary web automation framework with zero configuration"
__url__ = "https://github.com/unrealon/unrealon-driver"
__keywords__ = ["web-automation", "parsing", "ai", "websocket", "daemon", "zero-config"]
