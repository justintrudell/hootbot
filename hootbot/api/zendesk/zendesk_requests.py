import requests
import copy
import json

import config
from hootbot.helpers import endpoint_helpers
from hootbot.logging.logger import bot_log
from hootbot.json.zendesk import zendesk_encodings
from hootbot.database.database import db
from hootbot.models.dao.zendesk_ticket import ZendeskTicket
from hootbot.models.dao.user import User
from hootbot.models.enums.zendesk_status import ZendeskStatus


def post_ticket(data):
    """
    Creates a ticket.
    :param data: JSON data to be sent to the Zendesk API.
    :return JSON of reply on success
    """
    r = requests.post("https://%s.zendesk.com/api/v2/tickets.json" % config.ZENDESK_SUBDOMAIN,
                      data=json.dumps(data),
                      headers={
                          "Content-type": "application/json"
                      },
                      auth=("%s/token" % config.ZENDESK_EMAIL_ADDRESS, config.ZENDESK_ACCESS_TOKEN))
    if r.status_code != requests.codes.created:
        bot_log(r.text)
    else:
        return r.json()


def update_ticket(ticket_id, data):
    """
    Updates an existing Zendesk ticket.
    :param ticket_id: The ID of the ticket to be updated.
    :param data: JSON data to update the ticket with.
    """
    r = requests.put("https://%s.zendesk.com/api/v2/tickets/%s.json" % (config.ZENDESK_SUBDOMAIN, ticket_id),
                     data=json.dumps(data),
                     headers={
                          "Content-type": "application/json"
                     },
                     auth=("%s/token" % config.ZENDESK_EMAIL_ADDRESS, config.ZENDESK_ACCESS_TOKEN))
    if r.status_code != requests.codes.ok:
        bot_log(r.text)
    else:
        return r.json()


def update_user(user_id, data):
    """
    Updates an existing Zendesk user.
    :param user_id: The Facebook ID of the user.
    :param data: The JSON data to update the user with/
    """
    r = requests.put("https://%s.zendesk.com/api/v2/users/%s.json" % (config.ZENDESK_SUBDOMAIN, user_id),
                     data=json.dumps(data),
                     headers={
                          "Content-type": "application/json"
                     },
                     auth=("%s/token" % config.ZENDESK_EMAIL_ADDRESS, config.ZENDESK_ACCESS_TOKEN))
    if r.status_code != requests.codes.ok:
        bot_log(r.text)
    else:
        return r.json()


def add_ticket_comment(ticket_id, data, email):
    """
    Adds a comment to an existing Zendesk ticket, acting as an end user - leverages the ZD Requests API
    :param ticket_id: The ID of the ticket to be updated.
    :param data: The JSON data to update the ticket with.
    :param email: The email address of the requester (the end user updating the ticket)
    :return The JSON response
    """
    r = requests.put("https://%s.zendesk.com/api/v2/requests/%s.json" % (config.ZENDESK_SUBDOMAIN, ticket_id),
                     data=json.dumps(data),
                     headers={
                          "Content-type": "application/json"
                     },
                     auth=("%s/token" % email, config.ZENDESK_ACCESS_TOKEN))
    if r.status_code != requests.codes.ok:
        bot_log(r.text)
    else:
        return r.json()


def get_comments(ticket_id):
    """
    Gets all comments on an existing Zendesk ticket.
    :param ticket_id: The Zendesk ID of the ticket to be updated.
    :return: A list of comments with various parameters, defined here:
             https://developer.zendesk.com/rest_api/docs/core/ticket_comments#list-comments
    """
    r = requests.get("https://%s.zendesk.com/api/v2/tickets/%s/comments.json?sort_order=desc"
                     % (config.ZENDESK_SUBDOMAIN, ticket_id),
                     headers={
                         "Content-type": "application/json"
                     },
                     auth=("%s/token" % config.ZENDESK_EMAIL_ADDRESS, config.ZENDESK_ACCESS_TOKEN))
    if r.status_code != requests.codes.ok:
        bot_log(r.text)
    else:
        return r.json()


def create_ticket_helper(event, user):
    """
    Helper method that calls appropriate methods to create a Zendesk ticket from the given event and user objects.
    :param event: JSON containing information about the interaction.
    :param user: The User object corresponding to the Facebook User
    """
    data = copy.deepcopy(zendesk_encodings.ticket)
    image_attachment = endpoint_helpers.event_is_image(event)
    if image_attachment:
        data['ticket']['subject'] = "Image Attachment"
        data['ticket']['comment']['body'] = "Image: %s " % str(image_attachment)
    else:
        data['ticket']['subject'] = event['message']['text']
        data['ticket']['comment']['body'] = event['message']['text']
    data['ticket']['requester']['name'] = user.first_name + " " + user.last_name
    data['ticket']['requester']['email'] = user.email

    result_json = post_ticket(data)
    if result_json:
        zendesk_id = result_json['ticket']['requester_id']
        user.zendesk_id = zendesk_id
        ticket = ZendeskTicket(result_json['ticket']['id'], ZendeskStatus.OPEN.value, user.id)
        db.session().add(ticket)
        db.session().commit()


def reopen_ticket(ticket_id):
    """
    Helper method to reopen a solved Zendesk Ticket
    :param ticket_id: The Zendesk ID of the ticket to be reopened
    """
    data = copy.deepcopy(zendesk_encodings.ticket_status)
    data['ticket']['status'] = ZendeskStatus.OPEN.value
    resp = update_ticket(ticket_id, data)
    if resp:
        ZendeskTicket.query.filter_by(id=ticket_id).first().status = ZendeskStatus.OPEN.value
        db.session().commit()


def add_comment_helper(recipient_id, ticket_id, event):
    """
    Helper method to update a Zendesk ticket by adding a comment.
    :param recipient_id Facebook ID of the user
    :param ticket_id The Zendesk ID for the ticket
    :param event JSON event
    """
    data = copy.deepcopy(zendesk_encodings.update_ticket)
    image_attachment = endpoint_helpers.event_is_image(event)
    if image_attachment:
        data['request']['comment']['body'] = "Image: %s " % str(image_attachment)
    else:
        data['request']['comment']['body'] = event['message']['text']
    email = User.query.filter_by(id=recipient_id).first().email
    add_ticket_comment(ticket_id, data, email)


def verify_user_helper(zendesk_id):
    """
    Helper method to verify a Zendesk user.
    :param zendesk_id: The Zendesk ID of the user.
    """
    update_user(zendesk_id, zendesk_encodings.update_user)

