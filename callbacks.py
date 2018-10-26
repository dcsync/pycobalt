#
# For registering aggressor-to-python function callbacks
#
# Usage example:
#
#     def ps_callback(bid, results):
#         engine.message('received ps callback for {}'.format(bid))
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

_serialize_prefix = '<<callback>> '

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
def register(func, name=None):
    global _callbacks
    global _reverse_callbacks

    if not name:
        # make unique name based on function name and its hash
        name = '{}_{}'.format(func.__name__, str(hash(func)).replace('-', '1'))

    _callbacks[name] = func
    _reverse_callbacks[func] = name

def serialized(thing):
    if callable(thing):
        return _serialize_prefix + name(thing)
    else:
        return _serialize_prefix + thing
