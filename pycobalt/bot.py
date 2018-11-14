"""
For creating Event Log bots

Example:

    import pycobalt.bot as bot
    import pycobalt.engine as engine

    bot.set_prefix('!')
    bot.set_triggers(bot.PRIVMSG, bot.PREFIX, bot.ADDRESSED)
    bot.add_help()

    @bot.command('test-command', 'Tests bot')
    def _(*args):
        for arg in args:
            aggressor.say('- {}'.format(arg))

    engine.loop()

Using the example:

    event> !help test-command
    10/19 10:21:01 <bot> test-command: Tests bot
    10/19 10:21:01 <bot> Syntax: test-command(*args)

    event> !test-command arg1 "arg 2" arg3
    10/19 10:24:13 <bot> arg1
    10/19 10:24:13 <bot> arg 2
    10/19 10:24:13 <bot> arg3
"""

import re
import shlex
import textwrap

import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.engine as engine
import pycobalt.utils as utils
import pycobalt.events as events

PRIVMSG = 'privmsg'
PREFIX = 'prefix'
ADDRESSED = 'addressed'

_prefix = '!'
_triggers = [PRIVMSG, PREFIX, ADDRESSED]
# {name: callback}
_command_callbacks = {}
# {name: help}
_command_help = {}

def say(text):
    """
    Post to Event Log

    :param text: Text to post
    """

    aggressor.say(text)

def error(text):
    """
    Post error message to Event Log

    :param text: Error to post
    """

    say('[-] ' + text)

def good(text):
    """
    Post good message to Event Log

    :param text: Message to post
    """

    say('[+] ' + text)

def info(text):
    """
    Post info message to Event Log

    :param text: Message to post
    """

    say('[*] ' + text)

def set_prefix(prefix):
    """
    Set the prefix to use with the PREFIX trigger

    :param prefix: Prefix to use
    """

    global _prefix
    _prefix = prefix

def set_triggers(*triggers):
    """
    Set bot triggers

    Options are:
     - bot.PRIVMSG: Allow commands through privmsgs
     - bot.PREFIX: Allow commands with prefix
     - bot.ADDRESSED: Allow commands when addressed by nick

    :param *triggers: Triggers to use.
    """

    global _triggers

    # check triggers
    for trigger in triggers:
        if trigger not in [PRIVMSG, PREFIX, ADDRESSED]:
            raise RuntimeError('unrecognized trigger: {}'.format(trigger))

    _triggers = triggers

def add_help():
    """
    Register the help command
    """

    def help_callback(command=None):
        global _command_help
        global _command_callbacks

        if command and command in _command_help:
            callback = _command_callbacks[command]
            syntax = '{}{}'.format(command, utils.signature(callback))
            out = textwrap.dedent("""\
                Help info for {command}:
                {command}: {help}
                Syntax: {command}{syntax}".format(command, syntax))
                """.format(command=command, help=_command_help[command], syntax=syntax))
            aggressor.say(out)
        else:
            out = 'Commands:'
            for command in _command_callbacks:
                if command in _command_help:
                    help = _command_help[command].splitlines()[0]
                    out += '\n - {}: {}'.format(command, help)
                else:
                    out += '\n - {}'.format(command)
            aggressor.say(out)

    register('help', help_callback, 'Show help')

def _handle_message(content):
    """
    Handle a bot message
    """

    global _command_callbacks

    parts = shlex.split(content)

    if not parts:
        # empty
        return

    command = parts[0]
    args = parts[1:]

    if command in _command_callbacks:
        # call the callback
        callback = _command_callbacks[command]
        if utils.check_args(callback, args):
            callback(*args)
        else:
            # bad arguments
            syntax = '{}{}'.format(command, utils.signature(callback))
            aggressor.say("Bad arguments. Syntax: {}".format(command, syntax))
    else:
        # unrecognized
        aggressor.say('Unrecognized command: ' + command)

# Event handler for PREFIX and ADDRESSED
@events.event('event_public')
def _(source, content, time):
    global _triggers
    global _prefix

    # prefixed command?
    if PREFIX in _triggers and _prefix and content.startswith(_prefix):
        _handle_message(content[len(_prefix):])

    # addressed command?
    m = re.match('^{}[:,]\s+(.*)'.format(aggressor.mynick()), content)
    if ADDRESSED in _triggers and m:
        _handle_message(m.group(1))

# Event handler for PRIVMSG
@events.event('event_private')
def _(source, dest, content, time):
    global _triggers

    # privmsg command?
    if PRIVMSG in _triggers and dest == aggressor.mynick():
        _handle_message(content)

def register(name, callback, help=None):
    """
    Register a command

    :param name: Name of the command
    :param callback: Callback
    :param help: Help info
    """

    global _command_callbacks

    _command_callbacks[name] = callback

    if help:
        _command_help[name] = help

def remove(command):
    """
    Remove a command

    :param command: Command to remove
    """

    if command in _command_callbacks:
        del _command_callbacks[command]
    if command in _command_help:
        del _command_help[command]

class command:
    """
    Decorator for bot command registration
    """

    def __init__(self, name, help=None):
        """
        :param name: Name of the command
        :param help: Help info
        """

        self.name = name
        self.help = help

    def __call__(self, func):
        self.func = func
        register(self.name, self.func,
                 help=self.help)
