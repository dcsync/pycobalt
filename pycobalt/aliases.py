"""
For registering beacon console aliasess

Regular example:

    def test_alias(args):
        print(args)
    aliases.register('test_alias', test_alias)

Decorator example:

    @aliases.alias('test_alias')
    def test_alias(args):
        print(args)
"""

import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.engine as engine
import pycobalt.utils as utils

def register(name, callback, short_help=None, long_help=None):
    """
    Register an alias

    :param name: Name of alias
    :param callback: Callback for alias
    :param short_help: Short version of help, shown when running `help` with no
                       arguments
    :param long_help: Long version of help, shown when running `help <alias>`.
                      By default this is generated based on the short help and syntax of the
                      Python callback.
    """

    def alias_callback(*args):
        bid = int(args[0])
        if utils.check_args(callback, args):
            try:
                engine.debug('calling callback for alias {}'.format(name))
                callback(*args)
            except Exception as e:
                aggressor.berror(bid,
                    "Caught Python exception while executing alias '{}': {}\n    See Script Console for more details.".format(name, str(e)))
                raise e
        else:
            syntax = '{} {}'.format(name, utils.signature_command(callback, trim=1))
            aggressor.berror(bid, "Syntax: " + syntax)
            engine.error("Invalid number of arguments passed to alias '{}'. Syntax: {}".format(name, syntax))

    callbacks.register(alias_callback, prefix='alias_{}'.format(name))
    aggressor.alias(name, alias_callback)

    # register help info
    if not long_help:
        long_help = ''
        if short_help:
            long_help += short_help + '\n\n'
        long_help += 'Syntax: {} {}'.format(name, utils.signature_command(callback, trim=1))

    if not short_help:
        short_help = 'Custom python command'

    aggressor.beacon_command_register(name, short_help, long_help)

class alias:
    """
    Decorator for alias registration
    """

    def __init__(self, name, short_help=None, long_help=None):
        """
        :param name: Name of alias
        :param short_help: Short version of help, shown when running `help` with no
                           arguments
        :param long_help: Long version of help, shown when running `help <alias>`.
                          By default this is generated based on the short help and syntax of the
                          Python callback.
        """

        self.name = name
        self.short_help = short_help
        self.long_help = long_help

    def __call__(self, func):
        self.func = func
        register(self.name, self.func,
                 short_help=self.short_help,
                 long_help=self.long_help)
