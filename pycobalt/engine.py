"""
For communication with cobaltstrike
"""

# TODO better argument checking on aggressor functions
# TODO handle 'set'

import json
import re
import sys
import traceback

import pycobalt.utils as utils
import pycobalt.events as events
import pycobalt.aggressor as aggressor
import pycobalt.commands as commands
import pycobalt.aliases as aliases
import pycobalt.callbacks as callbacks

_in_pipe = None
_out_pipe = None

_debug_on = False

def __init__():
    global _in_pipe
    global _out_pipe

    _in_pipe = sys.stdin
    _out_pipe = sys.stdout

    # since cobaltstrike can't read stderr
    sys.stderr = sys.stdout

def write(message_type, message=''):
    """
    Write a message to cobaltstrike. Message can be anything serializable by
    json.
    """

    global _out_pipe
    wrapper = {
                  'name': message_type,
                  'message': message,
              }
    _out_pipe.write(json.dumps(wrapper) + "\n")
    _out_pipe.flush()

def fix_dicts(old):
    """
    Fix for sleep's broken Java parameter marshalling
    """

    if not isinstance(old, dict):
        return old

    new = {}
    for key, item in old.items():
        # make new key
        m = re.match("'([^']+)'", key)
        if m:
            new_key = m.group(1)
        else:
            new_key = key

        if isinstance(item, list):
            # lists
            new_item = []
            for piece in item:
                new_item.append(fix_dicts(piece))
        elif isinstance(item, dict):
            # nested dicts
            new_item = fix_dicts(item)
        else:
            new_item = item
        new[new_key] = new_item
    return new

def handle_message(name, message):
    """
    Handle a received message according to its name
    """

    debug('handling message of type {}: {}'.format(name, message))
    if name == 'callback':
        # dispatch callback
        callback_name = message['name']
        callback_args = message['args'] if 'args' in message else []
        callbacks.call(callback_name, callback_args)
    elif name == 'eval':
        # eval python code
        eval(message)
    elif name == 'debug':
        # set debug mode
        if message is True:
            enable_debug()
        else:
            disable_debug()
    else:
        raise RuntimeError('received unhandled or out-of-order message type: {} {}'.format(name, str(message)))

_has_forked = False
def fork():
    """
    Tell cobaltstrike to fork
    """

    global _has_forked

    if _has_forked:
        raise RuntimeError('tried to fork cobaltstrike twice')

    write('fork')

def loop(fork_first=True):
    """
    Loop forever, handling messages
    """

    if fork_first:
        fork()

    reader = readiter()
    while True:
        try:
            name, message = next(reader)
            if name:
                handle_message(name, message)
            else:
                error('received invalid message: {}'.format(message))
        except StopIteration as e:
            break
        except Exception as e:
            error('exception: {}\n'.format(str(e)))
            error('traceback: {}'.format(traceback.format_exc()))

def stop():
    """
    Stop the script (just exits the process)
    """

    sys.exit()

def parse_line(line):
    """
    Parse an input line
    Format: {'name':<name>, 'message':<message>}
    """

    try:
        line = line.strip()
        wrapper = json.loads(line)
        wrapper = fix_dicts(wrapper)
        name = wrapper['name']
        if 'message' in wrapper:
            message = wrapper['message']
        else:
            message = None

        return name, message
    except Exception as e:
        return None, str(e)

def read():
    """
    Read a message line
    Returns: message name, submessage
    """

    global _in_pipe
    return parse_line(next(_in_pipe))

def readiter():
    """
    Read message lines
    Returns: iter({message name, submessage}, ...)
    """

    global _in_pipe
    for line in _in_pipe:
        yield parse_line(line)

def call(name, args, silent=False, fork=False, sync=True):
    """
    Call a sleep/aggressor function
    """

    # serialize and register function callbacks if needed
    if callbacks.has_callback(args):
        args = callbacks.serialized(args)

        # when there's a callback involved we usually have to fork because the
        # main script thread is busy reading from the script.
        debug('forcing fork for call to {}'.format(name))
        fork = True

    message = {
                'name': name,
                'args': args,
                'silent': silent,
                'fork': fork,
                'sync': sync,
              }
    write('call', message)

    if sync:
        # read and handle messages until we get our return value
        while True:
            name, message = read()
            if name == 'return':
                # got it
                return message
            else:
                handle_message(name, message)

def eval(code):
    """
    Eval aggressor code
    """

    write('eval', code)

def menu(menu_items):
    """
    Register a cobaltstrike menu
    """

    global _has_forked

    if _has_forked:
        raise RuntimeError('tried to register a menu after forking. this crashes cobaltstrike')

    menu_items = callbacks.serialized(menu_items)
    write('menu', menu_items)

def error(line):
    """
    Write error notice
    """

    write('error', line)

def message(line):
    """
    Write script console message
    """

    write('message', line)

def enable_debug():
    """
    Enable debug messages
    """

    global _debug_on
    _debug_on = True
    debug('enabled debug')

def disable_debug():
    """
    Disable debug messages
    """

    global _debug_on
    debug('disabling debug')
    _debug_on = False

def debug(line):
    """
    Write script console debug message
    """

    global _debug_on
    if _debug_on:
        write('debug', line)

__init__()
