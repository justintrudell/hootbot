max_three_button_list = {
    'recipient': {
        'id': ''
    },
    'message': {
        'attachment': {
            'type': 'template',
            'payload': {
                'template_type': 'button',
                'text': '',
                'buttons': [
                ]
            }
        }
    }
}

postback_button = {
    'type': 'postback',
    'title': '',
    'payload': ''
}

scrollable_button_list = {
    'recipient': {
        'id': ''
    },
    'message': {
        'attachment': {
            'type': 'template',
            'payload': {
                'template_type': 'generic',
                'elements': []
            }
        }
    }
}

scrollable_button_list_element = {
    'title': 'Swipe for more options',
    'buttons': []
}

"""
From the Facebook docs: Use the generic template to send a horizontal scrollable carousel of items, 
each composed of an image attachment, short description and buttons to request input from the user.
"""
generic_template = {
    'recipient': {
        'id': ''
    },
    'message': {
        'attachment': {
            'type': 'template',
            'payload': {
                'template_type': 'generic',
                'elements': [
                    {
                        'title': '',
                        'image_url': '',
                        'default_action': {
                            'type': 'web_url',
                            'url': '',
                            'messenger_extensions': True,
                            'webview_height_ratio': 'tall'
                        }

                    }
                ]
            }
        }
    }
}

url_list_template = {
    "recipient": {
        "id": ""
    },
    "message": {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                ]
            }
        }
    }
}

url_list_element = {
   "title": "",
   "subtitle": "",  # Optional parameter
   "image_url": "",  # Optional parameter
   "default_action": {
       "type": "web_url",
       "url": "",
       "messenger_extensions": "true",
       "webview_height_ratio": "full"
   }
}

image = {
    "recipient": {
        "id": ""
    },
    "message": {
       "attachment": {
            "type": "image",
            "payload": {
                "url": ""
            }
        }
    }
}

text = {
    "recipient": {
        "id": ""
    },
    "message": {
        "text": ""
    }
}

