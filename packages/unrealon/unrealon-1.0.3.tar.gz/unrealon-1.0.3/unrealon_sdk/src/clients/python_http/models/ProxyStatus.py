from enum import Enum


class ProxyStatus(str, Enum):

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    BLOCKED = "blocked"
    ERROR = "error"
