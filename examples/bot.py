#!/usr/bin/env python3

import sys
import utils
sys.path.insert(0, utils.basedir('pycobalt'))

import textwrap
import threading

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.commands as commands
import pycobalt.aliases as aliases
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.helpers as helpers
import pycobalt.bot as bot

# bot config
bot.set_prefix('!')
bot.set_triggers(bot.PRIVMSG, bot.PREFIX, bot.ADDRESSED)
bot.add_help()

# [{bid?, user?, computer?, command}]
_triggers = []

def _run_command(bid, command):
    """
    Run a command
    """

    alias = command[0]
    args = ' '.join(command[1:])

    aggressor.fireAlias(bid, alias, args)

def _conditionally_run(bid, trigger):
    """
    Run a trigger if the conditions match

    :param bid: Bid to run on
    :param trigger: Trigger to match
    :return: Whether or not command was run
    """

    user = aggressor.beacon_info(bid, 'user')
    computer = aggressor.beacon_info(bid, 'computer')

    if 'all' in trigger and trigger['all'] or \
       'bid' in trigger and bid == trigger['bid'] or \
       'user' in trigger and user == trigger['user'] or \
       'computer' in trigger and computer == trigger['computer']:
        engine.debug('running command: ' + str(trigger['command']))
        _run_command(bid, trigger['command'])
        return True
    else:
        return False

# XXX broken because message handling isn't thread safe yet
class TriggerTimer(threading.Thread):
    def __init__(self, trigger):
        super().__init__()
        self.stop_event = threading.Event()
        self.trigger = trigger

    def run(self):
        time = self.trigger['time']
        engine.debug('thread running {}'.format(time))

        while not self.stop_event.wait(time):
            engine.debug('conditional timer trigger')
            for bid in aggressor.beacon_ids():
                _conditionally_run(bid, self.trigger)

    def stop(self):
        self.stop_event.set()

@events.event('beacon_initial')
def _(bid):
    global _triggers

    for trigger in _triggers:
        if trigger['type'] == 'initial':
            _conditionally_run(bid, trigger)

@events.event('beacon_output')
def _(bid, text, when):
    global _triggers

    user = aggressor.beacon_info(bid, 'user')
    computer = aggressor.beacon_info(bid, 'computer')

    for trigger in _triggers:
        if trigger['type'] == 'output':
            _conditionally_run(bid, trigger)

@bot.command('auto', 'Run beacon commands on triggers. See `auto -h`.')
def _(*args):
    global _triggers

    parser = helpers.ArgumentParser(prog='auto', event_log=True)
    parser.add_argument('-b', '--bid', action='append', type=int, help='Bid to trigger on')
    parser.add_argument('-u', '--user', action='append', help='User to trigger on')
    parser.add_argument('-c', '--computer', action='append', help='Computer to trigger on')
    parser.add_argument('-a', '--all', action='store_true', help='Trigger on all beacons')
    parser.add_argument('-i', '--initial', action='store_true', help='Trigger on initial beacon (default for --user and --computer)')
    parser.add_argument('-o', '--output', action='store_true', help='Trigger on beacon output (default for --bid)')
    #parser.add_argument('-t', '--timed', metavar='SECONDS', type=int, help='Trigger every X seconds')
    parser.add_argument('-r', '--remove', type=int, help='Remove a trigger')
    parser.add_argument('-l', '--list', action='store_true', help='List triggers')
    parser.add_argument('command', nargs='*', help='Command to run')
    try: args = parser.parse_args(args)
    except: return

    # -r/--remove
    if args.remove:
        if args.remove < len(_triggers) and args.remove >= 0:
            trigger = _triggers[args.remove]
            if trigger['type'] == timed:
                trigger['timer'].stop()
            del _triggers[args.remove]
            bot.say('Removed trigger {}'.format(args.remove))
        else:
            bot.error('Trigger {} does not exist'.format(args.remove))
    # -l/--list
    elif args.list:
        output = 'Triggers:\n'
        for num, trigger in enumerate(_triggers):
            output += '{}: {}\n'.format(num, str(trigger))
        bot.say(output)
    else:
        if not (args.bid or args.user or args.computer or args.all):
            bot.error('Specify --bid, --user, --computer, or --all')
            return

        if not args.command:
            bot.error('Specify command')
            return

        trigger = {}
        trigger['command'] = args.command
        if args.bid:
            trigger['bids'] = args.bid
        if args.user:
            trigger['users'] = args.user
        if args.computer:
            trigger['computers'] = args.computer
        if args.all:
            trigger['all'] = True

        # -o/--output
        if args.output:
            # on output
            trigger['type'] = 'output'
        # -t/--timed
        elif args.timed:
            # timed
            trigger['type'] = 'timed'
            trigger['time'] = args.timed
            trigger['timer'] = TriggerTimer(trigger)
            trigger['timer'].start()
        else:
            # on initial
            trigger['type'] = 'initial'

        _triggers.append(trigger)
        engine.debug('Adding trigger: {}'.format(str(trigger)))
        bot.good('Added trigger')

engine.enable_debug()
engine.loop()
