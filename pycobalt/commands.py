"""
For registering script console commands

Regular example:

    def test_command(args):
        print(args)
    commandes.register('test_command', test_command)

Decorator example:

    @commands.command('test_command')
    def test_command(args):
        print(args)
"""

import pycobalt.engine as engine
import pycobalt.utils as utils
import pycobalt.callbacks as callbacks
import pycobalt.aggressor as aggressor

def register(name, callback, quote_replacement=None):
    """
    Register a command

    Regarding the `quote_replacement` argument: Cobalt Strike's Script Console
    uses double quotes to enclose arguments with spaces in them. There's no way
    to escape double quotes within those quotes though. Set `quote_replacement`
    to a string and PyCobalt will replace it with " in each argument.

    :param name: Name of command
    :param callback: Callback for command
    :param quote_replacement: Replace this string with " in each
                              argument.
    """

    def command_callback(*args):
        # check arguments
        if not utils.check_args(callback, args):
            syntax = '{} {}'.format(name, utils.signature_command(callback))
            engine.error("Syntax: " + syntax)
            return

        # handle the quote replacement character
        if quote_replacement:
            args = [arg.replace(quote_replacement, '"') for arg in args]

        engine.debug('calling callback for command {}'.format(name))
        callback(*args)

    callbacks.register(command_callback, prefix='command_{}'.format(name))
    aggressor.command(name, command_callback)

class command:
    """
    Decorator for command registration
    """

    def __init__(self, name, quote_replacement=None):
        """
        :param name: Name of command
        :param quote_replacement: Replace this string with " in each
                                  argument (see notes in the `register()`
                                  function)
        """

        self.name = name
        self.quote_replacement = quote_replacement

    def __call__(self, func):
        self.func = func
        register(self.name, self.func, self.quote_replacement)
