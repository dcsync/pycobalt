#
# For registering aggressor-to-python function callbacks
#
# Regular example:
#
#     def ps_callback(bid, results):
#         engine.message('received ps callback for {}'.format(bid))
#     callbacks.register(ps_callback)
#
# Decorator example:
#
#     @callbacks.callback
#     def ps_callback(bid, results):
#         engine.message('received ps callback for {}'.format(bid))
#
# Usage example:
#
#     aggressor.bps(bid, ps_callback)
#

import collections

import pycobalt.utils as utils
import pycobalt.engine as engine

# { name: func }
_callbacks = {}
# { func: name }
_reverse_callbacks = {}

# Call a function callback
def call(name, args):
    global _callbacks
    if name in _callbacks:
        callback = _callbacks[name]
        if utils.check_args(callback, args):
            callback(*args)
        else:
            syntax = '{}{}'.format(name, utils.signature(callback))
            engine.error("invalid number of arguments passed for callback '{}'. syntax: {}".format(name, syntax))
    else:
        engine.debug('unknown callback {}'.format(name))

# Get name for function
def name(func):
    global _reverse_callbacks
    if func in _reverse_callbacks:
        return _reverse_callbacks[func]
    else:
        return None

# Register a callback
def register(name, callback):
    global _callbacks
    global _reverse_callbacks
    _callbacks[name] = callback
    _reverse_callbacks[callback] = name
    engine.callback(name)

# Decorator
class callback:
    def __init__(self, func):
        self.func = func
        self.name = '{}_{}'.format(self.func.__name__, str(hash(func)).replace('-', '1'))
        register(self.name, self)

    def __call__(self, *args):
        self.func(*args)
