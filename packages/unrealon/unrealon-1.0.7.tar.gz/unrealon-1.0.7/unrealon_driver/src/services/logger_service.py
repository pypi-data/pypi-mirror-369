"""
Logger Service for UnrealOn Driver v3.0

Intelligent logging service with file rotation and structured output.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from unrealon_driver.src.dto.services import LoggerConfig
from logging.handlers import RotatingFileHandler


class LoggerService:
    """
    📝 Logger Service - Intelligent Logging

    Zero-configuration logging with:
    - Console and file output
    - Automatic log rotation
    - Structured logging for production
    - Integration with unrealon_sdk development logger
    """

    def __init__(
        self,
        config: LoggerConfig,
        parser_id: str = "unknown",
        parser_name: str = "UnrealOn Parser",
    ):
        """Initialize logger service."""
        self.config = config
        self.parser_id = parser_id
        self.parser_name = parser_name

        # Setup logger
        self.logger = logging.getLogger(f"unrealon_driver.{parser_id}")
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        # Clear any existing handlers
        self.logger.handlers.clear()

        # Set log level using Pydantic config
        log_level = getattr(logging, self.config.log_level.value.upper())
        self.logger.setLevel(log_level)

        # Console handler
        if self.config.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)  # Use same level as main logger

            # Console formatter (using standard format from config)
            console_formatter = logging.Formatter(
                fmt=self.config.log_format, datefmt=self.config.date_format
            )

            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # File handler
        if self.config.file_output:
            log_dir = (
                Path(self.config.log_dir)
                if self.config.log_dir
                else Path("system/logs")
            )
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file_name = self.config.log_file or f"{self.parser_id}.log"
            log_file = log_dir / log_file_name

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self._parse_size(self.config.max_file_size),
                backupCount=self.config.backup_count,
            )

            file_level = getattr(logging, self.config.log_level.value.upper())
            file_handler.setLevel(file_level)

            # File formatter (always use standard format)
            file_formatter = logging.Formatter(
                fmt=self.config.log_format, datefmt=self.config.date_format
            )

            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        # Initial log message
        self.logger.info(
            f"Logger initialized for {self.parser_name} ({self.parser_id})"
        )

    def _get_standard_formatter(self) -> logging.Formatter:
        """Get standard text formatter."""
        format_str = (
            self.config.format_string or "[{asctime}] {levelname} | {name} | {message}"
        )
        date_format = self.config.date_format or "%Y-%m-%d %H:%M:%S"

        return logging.Formatter(format_str, datefmt=date_format, style="{")

    def _get_colored_formatter(self) -> logging.Formatter:
        """Get colored formatter for console output."""
        # Color codes
        colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
            "RESET": "\033[0m",  # Reset
        }

        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                if record.levelname in colors:
                    record.levelname = (
                        f"{colors[record.levelname]}{record.levelname}{colors['RESET']}"
                    )
                return super().format(record)

        format_str = "[{asctime}] {levelname} | {name} | {message}"
        return ColoredFormatter(format_str, datefmt="%H:%M:%S", style="{")

    def _get_json_formatter(self) -> logging.Formatter:
        """Get JSON formatter for structured logging."""
        import json

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "parser_id": self.parser_id,
                    "parser_name": self.parser_name,
                }

                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)

                return json.dumps(log_entry)

        return JSONFormatter()

    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes."""
        size_str = size_str.upper().strip()

        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)  # Assume bytes

    # ==========================================
    # LOGGING METHODS
    # ==========================================

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)

    # ==========================================
    # SERVICE MANAGEMENT
    # ==========================================

    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes."""
        size_str = size_str.upper().strip()

        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            # Assume bytes if no unit
            return int(size_str)

    def health_check(self) -> dict:
        """Check logger service health."""
        return {
            "status": "healthy",
            "log_level": self.logger.level,
            "handlers_count": len(self.logger.handlers),
            "console_output": self.config.console_output,
            "file_output": self.config.file_output,
        }

    async def cleanup(self):
        """Clean up logger resources."""
        # Close all handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        self.logger.info("Logger service cleanup completed")

    def __repr__(self) -> str:
        return f"<LoggerService(parser_id={self.parser_id}, level={self.logger.level})>"
