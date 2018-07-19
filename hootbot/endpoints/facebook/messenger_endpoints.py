from flask import Blueprint, request
import json
import time

from hootbot.helpers import endpoint_helpers
from hootbot.logging.logger import bot_log
from hootbot.models.dao.zendesk_ticket import ZendeskTicket
from hootbot.models.enums.payloads import Payloads
from hootbot.models.enums.session_states import SessionStates
from hootbot.actions.facebook.facebook_actions_dict import facebook_actions_dict
from hootbot.database.database import db
from hootbot.api.facebook import facebook_requests
from hootbot.database.database import redis_store
from hootbot.helpers.endpoint_helpers import validate_email
from hootbot.models.dao.user import User
from hootbot.actions.facebook import facebook_actions
from hootbot.api.wit import wit_requests
from hootbot.actions.wit import wit_actions
from hootbot.api.zendesk import zendesk_requests
from hootbot.constants import constants

facebook_api = Blueprint("facebook_api", __name__)


@facebook_api.route('/', methods=['GET'])
def handle_verification():
    bot_log("Handling Verification...")
    if request.args.get('hub.verify_token', '') == 'hootastic':
        bot_log("Verification successful!")
        return request.args.get('hub.challenge', '')
    else:
        bot_log("Verification failed!")
        return 'Error, wrong validation token'


@facebook_api.route('/', methods=['POST'])
def handle_messages():
    payload = request.get_data()
    handle_messaging_events(payload)
    return "ok"


def handle_messaging_events(payload):
    """
    Handles a POST from the Messenger API, corresponding to an interaction from a user.
    :param payload: The JSON payload from the POST request.
    """
    try:
        data = json.loads(payload)
        messaging_events = data['entry'][0]['messaging']
        for event in messaging_events:
            recipient_id = event['sender']['id']
            res = zendesk_flow(recipient_id)
            if not res:
                return
            # Add this user's Facebook Page ID to the database if it doesn't yet exist
            user = User.get_or_create(search_key={'id': recipient_id}, fb_id=recipient_id)[0]
            if not handle_support_paths(event, user):
                return
            # Handle the cases where the message is either raw text or a postback
            elif 'postback' in event:
                handle_postback(event)
            elif 'message' in event and 'text' in event['message']:
                handle_text_message(event)
            elif endpoint_helpers.event_is_image(event):
                wit_actions.handle_failed_interpretation(event)
            else:
                bot_log("Unable to handle messaging event %s" % event)
    except (KeyError, ValueError) as e:
        bot_log("Handling of message events failed with following message: %s" % e)


def zendesk_flow(recipient_id):
    """
    Temporary function to handle the migration of users with currently open tickets when Zendesk was turned on.
    This function should be removed once all of these tickets have been closed and migrated.
    """
    fb_json = facebook_requests.get_user_info(recipient_id)
    first_name = fb_json['first_name']
    last_name = fb_json['last_name']
    name = str(first_name + last_name).strip().replace(' ', '').lower()
    users = User.query.filter_by(first_name=name).all()
    for user in users:
        if user.id == user.zendesk_id:
            new_user = User(fb_id=recipient_id, first_name=first_name, last_name=last_name, zendesk_id=user.zendesk_id)
            db.session().add(new_user)
            ZendeskTicket.query.filter_by(user_id=user.zendesk_id).delete()
            User.query.filter_by(id=user.id).delete()
            facebook_requests.post_text(recipient_id,
                                        "Hello! We've recently activated a bot on our Facebook page. To continue "
                                        "helping you with your active support issue, please provide your email.")
            redis_store.set(recipient_id, SessionStates.PROVIDING_EMAIL.value)
            db.session().commit()
            return False
        db.session().commit()
    return True


def handle_postback(event):
    """
    Handles a postback due to a user interacting with the bot.
    :param event: JSON containing information about the interaction.
    """
    try:
        # Parse the key from the postback, removing 'POSTBACK_' and passing to the dictionary
        query_payload = Payloads(event["postback"]["payload"].split("?=")[0])
        facebook_actions_dict[query_payload](event)
    except (KeyError, IndexError, TypeError, ValueError) as e:
        bot_log("Handling of postback failed with the following message: %s" % e.message)
        raise


