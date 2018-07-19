import requests
from hootbot.logging.logger import bot_log
import config


def get_intent(message):
    """
    Provides text to Wit and retrieves the assumed intent after NLP
    :param message: Text message to send to Wit
    :return: Response JSON from the Wit API
    """
    payload = {
        "v": "20170510",  # Version number
        "q": message
    }
    r = requests.get("https://api.wit.ai/message",
                     headers={
                         "Authorization": "Bearer " + config.WIT_ACCESS_TOKEN
                     },
                     params=payload)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        bot_log(r.text)

