"""
Time Formatter Utility - UnrealOn Driver v3.0

Beautiful time formatting for CLI applications with HH:MM:SS display,
duration calculations, and human-readable intervals.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Union


class TimeFormatter:
    """
    Beautiful time formatting utility for CLI applications.
    
    Features:
    - HH:MM:SS format display
    - Duration calculations
    - Human-readable intervals
    - Elapsed time tracking
    - Next run time display
    """
    
    @staticmethod
    def format_duration(seconds: Union[int, float]) -> str:
        """
        Format duration in HH:MM:SS format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string like "01:23:45" or "00:05:30"
        """
        if seconds < 0:
            return "00:00:00"
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def format_time(dt: Optional[datetime] = None) -> str:
        """
        Format datetime in HH:MM:SS format.
        
        Args:
            dt: Datetime object (current time if None)
            
        Returns:
            Time string like "14:30:45"
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%H:%M:%S")
    
    @staticmethod
    def format_datetime(dt: Optional[datetime] = None) -> str:
        """
        Format datetime in full format.
        
        Args:
            dt: Datetime object (current time if None)
            
        Returns:
            Full datetime string like "2024-01-15 14:30:45"
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def parse_interval(interval: str) -> int:
        """
        Parse human-readable interval to seconds.
        
        Args:
            interval: Human-readable interval like "30m", "1h", "daily"
            
        Returns:
            Interval in seconds
            
        Raises:
            ValueError: If interval format is invalid
        """
        interval = interval.lower().strip()
        
        # Natural language
        interval_map = {
            "minutely": 60,
            "hourly": 3600,
            "daily": 86400,
            "weekly": 604800,
            "monthly": 2592000,  # 30 days
        }
        
        if interval in interval_map:
            return interval_map[interval]
        
        # Time units with numbers
        if interval.endswith('s'):
            return int(interval[:-1])
        elif interval.endswith('m'):
            return int(interval[:-1]) * 60
        elif interval.endswith('h'):
            return int(interval[:-1]) * 3600
        elif interval.endswith('d'):
            return int(interval[:-1]) * 86400
        elif interval.endswith('w'):
            return int(interval[:-1]) * 604800
        elif interval.endswith('mo'):
            return int(interval[:-2]) * 2592000
        
        # Try parsing as plain seconds
        try:
            return int(interval)
        except ValueError:
            raise ValueError(f"Invalid interval format: {interval}")
    
    @staticmethod
    def format_interval(seconds: int) -> str:
        """
        Format seconds back to human-readable interval.
        
        Args:
            seconds: Interval in seconds
            
        Returns:
            Human-readable string like "30m", "2h", "1d"
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m"
        elif seconds < 86400:
            return f"{seconds // 3600}h"
        elif seconds < 604800:
            return f"{seconds // 86400}d"
        else:
            return f"{seconds // 604800}w"
    
    @staticmethod
    def time_until(target_time: datetime) -> str:
        """
        Calculate time remaining until target time.
        
        Args:
            target_time: Target datetime
            
        Returns:
            Time remaining in HH:MM:SS format
        """
        now = datetime.now()
        if target_time <= now:
            return "00:00:00"
        
        diff = target_time - now
        return TimeFormatter.format_duration(diff.total_seconds())
    
    @staticmethod
    def elapsed_since(start_time: float) -> str:
        """
        Calculate elapsed time since start timestamp.
        
        Args:
            start_time: Start timestamp from time.time()
            
        Returns:
            Elapsed time in HH:MM:SS format
        """
        elapsed = time.time() - start_time
        return TimeFormatter.format_duration(elapsed)
    
    @staticmethod
    async def countdown_sleep(duration_seconds: int, callback=None, interval: float = 1.0):
        """
        Sleep with live countdown display that updates in place.
        
        Args:
            duration_seconds: Total sleep duration in seconds
            callback: Optional callback function to call with remaining time
            interval: Update interval in seconds (default 1.0)
        """
        import sys
        
        slept = 0
        while slept < duration_seconds:
            remaining = duration_seconds - slept
            
            if remaining > 0 and callback:
                remaining_time = TimeFormatter.format_duration(remaining)
                current_time = TimeFormatter.format_time()
                # Use \r to return to beginning of line and overwrite
                callback(current_time, remaining_time, remaining, update_in_place=True)
            
            sleep_chunk = min(interval, duration_seconds - slept)
            await asyncio.sleep(sleep_chunk)
            slept += sleep_chunk
        
        # Print newline after countdown finishes
        if callback:
            print()  # Move to next line when done


