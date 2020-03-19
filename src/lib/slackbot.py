import os
import re
import logging
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from .victorops import VictorOps
from .commands import oncall

class Slackbot:

	def __init__(self, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, config):
		# configuration
		self.log = logging.getLogger(__name__)
		self.config = config
		self.victorops = VictorOps(
			os.getenv('VICTOROPS_API_ID',''),
			os.getenv('VICTOROPS_API_KEY','')
		)
		# Login to slack
		self.adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/")
		self.client = WebClient(token=SLACK_BOT_TOKEN)
		# Listen for events
		# -> this is alternative for decorators
		self.adapter.on("app_mention", self.handle_mention)

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
		# command can have sub-commands
		# so let's split it on spaces
		commands = re.split('\s+', message)
		c = commands.pop(0) # get first command
		for cmd in COMMANDS:
			if ( cmd == c ):
				self.print_message(
					# generate the output from function ref
					COMMANDS[cmd]['func'](
						# inject victorops object
						self.victorops,
						# send the configuration for this command
						# (only if the configuration exist)
						self.config[cmd] if cmd in self.config else {},
						# send sub-command(s)
						commands
					),
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
	def help(a, b, c):
		message=[ "I know following commands:" ]
		for cmd in COMMANDS:
			message.append('- %s: %s' % (cmd, COMMANDS[cmd]['help']))

		return("\n".join(message))

# Commands that this SlackBot knows
COMMANDS = {
	'oncall': { 'help': 'find information about oncalls', 'func': oncall.dispatch },
	'help': { 'help': 'show this help', 'func': Slackbot.help }
}
