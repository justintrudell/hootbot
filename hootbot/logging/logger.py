import logging

import config

logger = logging.getLogger('__main__')


def bot_log(message):
    if config.LOCATION == "deis":
        # Deis only logs things from stdout so we simply print when running on Deis
        print(message)
    else:
        logger.info(message)
