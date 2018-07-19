import requests
import json
import copy  # Since we're storing the JSON as a dictionary we need to deepcopy it before using it

import config
from hootbot.logging.logger import bot_log
import hootbot.json.facebook.facebook_encodings as facebook_encodings
from hootbot.helpers.request_helpers import grouper
from hootbot.database.database import db


def post_data(data):
    """
    Posts JSON data to the Facebook messages API
    :param data: Data to be sent, as a dictionary
    """
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={
                          "access_token": config.FB_ACCESS_TOKEN
                      },
                      data=json.dumps(data),
                      headers={
                          "Content-type": "application/json"
                      })
    if r.status_code != requests.codes.ok:
        bot_log(r.text)


def post_text(recipient_id, text):
    """
    Sends a simple text message with 'text' as the string.
    :param recipient_id: ID of the anticipated receiver of this text message.
    :param text: The text to be sent to the user
    """
    data = copy.deepcopy(facebook_encodings.text)
    data['recipient']['id'] = recipient_id
    data['message']['text'] = text
    post_data(data)


def post_button_list(recipient_id, text, payload_header, tuples):
    """
    :param recipient_id: ID of the anticipated receiver of this list.
    :param text: General header text to send to the user along with the list of objectives.
    :param payload_header: Payload for every button that will be returned when they're tapped
    :param tuples: List of tuples (payload, title)
    """
    if len(tuples) <= 3:
        data = three_button_helper(recipient_id, payload_header.value, text, tuples)
    else:
        data = scrollable_list_helper(recipient_id, payload_header.value, tuples)
        post_text(recipient_id, text)
    post_data(data)


def post_image(recipient_id, url):
    """
    Helper method to post an image to the user, given a URL to that image
    :param recipient_id: ID of the receiver of the image.
    :param url: Image URL
    """
    data = copy.deepcopy(facebook_encodings.image)
    data['recipient']['id'] = recipient_id
    data['message']['attachment']['payload']['url'] = url
    post_data(data)


def post_generic_template(recipient_id, title, image_url, url):
    """
    Helper method to post Facebook's 'generic template'
    :param recipient_id: ID of the receiver of the template
    :param title: Title of the template
    :param image_url: URL for the image to be displayed alongside the template
    :param url: URL to navigate to when the template is tapped
    """
    data = copy.deepcopy(facebook_encodings.generic_template)
    data['recipient']['id'] = recipient_id
    element = data['message']['attachment']['payload']['elements'][0]
    element['title'] = title
    element['image_url'] = image_url
    element['default_action']['url'] = url
    data['message']['attachment']['payload']['elements'][0] = element
    post_data(data)


def post_url_list(recipient_id, url_list):
    """
    Helper method to post Facebook's 'list template'
    :param recipient_id: ID of the receiver of the list
    :param url_list: List of ArticleLink objects to send to the user.
    """
    data = copy.deepcopy(facebook_encodings.url_list_template)
    data['recipient']['id'] = recipient_id
    elements = []
    for url_obj in url_list:
        element = copy.deepcopy(facebook_encodings.url_list_element)
        element['title'] = url_obj.title
        if url_obj.description:
            element['subtitle'] = url_obj.description
        if url_obj.image_url:
            element['image_url'] = url_obj.image_url
        element['default_action']['url'] = url_obj.url
        elements.append(element)
    data['message']['attachment']['payload']['elements'] = elements
    post_data(data)


def get_user_info(facebook_id):
    """
    Retrieves user information from the Facebook API (currently first and last name)
    :param facebook_id: The FB Page ID of the user
    :return: JSON response from the FB API, containing first and last name on success
    """
    r = requests.get("https://graph.facebook.com/v2.6/%s" % facebook_id,
                     params={
                         "fields": "first_name,last_name",
                         "access_token": config.FB_ACCESS_TOKEN
                     },
                     headers={
                         "Content-type": "application/json"
                     })
    if r.status_code != requests.codes.ok:
        bot_log(r.text)
    return r.json()


def three_button_helper(recipient_id, payload_header, text, buttons):
    """
    Helper method to format a single button list, which has a max of three buttons
    :param recipient_id: ID of the receiver of the buttons
    :param payload_header: Payload to send back when a user taps on the button
    :param text: Text to send on top of the buttons.
    :param buttons: List of tuples (payload, title) to act as the buttons
    :return Formatted JSON
    """
    if len(buttons) > 3:
        raise ValueError("List of buttons greater than 3 provided.")
    data = copy.deepcopy(facebook_encodings.max_three_button_list)
    data['recipient']['id'] = recipient_id
    data['message']['attachment']['payload']['text'] = text
    buttons = build_button_list_buttons(payload_header, buttons)
    data['message']['attachment']['payload']['buttons'] = buttons
    return data


def scrollable_list_helper(recipient_id, payload_header, buttons):
    """
    Helper method to format a scrollable button list, which can have up to 30 buttons.
    :param recipient_id: ID of the receiver of the buttons
    :param payload_header: Payload to send back when a user taps on the button.
    :param buttons: List of tuples (payload, title) to act as the buttons
    :return Formatted JSON
    """
    if len(buttons) > 30:
        raise ValueError("List of buttons greater than 30 provided.")
    data = copy.deepcopy(facebook_encodings.scrollable_button_list)
    data['recipient']['id'] = recipient_id
    grouped_list = grouper(buttons, 3)
    for group in grouped_list:
        buttons = build_button_list_buttons(payload_header, group)
        element = copy.deepcopy(facebook_encodings.scrollable_button_list_element)
        element['buttons'] = buttons
        data['message']['attachment']['payload']['elements'].append(element)
    return data


def build_button_list_buttons(payload_header, tuples):
    """
    Helper method to build the individual buttons for the three button or scrollable list
    :param payload_header: Payload to send back when a user taps on the button.
    :param tuples: List of tuples (payload, title) to act as the buttons
    :return: Formatted list of JSON objects for the buttons
    """
    buttons = []
    for payload, title in tuples:
        button = copy.deepcopy(facebook_encodings.postback_button)
        button['title'] = title
        button['payload'] = "%s?=%s" % (payload_header, payload)
        buttons.append(button)
    return buttons


def populate_user_info(user):
    """
    Retrieves the user's first/last name from the API and populates their database entry.
    :param user: The user to retrieve the information for
    """
    fb_json = get_user_info(user.id)
    try:
        user.first_name = fb_json["first_name"]
        user.last_name = fb_json["last_name"]
        db.session().commit()
    except KeyError:
        bot_log("First/last name not properly returned from Facebook for FB ID " + user.id)
