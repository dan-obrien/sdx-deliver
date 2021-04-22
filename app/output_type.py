from enum import Enum


class OutputType(Enum):
    """
    ENUM for different types of survey submission
    """
    DAP = 1
    LEGACY = 2
    HYBRID = 3
    FEEDBACK = 4
    COMMENTS = 5
    SEFT = 6
