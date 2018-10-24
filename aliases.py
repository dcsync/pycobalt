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

import communicate
import aggressor
import utils

# { name: callback }
_callbacks = {}

def register(name, callback):
    global _callbacks

    communicate.alias(name)
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
        aggressor.blog(bid, "{}: invalid number of arguments".format(name))
        communicate.error("invalid number of arguments passed to alias '{}'".format(name))

# Decorator
class alias:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, func):
        self.func = func
        register(self.name, self.func)
