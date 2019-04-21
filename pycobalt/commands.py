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

def register(name, callback):
    """
    Register a command

    :param name: Name of command
    :param callback: Callback for command
    """

    def command_callback(*args):
        # check arguments
        if not utils.check_args(callback, args):
            syntax = '{} {}'.format(name, utils.signature_command(callback))
            engine.error("Syntax: " + syntax)
            return

        engine.debug('calling callback for command {}'.format(name))
        callback(*args)

    callbacks.register(command_callback, prefix='command_{}'.format(name))
    aggressor.command(name, command_callback)

class command:
    """
    Decorator for command registration
    """

    def __init__(self, name):
        """
        :param name: Name of command
        """

        self.name = name

    def __call__(self, func):
        self.func = func
        register(self.name, self.func)
