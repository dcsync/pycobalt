"""
Helper functions for printing to the Beacon Console and Script Console. This
includes:

  - Modifying the Beacon Console output with Aggressor's undocumented `set
    BEACON_OUTPUT` blocks.
  - Helper functions for coloring and styling text.
  - Helper functions for creating ASCII tables and aligned text in the console.

Changing Beacon Console output (regular example):

    def beacon_output(bid, contents):
        return '<output>\n{}\n</output>'.format(contents)
    console.register('beacon_output', beacon_output)

Changing Beacon Console output (decorator example):

    @console.modifier('beacon_output')
    def beacon_output(bid, contents):
        return '<output>\n{}\n</output>'.format(contents)

Printing colored text to the Script Console:
    
    engine.message(console.red('red text'));

I'm sort of color blind so orange might be red and cyan might be blue. To see
all of Cobalt Strike's color options run this in the Script Console:

    e for ($i = 0; $i < 100; $i++) { println($i . "    \x03" . chr($i) . "test"); }

I've attempted to document the arguments to various output modifiers below.
This documentation is mostly based on Cobalt Strike's
[`default.cna`](https://www.cobaltstrike.com/aggressor-script/default.cna).

Event Log messages
 - `EVENT_PUBLIC`: from, text, when
 - `EVENT_PRIVATE`: from, to, text, when
 - `EVENT_ACTION`: from, text, when
 - `EVENT_JOIN`: from, when
 - `EVENT_QUIT`: from, when
 - `EVENT_NOTIFY`: text, when
 - `EVENT_NEWSITE`: from, text, when
 - `EVENT_NOUSER`: to, when
 - `EVENT_BEACON_INITIAL`: from, when
 - `EVENT_SSH_INITIAL`: from, when
 - `EVENT_USERS`: users
 - `EVENT_SBAR_LEFT`: <no arguments?>
 - `EVENT_SBAR_RIGHT`: lag

Web Log
 - `WEB_HIT`: method, uri, addr, ua, response, size, handler, when

Profiler
 - `PROFILER_HIT`: <five unknown arguments>

Keystrokes
 - `KEYLOGGER_HIT`: <four unknown arguments>

Beacon Console
 - `BEACON_SBAR_LEFT`: bid, metadata
 - `BEACON_SBAR_RIGHT`: bid, metadata
 - `BEACON_CHECKIN`: bid, message
 - `BEACON_ERROR`: bid, message
 - `BEACON_TASKED`: bid, message
 - `BEACON_OUTPUT`: bid, message
 - `BEACON_OUTPUT_ALT`: bid, message
 - `BEACON_OUTPUT_PS`: bid, output (see `helpers.parse_ps`)
 - `BEACON_OUTPUT_LS`: bid, output (see `helpers.parse_ls`)
 - `BEACON_OUTPUT_JOBS`: bid, output (see `helpers.parse_jobs`)
 - `BEACON_OUTPUT_DOWNLOADS`: bid, downloads={'name', 'path', 'size', 'rcvd'}
 - `BEACON_OUTPUT_EXPLOITS`: <no arguments?>
 - `BEACON_OUTPUT_HELP`: <no arguments?>
 - `BEACON_OUTPUT_HELP_COMMAND`: command
 - `BEACON_MODE`: bid?, output
 - `BEACON_INPUT`: bid, user, text, when

Phishing
 - `SENDMAIL_START`: unknown, ntarget, attachment, bounceto, server, subject, templatef, url
 - `SENDMAIL_PRE`: unknown, dest
 - `SENDMAIL_POST`: cid, email, status, message
 - `SENDMAIL_DONE`: <no arguments?>

SSH Beacon Console
 - `SSH_OUTPUT_HELP`: <no arguments?>
 - `SSH_OUTPUT_HELP_COMMAND`: command
 - `SSH_SBAR_LEFT`: bid, metadata
 - `SSH_SBAR_RIGHT`: bid, metadata
 - `SSH_CHECKIN`: bid, message
 - `SSH_ERROR`: bid, message
 - `SSH_TASKED`: bid, message
 - `SSH_OUTPUT`: bid, message
 - `SSH_OUTPUT_ALT`: bid, message
 - `SSH_OUTPUT_DOWNLOADS`: bid, downloads={'name', 'path', 'size', 'rcvd'}
 - `SSH_INPUT`: bid, user, text, when
"""

import math
import collections

