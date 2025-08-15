"""
SDK Log Cleanup Utilities

Automatic log file cleanup functionality for UnrealOn SDK.
Provides smart log clearing for both parser development and internal SDK logging.
"""

import time
import logging
from pathlib import Path
from typing import Optional

# Global flag to ensure cleanup happens only once per application run
_CLEANUP_PERFORMED = False


def clear_old_sdk_logs(log_dir: Optional[str] = None) -> None:
    """
    Clear all *.log files older than 5 minutes in SDK logs directory.
    
    This function is called automatically when SDK starts to ensure clean logging.
    Targets both parser development logs and internal SDK logs.
    
    Args:
        log_dir: Custom log directory path. If None, uses default SDK logs location.
    """
    if log_dir is None:
        # Default SDK logs directory (at SDK root level)
        sdk_root = Path(__file__).parent.parent.parent
        logs_dir = sdk_root / "logs"
    else:
        logs_dir = Path(log_dir)
    
    if not logs_dir.exists():
        return
    
    # Clear logs older than 5 minutes (300 seconds)
    cutoff_time = time.time() - 300
    log_files = list(logs_dir.glob("*.log"))
    
    if not log_files:
        return
    
    print("🧹 SDK: Clearing old logs...")
    
    for log_path in log_files:
        try:
            # Check if file is older than 5 minutes
            if log_path.stat().st_mtime < cutoff_time:
                log_path.write_text("")
                print(f"🗑️  SDK: Cleared old log: {log_path.name}")
        except Exception as e:
            print(f"⚠️  SDK: Failed to clear log {log_path.name}: {e}")
    
    print("✅ SDK: Log cleanup completed")


def setup_sdk_logging_with_cleanup(parser_id: str, clear_logs: bool = True) -> logging.Logger:
    """
    Setup SDK logging with automatic cleanup on startup.
    
    This is the main function that SDK components should use to get a logger
    with automatic log cleanup functionality.
    
    Args:
        parser_id: Parser identifier for logger naming
        clear_logs: Whether to perform log cleanup on startup
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global _CLEANUP_PERFORMED
    
    # Perform automatic log cleanup only once per application run
    if clear_logs and not _CLEANUP_PERFORMED:
        clear_old_sdk_logs()
        _CLEANUP_PERFORMED = True
    
    # Create logger
    logger = logging.getLogger(f"unrealon_sdk.{parser_id}")
    
    # Set up basic configuration if not already configured
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with automatic directory creation
        sdk_root = Path(__file__).parent.parent.parent
        log_path = sdk_root / "logs" / "unrealon_sdk.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.setLevel(logging.INFO)
        logger.info(f"SDK logging configured with cleanup - Parser: {parser_id}")
    
    return logger


def clear_development_logs() -> None:
    """
    Clear development logger specific logs.
    
    This function targets internal SDK development logs specifically,
    used by DevelopmentLogger for internal SDK operations tracking.
    """
    try:
        sdk_root = Path(__file__).parent.parent.parent
        dev_logs_dir = sdk_root / "logs" / "development"
        
        if dev_logs_dir.exists():
            clear_old_sdk_logs(str(dev_logs_dir))
    except Exception as e:
        print(f"⚠️  SDK: Failed to clear development logs: {e}")


def clear_parser_logs() -> None:
    """
    Clear parser-specific logs.
    
    This function targets logs created by parser developers using LoggingService,
    typically stored in the main logs directory.
    """
    try:
        clear_old_sdk_logs()  # Uses default location
    except Exception as e:
        print(f"⚠️  SDK: Failed to clear parser logs: {e}")


# Main cleanup function called on SDK startup
def sdk_startup_cleanup() -> None:
    """
    Perform complete SDK log cleanup on startup.
    
    This function is called automatically when SDK components initialize
    to ensure clean logging environment for both development and parser logs.
    """
    global _CLEANUP_PERFORMED
    
    # Only perform cleanup once per application run
    if _CLEANUP_PERFORMED:
        return
        
    print("🚀 SDK: Starting log cleanup on startup...")
    
    # Clear both development and parser logs
    clear_development_logs()
    clear_parser_logs()
    
    _CLEANUP_PERFORMED = True
    print("✅ SDK: Startup log cleanup completed")
