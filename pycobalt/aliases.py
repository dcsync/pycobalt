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

_default_quote_replacement = None

def set_quote_replacement(replacement):
    """
    Set the default `quote_replacement` value. Passing `quote_replacement=` to
    `register()` or `@alias()` overrides this.

    See `register()` for more information.

    :param replacement: Quote replacement string
    """

    global _default_quote_replacement
    _default_quote_replacement = replacement

def register(name, callback, short_help=None, long_help=None,
             quote_replacement=None):
    """
    Register an alias

    Regarding the `quote_replacement` argument: Cobalt Strike's Beacon console
    uses double quotes to enclose arguments with spaces in them. There's no way
    to escape double quotes within those quotes though. Set `quote_replacement`
    to a string and PyCobalt will replace it with " in each argument. Call
    `aliases.set_quote_replacement(<string>)` to change the default quote
    replacement behavior.

    :param name: Name of alias
    :param callback: Callback for alias
    :param short_help: Short version of help, shown when running `help` with no
                       arguments
    :param long_help: Long version of help, shown when running `help <alias>`.
                      By default this is generated based on the short help and syntax of the
                      Python callback.
    :param quote_replacement: Replace this string with " in each
                              argument.
    """

    # this is a workaround for a famously stupid python issue where keyword
    # arguments are not passed to closures correctly.
    quote_replacement_ = quote_replacement

    def alias_callback(*args):
        # first argument is bid
        bid = int(args[0])

        # see above
        quote_replacement = quote_replacement_

        # check arguments
        if not utils.check_args(callback, args):
            syntax = '{} {}'.format(name, utils.signature_command(callback, trim=1))
            aggressor.berror(bid, "Syntax: " + syntax)
            engine.error("Invalid number of arguments passed to alias '{}'. Syntax: {}".format(name, syntax))
            return

        # handle the quote replacement character
        if not quote_replacement:
            global _default_quote_replacement
            quote_replacement = _default_quote_replacement

        if quote_replacement:
            args = [arg.replace(quote_replacement, '"') for arg in args]

        try:
            # run the alias callback
            #engine.debug('calling callback for alias {}'.format(name))
            callback(*args)
        except Exception as e:
            # print exception summaries to the beacon log. raise the
            # Exception again so the full traceback can get printed to the
            # Script Console
            aggressor.berror(bid,
                "Caught Python exception while executing alias '{}': {}\n    See Script Console for more details.".format(name, str(e)))
            raise e

    callbacks.register(alias_callback, prefix='alias_{}'.format(name))
    aggressor.alias(name, alias_callback, sync=False)

    # by default short_help is just 'Custom Python command'
    if not short_help:
        short_help = 'Custom Python command'

    # by default long_help is short_help
    if not long_help:
        long_help = short_help

    # tack the syntax on the long_help, even if the user set their own
    long_help += '\n\nSyntax: {} {}'.format(name, utils.signature_command(callback, trim=1))

    aggressor.beacon_command_register(name, short_help, long_help, sync=False)

class alias:
    """
    Decorator for alias registration
    """

    def __init__(self, name, short_help=None, long_help=None,
                 quote_replacement=None):
        """
        :param name: Name of alias
        :param short_help: Short version of help, shown when running `help` with no
                           arguments
        :param long_help: Long version of help, shown when running `help <alias>`.
                          By default this is generated based on the short help and syntax of the
                          Python callback.
        :param quote_replacement: Replace this string with " in each
                                  argument (see notes in the `register()`
                                  function)
        """

        self.name = name
        self.short_help = short_help
        self.long_help = long_help
        self.quote_replacement = quote_replacement

    def __call__(self, func):
        self.func = func
        register(self.name, self.func,
                 short_help=self.short_help,
                 long_help=self.long_help,
                 quote_replacement=self.quote_replacement)
