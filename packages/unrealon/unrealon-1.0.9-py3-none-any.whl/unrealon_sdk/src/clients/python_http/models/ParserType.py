from enum import Enum


class ParserType(str, Enum):

    ENCAR = "encar"
    MOBILE = "mobile"
    REALESTATE = "realestate"
    CUSTOM = "custom"
    GENERAL = "general"
