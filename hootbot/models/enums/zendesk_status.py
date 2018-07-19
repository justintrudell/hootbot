from enum import Enum


# Status constants for different states of a Zendesk Ticket
class ZendeskStatus(Enum):
    """
    Enum representing the different possibilities for payloads returned from messenger.
    """
    OPEN = 'open'
    SOLVED = 'solved'
    CLOSED = 'closed'
