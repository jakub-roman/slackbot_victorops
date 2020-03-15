import os
import logging
from lib.slackbot import Slackbot

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    s = Slackbot(
        os.getenv('SLACK_BOT_TOKEN', ''),
        os.getenv('SLACK_SIGNING_SECRET', '')
    )
    s.run(port=8080, host='0.0.0.0')
