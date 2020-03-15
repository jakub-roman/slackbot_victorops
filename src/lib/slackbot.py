import re
import logging
from slack import WebClient
from slackeventsapi import SlackEventAdapter

class Slackbot:

	def __init__(self, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET):
		# Login to slack
		self.adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/")
		self.client = WebClient(token=SLACK_BOT_TOKEN)
		# Listen for events
		# -> this is alternative for decorators
		self.adapter.on("app_mention", self.handle_mention)
		self.log = logging.getLogger(__name__)

	def run(self, port=8080, host='127.0.0.1'):
		self.adapter.start(port=port, host=host)

	def print_message(self, message, channel):
		self.client.chat_postMessage(
	        channel=channel,
	        text=message
	    )

	def not_found(self, cmd):
		return("I don't know this command: '%s', try 'help'" % cmd)

	def process_message(self, message, channel):
		for cmd in COMMANDS:
			if ( cmd == message ):
				self.print_message(
					COMMANDS[cmd]['func'](), # generate the output from function ref
					channel
				)
				return
		# in case we don't know this command
		self.print_message(self.not_found(message), channel)

	def handle_mention(self, payload):
		event = payload.get('event', {})
		self.log.debug("Got mention: %s" % event)
		m = re.match('<@\w+>\s(.*)', event.get('text'))
		self.process_message(m.group(1), event.get('channel'))

	@staticmethod
	def get_oncall():
		return("This is oncall!")

	@staticmethod
	def get_help():
		message=[ "I know following commands:" ]
		for cmd in COMMANDS:
			message.append('- %s: %s' % (cmd, COMMANDS[cmd]['help']))

		return("\n".join(message))

# Commands that a SlackBot knows
COMMANDS = {
	'oncall': { 'help': 'get oncall schedule', 'func': Slackbot.get_oncall },
	'help': { 'help': 'show this help', 'func': Slackbot.get_help }
}
