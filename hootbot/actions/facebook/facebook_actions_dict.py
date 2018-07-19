from hootbot.models.enums.payloads import Payloads
from hootbot.actions.facebook import facebook_actions
from hootbot.actions.wit import wit_actions

facebook_actions_dict = {
    # POSTBACK ACTIONS
    Payloads.GET_STARTED: facebook_actions.get_started_action,
    Payloads.NEW: facebook_actions.new_to_hootsuite_action,
    Payloads.SOCIAL_OR_SUPPORT: facebook_actions.social_or_support_action,
    Payloads.ASK_TIPS: facebook_actions.daily_tips_action,
    Payloads.SOCIAL: facebook_actions.social_networks_action,
    Payloads.LEARNING: facebook_actions.learning_objectives_action,
    Payloads.ARTICLE_LINKS: facebook_actions.article_links_action,
    Payloads.SUPPORT: facebook_actions.support_action,
    Payloads.DONE: facebook_actions.done_action,
    Payloads.RESTART_SCHEDULED_MESSAGES: facebook_actions.restart_scheduled_messages_action,
    Payloads.RECENTLY_SOLVED_TICKET: facebook_actions.recently_solved_action,

    # WIT ACTIONS
    Payloads.WIT_ARTICLE_LINKS: wit_actions.article_links_action,
    Payloads.FAILED_INTERPRET: wit_actions.failed_interpret_action,
    Payloads.WIT_SUPPORT_OR_LEARN: wit_actions.support_or_learn_action,
    Payloads.WIT_STOP_TIPS: wit_actions.reply_to_stop_tips_action
}