class ScheduleTimer:
    """
    Timer for scheduled operations with beautiful display.
    
    Features:
    - Real-time countdown
    - Elapsed time tracking
    - Next run calculation
    - Progress display
    """
    
    def __init__(self, interval: str):
        """
        Initialize timer with interval.
        
        Args:
            interval: Human-readable interval like "30m"
        """
        self.interval = interval
        self.interval_seconds = TimeFormatter.parse_interval(interval)
        self.start_time = time.time()
        self.last_run = None
        self.next_run = None
        self.run_count = 0
        
    def start_run(self):
        """Mark start of new run."""
        self.last_run = datetime.now()
        self.next_run = self.last_run + timedelta(seconds=self.interval_seconds)
        self.run_count += 1
    
    def get_elapsed_total(self) -> str:
        """Get total elapsed time since timer start."""
        return TimeFormatter.elapsed_since(self.start_time)
    
    def get_time_until_next(self) -> str:
        """Get time remaining until next run."""
        if self.next_run is None:
            return "00:00:00"
        return TimeFormatter.time_until(self.next_run)
    
    def get_next_run_time(self) -> str:
        """Get next run time formatted."""
        if self.next_run is None:
            return "Not scheduled"
        return TimeFormatter.format_datetime(self.next_run)
    
    def get_status_display(self) -> str:
        """
        Get beautiful status display.
        
        Returns:
            Multi-line status string with timer info
        """
        lines = [
            f"⏱️  Interval: {self.interval} ({TimeFormatter.format_interval(self.interval_seconds)})",
            f"🔄 Runs completed: {self.run_count}",
            f"⏰ Total elapsed: {self.get_elapsed_total()}",
        ]
        
        if self.next_run:
            lines.extend([
                f"🕐 Next run at: {TimeFormatter.format_time(self.next_run)}",
                f"⏳ Time remaining: {self.get_time_until_next()}",
            ])
        
        return "\n".join(lines)


class DaemonTimer:
    """
    Timer for daemon operations with uptime tracking.
    
    Features:
    - Uptime display
    - Heartbeat counting
    - Status monitoring
    - Connection time tracking
    """
    
    def __init__(self):
        """Initialize daemon timer."""
        self.start_time = time.time()
        self.heartbeat_count = 0
        self.last_heartbeat = None
        self.connection_time = None
        
    def heartbeat(self):
        """Record heartbeat."""
        self.heartbeat_count += 1
        self.last_heartbeat = datetime.now()
    
    def connect(self):
        """Mark connection established."""
        self.connection_time = datetime.now()
    
    def get_uptime(self) -> str:
        """Get daemon uptime."""
        return TimeFormatter.elapsed_since(self.start_time)
    
    def get_connection_duration(self) -> str:
        """Get connection duration."""
        if self.connection_time is None:
            return "Not connected"
        
        elapsed = time.time() - self.connection_time.timestamp()
        return TimeFormatter.format_duration(elapsed)
    
    def get_status_display(self) -> str:
        """
        Get beautiful daemon status display.
        
        Returns:
            Multi-line status string with daemon info
        """
        lines = [
            f"⏰ Uptime: {self.get_uptime()}",
            f"💓 Heartbeats: {self.heartbeat_count}",
        ]
        
        if self.last_heartbeat:
            lines.append(f"🕐 Last heartbeat: {TimeFormatter.format_time(self.last_heartbeat)}")
        
        if self.connection_time:
            lines.extend([
                f"🔌 Connected at: {TimeFormatter.format_time(self.connection_time)}",
                f"📡 Connection time: {self.get_connection_duration()}",
            ])
        
        return "\n".join(lines)
