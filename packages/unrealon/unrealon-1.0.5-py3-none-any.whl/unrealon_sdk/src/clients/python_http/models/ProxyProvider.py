from enum import Enum


class ProxyProvider(str, Enum):

    PROXY6 = "proxy6"
    PROXY_CHEAP = "proxy_cheap"
    PROXY_SELLER = "proxy_seller"
    OXYLABS = "oxylabs"
    BRIGHT_DATA = "bright_data"
