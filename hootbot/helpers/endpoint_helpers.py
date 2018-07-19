import re

email_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


def validate_email(str):
    return email_pattern.match(str)


def event_is_image(event):
    """
    Checks if the event is an image, returns the URL if so, otherwise returns None
    :param event The JSON event
    :return: URL if even tis an image upload, otherwise None
    """
    if ('message' in event and 'attachments' in event['message']
        and event['message']['attachments'][0]['type'] == 'image'):
        return event['message']['attachments'][0]['payload']['url']
    return None
