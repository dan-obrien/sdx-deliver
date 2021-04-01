from enum import Enum


class OutputType(Enum):
    """
    ENUM for different types of survey submission
    """
    DAP = 1
    LEGACY = 2
    FEEDBACK = 3
    COMMENTS = 4
    SEFT = 5
