from enum import Enum


# Payload constants that will be returned by Messenger API
class Payloads(Enum):
    """"
    Enum representing the different possibilities for payloads returned from messenger.
    """
    # POSTBACK FLOW
    GET_STARTED = 'GET_STARTED'
    NEW = 'NEW'
    SOCIAL_OR_SUPPORT = 'SOCIAL_OR_SUPPORT'
    ASK_TIPS = 'ASK_TIPS'
    SOCIAL = 'SOCIAL'
    LEARNING = 'LEARNING'
    ARTICLE_LINKS = 'ARTICLE_LINKS'
    SWITCH = 'SWITCH'
    DONE = 'DONE'
    YES = 'YES'
    NO = 'NO'
    TEACH = 'TEACH'
    SUPPORT = 'SUPPORT'
    FAILED_INTERPRET = 'FAILED_INTERPRET'
    RESTART_SCHEDULED_MESSAGES = 'RESTART_SCHEDULED_MESSAGES'
    ADD_TO_TICKET = 'ADD_TO_TICKET'
    RECENTLY_SOLVED_TICKET = 'RECENTLY_SOLVED_TICKET'
    HELP = 'HELP'

    # WIT NLP FLOW
    WIT_ARTICLE_LINKS = 'WIT_ARTICLE_LINKS'
    WIT_SUPPORT_OR_LEARN = 'WIT_SUPPORT_OR_LEARN'
    WIT_STOP_TIPS = 'WIT_STOP_TIPS'

