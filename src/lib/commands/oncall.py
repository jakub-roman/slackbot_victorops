import json
import logging
import dateutil.parser

def dispatch(victorops, config, arg):
    oncall = Oncall(victorops)
    if not arg:
        return help(1, 2, 3)
    command = arg.pop(0)
    for cmd in oncall.commands:
        if ( cmd == command ):
            return oncall.commands[cmd]['func'](
                config[cmd] if cmd in config else {},
                arg
            )

class Oncall:

    def __init__(self, victorops):
        # Sub-commands this module can handle
        self.commands = {
        	'shift': { 'help': 'get upcomming oncall people for given shift', 'func': self.shift },
        	'help': { 'help': 'show this help', 'func': self.help }
        }
        self.victorops = victorops
        self.log = logging.getLogger(__name__)

    def find_shift(self, config):
        team_oncall = None
        try:
            team_oncall = self.victorops.get_oncall_schedule(
                config['team'],
                config['daysForward'],
                config['step']
            )
        except Exception as e:
            self.log.error(e)
            return "Can't get shift data from VictorOps"

        self.log.debug("schedule: %s" % json.dumps(team_oncall, indent=2))

        users = []
        for schedules in team_oncall['schedules']:
            for schedule in schedules['schedule']:
                if schedule['shiftName'] == config['shift']:
                    for r in schedule['rolls']:
                        users.append("%s\t-\t%s" % (r['onCallUser']['username'], self.timerange(r['start'], r['end'])))
        if users:
            return "Users oncall for shift '%s' of team '%s' (next %s days): \n%s" % \
                (config['shift'], config['team'], config['daysForward'], "\n".join(users))
        else:
            return "No configuration for shift '%s' in team '%s'" % \
                (config['shift'], config['team'])

    def timerange(self, start, stop):
        begin = dateutil.parser.isoparse(start)
        end = dateutil.parser.isoparse(stop)
        if ( (begin.date()) == (end.date()) ):
            return "%s\t%s - %s" % \
                (begin.strftime('%Y-%m-%d') ,begin.strftime('%H:%M') ,end.strftime('%H-%M'))
        else:
            return "%s %s - %s %s" % \
                (begin.strftime('%Y-%m-%d'), begin.strftime('%H:%M'), end.strftime('%Y-%m-%d'), end.strftime('%H-%M'))

    def shift(self, config, shift_name):
        if not config:
            return "I need configuration of shifts to lookup! See the documentation."
        if not shift_name:
            return "I need shift name to look it up!"
        if shift_name[0] in config:
            return self.find_shift(config[shift_name[0]])
        else:
            return "Don't have configuration for '%s' in configuration" % shift_name[0]

    def help(self, a, b, c):
        message=[ "Command 'oncall', available sub-commands:" ]
        for cmd in COMMANDS:
            message.append('- %s: %s' % (cmd, COMMANDS[cmd]['help']))

        return("\n".join(message))
