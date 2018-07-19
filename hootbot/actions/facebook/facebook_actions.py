from hootbot.models.enums.payloads import Payloads
from hootbot.api.facebook import facebook_requests
from hootbot.constants import constants
from hootbot.helpers.action_helpers import trim_payload, optimize_link_list
from hootbot.helpers.db_helpers import get_unselected_objectives
from hootbot.database.database import redis_store
from hootbot.models.dao.user_objectives import UserObjective
from hootbot.models.dao.social_network import SocialNetwork
from hootbot.models.dao.learning_objective import LearningObjective
from hootbot.models.dao.user import User
from hootbot.models.dao.scheduled_message import ScheduledMessage
from hootbot.models.enums.session_states import SessionStates
from hootbot.models.enums.zendesk_status import ZendeskStatus
from hootbot.models.dao.zendesk_ticket import ZendeskTicket
from hootbot.database.database import db
from hootbot.logging.logger import bot_log


def get_started_action(event):
    """
    Handles the postback from when a user taps on 'Get Started'.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    facebook_requests.post_text(recipient_id, constants.HI_THERE_IM_OWLY)
    facebook_requests.post_image(recipient_id, constants.OWLY_WAVING_GIF)

    options = [(Payloads.ASK_TIPS.value, "Teach me!"),
               (Payloads.SUPPORT.value, "Support please!")]
    facebook_requests.post_button_list(recipient_id,
                                       constants.WANT_TO_LEARN_OR_SUPPORT,
                                       Payloads.SOCIAL_OR_SUPPORT,
                                       options)


def daily_tips_action(event):
    recipient_id = event['sender']['id']

    options = [(Payloads.YES.value, "Great! Hook me up!"),
               (Payloads.NO.value, "I'm already a pro!")]
    facebook_requests.post_button_list(recipient_id, constants.TIP_EACH_MORNING, Payloads.NEW, options)


def new_to_hootsuite_action(event):
    """
    Handles the postback from when the user answers whether or not they want daily tips.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.NEW)

    if payload == Payloads.YES.value:

        scheduled_message, existed = ScheduledMessage.get_or_create(
            search_key={
                "facebook_id": recipient_id
            },
            facebook_id=recipient_id,
            topic="daily_social_tips")

        if existed:
            text = constants.CURRENTLY_RECEIVING_TIPS_ON_DAY % scheduled_message.next_day_to_send
            options = [(Payloads.YES.value, "Yes please!"),
                       (Payloads.NO.value, "No thanks!")]
            facebook_requests.post_button_list(recipient_id, text, Payloads.RESTART_SCHEDULED_MESSAGES, options)
            return
        else:
            facebook_requests.post_text(recipient_id, constants.EXPECT_TIP_EACH_WEEKDAY)
    else:
        facebook_requests.post_text(recipient_id, constants.STEP_FURTHER_GET_CERTIFIED)
        facebook_requests.post_generic_template(recipient_id,
                                                "Hootsuite Pro Certification",
                                                "https://hootsuite.com/uploads/images/stock/Chatbot-Daily-Icons-Hoot-Pro.png",
                                                "https://education.hootsuite.com/enroll/20308?coupon=H00tB0tPlatform")
    social_networks_action(event)


# For now, this is unused, and we fully restart each time - but it could be useful in the future
def short_intro_action(event):
    """
    Assume user has already seen the intro options about scheduled messages, and skip that part.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    facebook_requests.post_text(recipient_id, constants.HI_THERE_IM_OWLY)
    facebook_requests.post_image(recipient_id, constants.OWLY_WAVING_GIF)

    options = [(Payloads.SOCIAL.value, "Teach me!"),
               (Payloads.SUPPORT.value, "Support please!")]
    facebook_requests.post_image(recipient_id, constants.WAVING_QUESTION_MARKS_GIF)
    facebook_requests.post_button_list(recipient_id,
                                       constants.WANT_TO_LEARN_OR_SUPPORT,
                                       Payloads.SOCIAL_OR_SUPPORT,
                                       options)


def social_networks_action(event):
    """
    Handles the postback from when the user answers that they want to learn more about social.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    options = [(x.id, x.display_text) for x in SocialNetwork.query.all()]
    facebook_requests.post_button_list(recipient_id, constants.WHAT_NETWORK, Payloads.LEARNING, options)


def learning_objectives_action(event):
    """
    Handles the postback when the user selects a social network.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    text = "Would you like to learn about:"
    network_payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.LEARNING)
    network = SocialNetwork.query.filter_by(id=network_payload).first()
    send_objectives_helper(recipient_id, text, network)


def article_links_action(event):
    """
    Handles the postback when the user selects a learning objective from a social network, and we need to display links.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    objective_payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.ARTICLE_LINKS)

    # Handle possible auxiliary options of switching networks or ending session
    if objective_payload == Payloads.SWITCH.value:
        switch_networks_action(event)
        return
    elif objective_payload == Payloads.DONE.value:
        done_action(event)
        return

    # Retrieve and send the list of article links
    objective = LearningObjective.query.filter_by(id=objective_payload).first()
    text = constants.HERES_SOME_INFO_ON % (objective.display_text, objective.network.display_text)
    facebook_requests.post_text(recipient_id, text)

    db.session().add(UserObjective(recipient_id, objective.id))
    db.session().commit()
    send_article_links_helper(recipient_id, objective.network, objective)