import pycobalt.utils as utils
import pycobalt.engine as engine
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks

_known_modifiers = (
    'EVENT_PUBLIC',
    'EVENT_PRIVATE',
    'EVENT_ACTION',
    'EVENT_JOIN',
    'EVENT_QUIT',
    'EVENT_NOTIFY',
    'EVENT_NEWSITE',
    'EVENT_NOUSER',
    'EVENT_BEACON_INITIAL',
    'EVENT_SSH_INITIAL',
    'EVENT_USERS',
    'EVENT_SBAR_LEFT',
    'EVENT_SBAR_RIGHT',
    'WEB_HIT',
    'PROFILER_HIT',
    'KEYLOGGER_HIT',
    'BEACON_SBAR_LEFT',
    'BEACON_SBAR_RIGHT',
    'BEACON_CHECKIN',
    'BEACON_ERROR',
    'BEACON_TASKED',
    'BEACON_OUTPUT',
    'BEACON_OUTPUT_ALT',
    'BEACON_OUTPUT_PS',
    'BEACON_OUTPUT_LS',
    'BEACON_OUTPUT_JOBS',
    'BEACON_OUTPUT_DOWNLOADS',
    'BEACON_OUTPUT_EXPLOITS',
    'BEACON_OUTPUT_HELP',
    'BEACON_OUTPUT_HELP_COMMAND',
    'BEACON_MODE',
    'BEACON_INPUT',
    'SENDMAIL_START',
    'SENDMAIL_PRE',
    'SENDMAIL_POST',
    'SENDMAIL_DONE',
    'SSH_OUTPUT_HELP',
    'SSH_OUTPUT_HELP_COMMAND',
    'SSH_SBAR_LEFT',
    'SSH_SBAR_RIGHT',
    'SSH_CHECKIN',
    'SSH_ERROR',
    'SSH_TASKED',
    'SSH_OUTPUT',
    'SSH_OUTPUT_ALT',
    'SSH_OUTPUT_DOWNLOADS',
    'SSH_INPUT',
)

def is_known(name):
    """
    Check if a modifier is one of the known cobaltstrike ones

    :param name: Name of modifier
    :return: True if modifier is a known one
    """

    global _known_modifiers
    return name.upper() in _known_modifiers

def register(name, callback, known_only=True):
    """
    Register an modifier callback.

    :param name: Name of modifier (case-insensitive)
    :param callback: Modifier callback
    :param known_only: Only allow known modifiers
    :return: Name of registered callback
    """

    name = name.upper()

    def modifier_callback(*args):
        #engine.debug('calling callback for modifier {}'.format(name))
        try:
            return callback(*args)
        except Exception as exc:
            engine.handle_exception_softly(exc)
            return '[!] An Exception occurred in the {} output modifier. See Script Console for more details.'.format(name)

    if known_only and not is_known(name):
        raise RuntimeError('Tried to register an unknown modifier: {name}. Try console.modifier("{name}", known_only=False).'.format(name=name))

    callback_name = callbacks.register(modifier_callback, prefix='modifier_{}'.format(name))
    engine.write('set', {'name': name, 'callback': modifier_callback})

    return callback_name

def unregister(callback):
    """
    Unregister a modifier callback. There's no way to easily unregister a callback in
    Aggressor so this will forever leave us with broken callbacks coming back
    from the teamserver.

    :param callback: Callback to unregister
    :return: Name of unregistered callback
    """

    return callbacks.unregister(callback)

class modifier:
    """
    Decorator for output modifier registration
    """

    def __init__(self, name, known_only=True):
        """
        :param name: Name of modifier
        :param known_only: Only allow known modifiers
        """

        self.name = name
        self.known_only = known_only

    def __call__(self, func):
        self.func = func
        register(self.name, self.func, known_only=self.known_only)

# Color and formatting stuff follows
_escape = chr(3)

"""
Color escape codes. Feel free to use these directly instead of the helper
functions.
"""
codes = {
    'bold': _escape + chr(2),
    'underline': _escape + chr(31),
    'white': _escape + chr(48),
    'black': _escape + chr(49),
    'blue': _escape + chr(50),
    'green': _escape + chr(51),
    'orange_red': _escape + chr(52),
    'red': _escape + chr(53),
    'purple': _escape + chr(54),
    'orange': _escape + chr(55),
    'yellow': _escape + chr(56),
    'bright_green': _escape + chr(57),
    'blue_green': _escape + chr(65),
    'cyan': _escape + chr(66),
    'light_purple': _escape + chr(67),
    'pink': _escape + chr(68),
    'grey': _escape + chr(69) ,
    'reset': chr(15),
}

