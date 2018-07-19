from enum import Enum


# State constants to determine the state a user is in
class SessionStates(Enum):
    """
    Enum representing the different possibilities for payloads returned from messenger.
    """
    DEFINING_SUPPORT_REQUEST = '1'
    ADDING_COMMENT_TO_TICKET = '2'
    REPLYING_TO_RECENT_TICKET_QUESTION = '3'
    PROVIDING_EMAIL = '4'
