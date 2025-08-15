from enum import Enum

class TTL_Type(int, Enum):
    SHORT = 1
    LONG = 2
    EXTRA_LONG = 3