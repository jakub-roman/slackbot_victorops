import os
import logging
import argparse
import yaml
from lib.slackbot import Slackbot

def parse_config(config):
    with open(config, 'r') as stream:
        return yaml.safe_load(stream)

def main(args):
    s = Slackbot(
        os.getenv('SLACK_BOT_TOKEN', ''),
        os.getenv('SLACK_SIGNING_SECRET', ''),
        parse_config(args.config)
    )
    s.run(port=8080, host='0.0.0.0')

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser(
        description="Generate buildkite pipeline steps to install addons."
    )
    parser.add_argument('--config', action="store", dest="config",
        help="Config file for this slackbot",
        default="%s/config.yaml" % os.path.dirname(__file__),
        metavar="FILE")
    args = parser.parse_args()

    main(args)
