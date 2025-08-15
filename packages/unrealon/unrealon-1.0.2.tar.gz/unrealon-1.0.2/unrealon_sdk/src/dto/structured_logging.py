"""
Structured Logging Data Transfer Objects

DTO models for enterprise structured logging service functionality.
These models provide type-safe structured logging operations and configuration.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import deque
import threading
import asyncio

from pydantic import BaseModel, Field, ConfigDict


@dataclass
class LogBuffer:
    """Thread-safe buffer for batching log entries using auto-generated models."""

    max_size: int = 100
    flush_interval_seconds: float = 5.0

    # Buffer storage (will hold LogEntryMessage objects)
    entries: deque[Any] = field(default_factory=deque)
    lock: threading.Lock = field(default_factory=threading.Lock)

    # Flush callback
    flush_callback: Optional[Any] = None

    # Background task
    _flush_task: Optional[asyncio.Task[None]] = None
    _should_stop: bool = False

    def add_entry(self, entry: Any) -> None:
        """Add entry to buffer, trigger flush if needed."""
        with self.lock:
            self.entries.append(entry)

            # Auto-flush if buffer is full - use non-blocking approach
            if len(self.entries) >= self.max_size:
                # Schedule flush without blocking current context
                try:
                    loop = asyncio.get_running_loop()
                    if loop and not loop.is_closed():
                        loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(self._flush_now())
                        )
                except RuntimeError:
                    # No event loop running - skip flush, will be handled by auto-flush
                    pass

    async def start_auto_flush(self) -> None:
        """Start automatic flushing task."""
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._auto_flush_loop())

    async def stop_auto_flush(self) -> None:
        """Stop automatic flushing and flush remaining entries."""
        self._should_stop = True
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self._flush_now()

    async def _auto_flush_loop(self) -> None:
        """Background auto-flush loop."""
        while not self._should_stop:
            try:
                await asyncio.sleep(self.flush_interval_seconds)
                await self._flush_now()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Note: logger import needed in actual usage
                print(f"Error in auto-flush loop: {e}")

    async def _flush_now(self) -> None:
        """Flush current buffer contents."""
        entries_to_flush = []

        with self.lock:
            if self.entries:
                entries_to_flush = list(self.entries)
                self.entries.clear()

        if entries_to_flush and self.flush_callback:
            try:
                await self._call_flush_callback(entries_to_flush)
            except Exception as e:
                print(f"Error in flush callback: {e}")

    async def _call_flush_callback(self, entries: List[Any]) -> None:
        """Call flush callback, handling both sync and async callbacks."""
        if self.flush_callback is not None:
            if asyncio.iscoroutinefunction(self.flush_callback):
                await self.flush_callback(entries)
            else:
                self.flush_callback(entries)


__all__ = [
    # Buffer models
    "LogBuffer",
]
