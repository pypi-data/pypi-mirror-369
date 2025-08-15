from enum import Enum


class BroadcastPriority(str, Enum):

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"
