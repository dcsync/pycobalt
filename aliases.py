#
# For registering aliasess
#
# Regular example:
#
#     def test_alias(args):
#         print(args)
#     aliases.register('test_alias', test_alias)
#
# Decorator example:
#
#     @aliases.alias('test_alias')
#     def test_alias(args):
#         print(args)
#

import pycobalt.engine as engine
import pycobalt.aggressor as aggressor
import pycobalt.utils as utils

# { name: callback }
_callbacks = {}

def register(name, callback):
    global _callbacks

    engine.alias(name)
    _callbacks[name] = callback

def call(name, args):
    global _callbacks

    if name not in _callbacks:
        raise RuntimeError('unknown alias: {}'.format(name))

    callback = _callbacks[name]
    if utils.check_args(callback, args):
        callback(*args)
    else:
        bid = int(args[0])
        syntax = '{}{}'.format(name, utils.signature(callback))
        aggressor.berror(bid, "syntax: " + syntax)
        engine.error("invalid number of arguments passed to alias '{}'. syntax: {}".format(name, syntax))

# Decorator
class alias:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, func):
        self.func = func
        register(self.name, self.func)
