from enum import Enum


class MaintenanceMode(str, Enum):

    FULL_SYSTEM = "full_system"
    READ_ONLY = "read_only"
    PARTIAL_SERVICE = "partial_service"
    SCHEDULED_RESTART = "scheduled_restart"