def stripped_length(string):
    """
    Get the length of a string without control codes

    :param string: String
    :return: Length of string minus control codes
    """

    return len(strip(string))

def justify(string, total, side='left', fill=' '):
    """
    Justify a string for the console

    :param string: String to justify
    :param total: Total size to justify to
    :param side: Side to justify to (center, left, or right)
    :param fill: Character to fill with
    :return: Justified string
    """

    length = stripped_length(string)
    diff = total - length

    if diff <= 0:
        return string
    elif side == 'left':
        return string + fill * diff
    elif side == 'right':
        return fill * diff + string
    elif side == 'center':
        return fill * math.floor(diff / 2) + string + fill * math.ceil(diff / 2)
    else:
        raise RuntimeError('Invalid justify side: {}'.format(side))

def table(items, keys=None, show_headers=True):
    """
    Make a pretty ASCII table

    :param items: Items to make a table for (list of dictionaries)
    :param keys: Either a list of dictionary keys or a dictionary containing `{key: pretty_header}`
    :param show_headers: Show the table headers (default: True)
    :return: Pretty ASCII table
    """

    if not keys:
        # default: use all keys
        keys = set()
        for item in items:
            keys |= set(item.keys())
        keys = sorted(keys)

    sizes = {}

    # get max sizes
    for key in keys:
        # header size
        if show_headers:
            if isinstance(keys, dict):
                max_size = stripped_length(keys[key])
            else:
                max_size = stripped_length(key)
        else:
            max_size = 0

        # max size of key within each item
        for item in items:
            if key in item:
                size = stripped_length(str(item[key]))
                if size > max_size:
                    max_size = size
        sizes[key] = max_size

    output = ''

    if show_headers:
        # print header
        for key in keys:
            size = sizes[key] 

            if isinstance(keys, dict):
                header = keys[key]
            else:
                header = key

            output += '| {} '.format(justify(header, size, side='center'))
        output += '|\n'

        # print header line
        for key in keys:
            size = sizes[key] 
            output += '+' + '-' * (size + 2)
        output += '+\n'

    # print items
    for item in items:
        for key in keys:
            size = sizes[key] 

            if key in item:
                value = item[key]
            else:
                value = ''

            if isinstance(value, int):
                # justify numbers to the right
                side = 'right'
            else:
                # justify strings to the left
                side = 'left'

            output += '| {} '.format(justify(str(value), size, side=side))
        output += '|\n'

    return output


def strip(text):
    """
    Strip control codes from a string.

    :param text: String to strip
    :return: Stripped string
    """

    for code in codes.values():
        text = text.replace(code, '')

    return text

def bold(text):
    """
    Style text bold for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['bold'] + text + codes['reset']

def underline(text):
    """
    Style text underlined for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['underline'] + text + codes['reset']

def white(text):
    """
    Style text white for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['white'] + text + codes['reset']

def black(text):
    """
    Style text black for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['black'] + text + codes['reset']

def blue(text):
    """
    Style text blue for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['blue'] + text + codes['reset']

def green(text):
    """
    Style text green for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['green'] + text + codes['reset']

def orange_red(text):
    """
    Style text orange-red for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['orange_red'] + text + codes['reset']

def red(text):
    """
    Style text red for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['red'] + text + codes['reset']

def purple(text):
    """
    Style text purple for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['purple'] + text + codes['reset']

def orange(text):
    """
    Style text orange for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['orange'] + text + codes['reset']

def yellow(text):
    """
    Style text yellow for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['yellow'] + text + codes['reset']

def bright_green(text):
    """
    Style text bright-green for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['bright_green'] + text + codes['reset']

def blue_green(text):
    """
    Style text blue-green for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['blue_green'] + text + codes['reset']

def cyan(text):
    """
    Style text cyan for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['cyan'] + text + codes['reset']

def light_purple(text):
    """
    Style text light-purple for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['light_purple'] + text + codes['reset']

def pink(text):
    """
    Style text pink for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['pink'] + text + codes['reset']

def grey(text):
    """
    Style text grey for the Script Console and Beacon Console.

    :param text: Text to style
    :return: Styled text
    """

    return codes['grey'] + text + codes['reset']
