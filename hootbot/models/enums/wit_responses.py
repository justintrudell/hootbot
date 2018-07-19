from enum import Enum


class WitResponses(Enum):
    """
    Enum representing the different possibilities for a response from Wit.
    """
    INTENT = 1
    ENTITY = 2
