from hootbot.models.dao.social_network import SocialNetwork
from hootbot.models.dao.learning_objective import LearningObjective
from hootbot.models.dao.user_objectives import UserObjective
from hootbot.models.dao.scheduled_message import ScheduledMessage
from hootbot.database.database import db
from hootbot.constants import constants
from hootbot.logging.logger import bot_log
from hootbot.models.enums.wit_responses import WitResponses
from hootbot.actions.facebook import facebook_actions
from hootbot.actions.wit.wit_responses_dict import wit_responses
from hootbot.api.facebook import facebook_requests
from hootbot.models.enums.payloads import Payloads
from hootbot.helpers.action_helpers import trim_payload


def run_actions(event, resp):
    """
    Determines and runs required actions for the given Wit response
    :param event: Payload for the event returned by Facebook
    :param resp: Response returned by the Wit API
    """
    from hootbot.actions.wit.wit_actions_dict import wit_actions_dict
    bot_log("Wit response received: " + str(resp))

    matching_response, query = get_matching_response(resp)
    if matching_response == WitResponses.ENTITY:
        wit_actions_dict[query](event['sender']['id'], query)
    else:
        wit_actions_dict[query](event)


def get_matching_response(resp):
    """
    Match keys in wit_responses to keys in response, and return the first match.
    :param resp: Response received from the Wit API
    :return: Tuple containing the matching WitResponses enum and the value returned by Wit API
    """
    for key in resp['entities']:
        if key in wit_responses:
            return wit_responses[key], resp['entities'][key][0]['value']
    raise KeyError("No matching key found in the Wit response")


def objectives_for_network_action(fb_id, network):
    """
    Handles the postback from Wit when the user typed in a social network.
    :param fb_id: Facebook user ID
    :param network: The social network that was typed in.
    """
    text = "Would you like to learn about:"
    network = SocialNetwork.query.filter_by(display_text=network).first()
    facebook_actions.send_objectives_helper(fb_id, text, network)


def networks_for_objective_action(fb_id, objective):
    """
    Sends a list of networks to the user for a given learning objective.
    :param fb_id: Facebook user ID
    :param objective: The display_text of the desired learning objective
    """
    text = constants.I_CAN_TEACH_ABOUT_OBJECTIVE % objective
    networks = SocialNetwork.query.all()
    objective_text = LearningObjective.query.filter_by(display_text=objective).first().display_text
    options = [("%s_%s" % (x.id, objective_text), x.display_text) for x in networks]
    facebook_requests.post_button_list(fb_id, text, Payloads.WIT_ARTICLE_LINKS, options)


def article_links_action(event):
    """
    At this point, the user has selected a network and objective, so we display article links
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    full_payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.WIT_ARTICLE_LINKS)
    split_str = full_payload.split("_")
    network = SocialNetwork.query.filter_by(id=split_str[0]).first()
    objective = LearningObjective.query.filter_by(network=network).filter_by(display_text=split_str[1]).first()
    text = constants.HERES_SOME_INFO_ON % (objective.display_text, network.display_text)
    facebook_requests.post_text(recipient_id, text)
    db.session().add(UserObjective(recipient_id, objective.id))
    db.session().commit()
    facebook_actions.send_article_links_helper(recipient_id, network, objective)


def failed_interpret_action(event):
    """
    Handles the postback from when the NLP algorithm can't interpret a user's message.
    :param event: JSON containing information about the interaction.
    """
    from hootbot.actions.facebook.facebook_actions_dict import facebook_actions_dict
    payload = Payloads(trim_payload(full_str=event['postback']['payload'], payload=Payloads.FAILED_INTERPRET))
    # 'payload' will be either SOCIAL, SUPPORT or DONE, so dispatch to corresponding actions
    facebook_actions_dict[payload](event)


def handle_failed_interpretation(event):
    """
    Handles the case when the NLP algorithm failed to interpret the user's message
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    options = [(Payloads.SOCIAL.value, "Teach me!"),
               (Payloads.SUPPORT.value, "Speak to Support"),
               (Payloads.DONE.value, "Done for today")]
    facebook_requests.post_image(recipient_id, constants.THINKING_OWLY_GIF)
    facebook_requests.post_button_list(recipient_id, constants.BEYOND_ME, Payloads.FAILED_INTERPRET, options)


def assumed_support_request_action(event):
    """
    Handles the postback from Wit when it's been assumed the user needs support.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    options = [(Payloads.SUPPORT.value, "Message Support"),
               (Payloads.HELP.value, "Help Articles"),
               (Payloads.SOCIAL.value, "Keep learning!")]
    facebook_requests.post_button_list(recipient_id, constants.YOU_MIGHT_NEED_SUPPORT,
                                       Payloads.WIT_SUPPORT_OR_LEARN, options)


def support_or_learn_action(event):
    """
    Handles the postback from when the user confirms they want support after Wit assumed they did.
    :param event: JSON containing information about the interaction.
    """
    payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.WIT_SUPPORT_OR_LEARN)
    if payload == Payloads.SUPPORT.value:
        facebook_actions.support_action(event)
    elif payload == Payloads.HELP.value:
        facebook_requests.post_text(event['sender']['id'], constants.HELP_CENTER_HAS_GREAT_INFO)
        facebook_requests.post_generic_template(event['sender']['id'],
                                                "Help Desk Articles",
                                                "https://hootsuite.com/uploads/images/stock/Help_Desk_Articles.jpg",
                                                "https://hootsuite.com/help")
    else:
        facebook_actions.social_networks_action(event)


def stop_tips_action(event):
    """
    Handles the postback from when the user says they want to stop the daily tips.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']
    options = [(Payloads.YES.value, "Yes"),
               (Payloads.NO.value, "No")]
    facebook_requests.post_button_list(recipient_id, constants.ARE_YOU_SURE_STOP_TIPS, Payloads.WIT_STOP_TIPS, options)


def reply_to_stop_tips_action(event):
    """
    Handles the user saying whether or not they want to stop tips.
    :param event: JSON containing information about the interaction.
    """
    recipient_id = event['sender']['id']

    payload = trim_payload(full_str=event["postback"]["payload"], payload=Payloads.WIT_STOP_TIPS)
    if payload == Payloads.YES.value:
        ScheduledMessage.query.filter_by(facebook_id=recipient_id).delete()
        db.session().commit()
        facebook_requests.post_text(recipient_id, constants.IF_YOU_CHANGE_YOUR_MIND)
    elif payload == Payloads.NO.value:
        facebook_requests.post_text(recipient_id, constants.GREAT_STAY_TUNED)
