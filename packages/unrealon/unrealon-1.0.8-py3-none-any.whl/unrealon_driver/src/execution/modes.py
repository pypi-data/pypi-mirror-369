"""
Execution mode enumeration and utilities for UnrealOn Driver v3.0
"""

from enum import Enum, auto
from typing import Any, Dict


class ExecutionMode(Enum):
    """Enumeration of available execution modes."""

    TEST = auto()  # Development testing
    DAEMON = auto()  # Production WebSocket service
    SCHEDULED = auto()  # Automated recurring execution
    INTERACTIVE = auto()  # Live development shell

    @classmethod
    def from_string(cls, mode_str: str) -> "ExecutionMode":
        """Convert string to ExecutionMode."""
        mode_map = {
            "test": cls.TEST,
            "daemon": cls.DAEMON,
            "scheduled": cls.SCHEDULED,
            "interactive": cls.INTERACTIVE,
        }

        mode_str = mode_str.lower().strip()
        if mode_str not in mode_map:
            raise ValueError(f"Unknown execution mode: {mode_str}")

        return mode_map[mode_str]

    def to_string(self) -> str:
        """Convert ExecutionMode to string."""
        return self.name.lower()

    def get_description(self) -> str:
        """Get human-readable description."""
        descriptions = {
            self.TEST: "Development testing and debugging",
            self.DAEMON: "Production WebSocket service",
            self.SCHEDULED: "Automated recurring execution",
            self.INTERACTIVE: "Live development shell",
        }
        return descriptions[self]