def handle_support_paths(event, user):
    """
    Helper method to handle different states of a customer support flow a user may be in.
    This section has various different rules and is thus heavily commented for clarification.
    :param event: JSON containing information about the interaction.
    :param user: The User object these paths are for
    :return: True if execution should continue handling the event, False if not.
    """
    recipient_id = event['sender']['id']
    user_state = redis_store.get(recipient_id)

    # If this is a postback and the user has open tickets, we can't go through a normal postback flow
    # because that will interfere with the Zendesk integration and adding comments to the ticket.
    # Instead, we don't allow them to interact with buttons while a ticket is currently open.
    if 'postback' in event and (user.get_open_tickets()
                                or user_state == SessionStates.DEFINING_SUPPORT_REQUEST.value
                                or user_state == SessionStates.ADDING_COMMENT_TO_TICKET.value):
        facebook_requests.post_text(recipient_id, constants.LET_YOU_GET_BACK_TO_THAT)
    # This state occurs after the user had a solved, but not closed, ticket, and we asked them whether
    # they wanted to add a comment to the solved ticket, create a new ticket, or keep learning.
    # We take action on what they replied in the below code block.
    elif user_state == SessionStates.REPLYING_TO_RECENT_TICKET_QUESTION.value:
        redis_store.delete(recipient_id)
        if 'postback' in event:
            handle_postback(event)
        else:
            facebook_requests.post_text(recipient_id, "Please select one of the options in the menu below!")
            facebook_actions.recent_ticket_question_action(event)
    # When a user wants to create a ticket, if their user object does not have an email already attached to it
    # in the database, we ask them for it and handle validation in the following branch.
    elif user_state == SessionStates.PROVIDING_EMAIL.value:
        if 'message' in event and 'text' in event['message']:
            message = event['message']['text'].strip()
            if message.lower() == 'cancel':
                redis_store.delete(recipient_id)
                facebook_actions.social_networks_action(event)
            elif validate_email(event['message']['text']):
                user = User.query.filter_by(id=recipient_id).first()
                user.email = event['message']['text']
                db.session().commit()
                redis_store.delete(recipient_id)
                facebook_requests.post_text(recipient_id, constants.SUPPORT_REQUEST_NEW_EMAIL)
                redis_store.set(recipient_id, SessionStates.DEFINING_SUPPORT_REQUEST.value)
            else:
                facebook_requests.post_text(recipient_id, constants.INVALID_EMAIL)
        else:
            facebook_requests.post_text(recipient_id, constants.INVALID_EMAIL)
    # This state occurs when the user said they wanted to create a ticket, and they have no other
    # active/solved tickets in the database. In this case, we asked them to define what they wanted
    # support for. First, we need their email, so we ask for that if we didn't already have it, which is handled above.
    # Following, we ask for them to define their request, and create a ticket/add comments with these messages.
    # We also handle the edge case where the user presses a button while we're expecting text.
    elif user_state == SessionStates.DEFINING_SUPPORT_REQUEST.value:
        zendesk_requests.create_ticket_helper(event, user)
        redis_store.delete(recipient_id)
    # This state occurs when the user said they wanted to add a comment to their recently solved ticket.
    # If they have more than one solved ticket we raise an exception as this is an unexpected state.
    # We then add a comment to the solved ticket and reopen the ticket.
    elif user_state == SessionStates.ADDING_COMMENT_TO_TICKET.value:
        solved_tickets = user.get_solved_tickets()
        if len(solved_tickets) > 1:
            raise ValueError("User has more than one 'solved' ticket - unsure which ticket to reopen.")
        ticket = solved_tickets[0]
        # Re-open the Zendesk ticket and add the comment
        zendesk_requests.reopen_ticket(ticket.id)
        zendesk_requests.verify_user_helper(user.zendesk_id)
        zendesk_requests.add_comment_helper(recipient_id, ticket.id, event)
        redis_store.delete(recipient_id)
    # Finally, handle the general state of the user having tickets attached to them.
    elif user.tickets:
        open_tickets = user.get_open_tickets()
        solved_tickets = user.get_solved_tickets()
        # Having more than one open or one solved ticket is an invalid state
        if len(open_tickets) > 1 or len(solved_tickets) > 1:
            raise ValueError("User has more than one 'open' or 'solved' ticket - unsure which ticket to target.")
        # If the user has an open ticket, we simply assume they're adding a comment to their ticket
        if open_tickets:
            zendesk_requests.verify_user_helper(user.zendesk_id)
            zendesk_requests.add_comment_helper(recipient_id, open_tickets[0].id, event)
        # If the user has a solved ticket we ask them which actions they'd like to take (add to, create new, learn)
        elif solved_tickets:
            facebook_actions.recent_ticket_question_action(event)
        else:
            raise AttributeError("User has tickets, but they're neither solved nor open - invalid state")
    else:
        # If none of these states evaluated to true, the user is not currently involved with support at all.
        # We retrieve their name if it doesn't exist, then return True to continue onto the normal flow.
        if not user.first_name or not user.last_name:
            facebook_requests.populate_user_info(user)
        return True
    return False


def handle_text_message(event):
    """
    Handles a general text message sent by the user - runs NLP to try to interpret the text.
    :param event: JSON containing information about the interaction.
    """
    event['message']['text'] = event['message']['text'].encode('utf-8')
    resp = wit_requests.get_intent(event['message']['text'])
    try:
        wit_actions.run_actions(event, resp)
    except (KeyError, IndexError, TypeError):
        bot_log("Failed to interpret user message: %s" % event['message']['text'])
        wit_actions.handle_failed_interpretation(event)
