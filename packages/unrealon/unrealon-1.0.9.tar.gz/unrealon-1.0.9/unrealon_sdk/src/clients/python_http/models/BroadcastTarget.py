from enum import Enum


class BroadcastTarget(str, Enum):

    ALL_USERS = "all_users"
    ADMINS_ONLY = "admins_only"
    DEVELOPERS_ONLY = "developers_only"
    PARSERS_ONLY = "parsers_only"
    SPECIFIC_ROOM = "specific_room"
    SPECIFIC_USERS = "specific_users"