def restart_scheduled_messages_action(event):
    """
    Handles the postback from when the user claims they want to restart their scheduled messages.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.RESTART_SCHEDULED_MESSAGES)

    if payload == Payloads.YES.value:
        message = ScheduledMessage.query.filter_by(facebook_id=recipient_id).first()
        message.next_day_to_send = 1
        db.session().commit()
        facebook_requests.post_text(recipient_id, constants.SCHEDULED_TIPS_RESET)
    social_networks_action(event)


def social_or_support_action(event):
    """
    Handles the postback from when the user answers whether they want to learn or want support.
    :param event: JSON containing information about the interaction.
    """
    from hootbot.actions.facebook.facebook_actions_dict import facebook_actions_dict
    payload = Payloads(trim_payload(full_str=event['postback']['payload'], payload=Payloads.SOCIAL_OR_SUPPORT))
    # 'payload' will be either SOCIAL or SUPPORT, so dispatch to corresponding actions
    facebook_actions_dict[payload](event)


def switch_networks_action(event):
    """
    Handles the postback from when the user claims they want to switch networks.
    :param event: JSON containing information about the interaction.
    """
    UserObjective.clear_selected_objectives(event['sender']['id'])
    social_networks_action(event)


def support_action(event):
    """
    Handles the postback from when the user claims they want to speak to support.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    user = User.query.filter_by(id=recipient_id).first()

    # If the user has an email address defined, we skip asking for their email
    if user.email:
        facebook_requests.post_text(recipient_id, constants.SUPPORT_REQUEST_ALREADY_EMAIL)
        redis_store.set(recipient_id, SessionStates.DEFINING_SUPPORT_REQUEST.value)
    # If we didn't have their email, we first ask them to provide that, and validate
    else:
        facebook_requests.post_text(recipient_id, constants.GET_EMAIL_FIRST)
        redis_store.set(recipient_id, SessionStates.PROVIDING_EMAIL.value)


def recent_ticket_question_action(event):
    """
    Handles the situation where the user has had their ticket 'solved' but not yet 'closed'.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    options = [(Payloads.ADD_TO_TICKET.value, "Add Details"),
               (Payloads.NEW.value, "New Issue"),
               (Payloads.LEARNING.value, "Start Learning!")]
    facebook_requests.post_button_list(recipient_id,
                                       constants.RECENTLY_SOLVED,
                                       Payloads.RECENTLY_SOLVED_TICKET,
                                       options)
    redis_store.set(recipient_id, SessionStates.REPLYING_TO_RECENT_TICKET_QUESTION.value)


def recently_solved_action(event):
    """
    Handles the user's reply to the inquiry about a recently solved ticket.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.RECENTLY_SOLVED_TICKET)

    if payload == Payloads.ADD_TO_TICKET.value:
        redis_store.set(recipient_id, SessionStates.ADDING_COMMENT_TO_TICKET.value)
        facebook_requests.post_image(recipient_id, constants.OWLY_LISTENING_GIF)
        facebook_requests.post_text(recipient_id, constants.ADD_COMMENT_TO_TICKET)

    elif payload == Payloads.NEW.value:
        ZendeskTicket.query.filter_by(user_id=recipient_id, status=ZendeskStatus.SOLVED.value).delete()
        db.session().commit()
        support_action(event)

    elif payload == Payloads.LEARNING.value:
        ZendeskTicket.query.filter_by(user_id=recipient_id, status=ZendeskStatus.SOLVED.value).delete()
        db.session().commit()
        facebook_requests.post_image(recipient_id, constants.OWLY_YES_GIF)
        facebook_requests.post_text(recipient_id, constants.REMEMBER_YOU_CAN_ASK)
        social_networks_action(event)


def done_action(event):
    """
    Handles the postback from when the user claims they're done.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    facebook_requests.post_text(recipient_id, constants.THANKS_FOR_STOPPING_BY)
    facebook_requests.post_image(recipient_id, constants.FIST_BUMP_GIF)

    UserObjective.query.filter_by(user_id=recipient_id).delete()
    db.session().commit()


def send_article_links_helper(recipient_id, network, objective):
    """
    Helper method to send a list of article links to the user.
    :param recipient_id: Facebook ID of the user this message will be sent to.
    :param network: Social network to retrieve the links for.
    :param objective: Learning objective to retrieve the links for.
    """
    links = objective.article_links

    try:
        chunk_link_list = optimize_link_list(links)
        for article_links in chunk_link_list:
            facebook_requests.post_url_list(recipient_id, article_links)
    except ValueError as e:

        bot_log("Optimization of the list of links failed with the following message: %s" % e.message)
        facebook_requests.post_text(recipient_id, constants.SORRY_SOMETHING_WENT_WRONG)
    # Provide the user with more learning options for this network
    text = "Is there anything else you'd like to learn about %s today?" % network.display_text
    send_objectives_helper(recipient_id, text, network)


def send_objectives_helper(recipient_id, text, network):
    """
    Helper method used to send learning objectives to the user.
    :param recipient_id: ID of the Facebook user
    :param text: Text to be sent along with the options
    :param network: SocialNetwork object that the options should be retrieved for
    """
    objectives = get_unselected_objectives(network, recipient_id)
    if not objectives:
        # No more learning objectives to show in this scenario, so update the text
        text = constants.ANYTHING_ELSE_TODAY
    objective_options = [(x.id, x.display_text) for x in objectives]
    options = objective_options + [
        (Payloads.SWITCH.value, "Switch Networks"),
        (Payloads.DONE.value, "I'm done!")
    ]
    facebook_requests.post_button_list(recipient_id, text, Payloads.ARTICLE_LINKS, options)
