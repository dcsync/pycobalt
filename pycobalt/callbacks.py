"""
For registering aggressor-to-python function callbacks

Usage example:

    def ps_callback(bid, results):
        engine.message('received ps callback for {}'.format(bid))

    aggressor.bps(bid, ps_callback)

When aggressor.bps() serializes its arguments it calls
serialization.serialized(args), which will register and serialize all callbacks.

To register a callback manually (useful for setting the serialized name manually):

    def ps_callback(bid, results):
        engine.message('received ps callback for {}'.format(bid))

    callbacks.register(ps_callback, prefix='our_ps_callback')
    aggressor.bps(bid, ps_callback)
"""

import collections

import pycobalt.utils as utils
import pycobalt.engine as engine

# { name: func }
_callbacks = {}
# { func: name }
_reverse_callbacks = {}

def call(name, args):
    """
    Call a function callback by name
    """

    global _callbacks
    if name in _callbacks:
        callback = _callbacks[name]
        if utils.check_args(callback, args):
            callback(*args)
        else:
            syntax = '{}{}'.format(name, utils.signature(callback))
            engine.error("{} is an invalid number of arguments for callback '{}'. syntax: {}".format(len(args), name, syntax))
    else:
        engine.debug('unknown callback {}'.format(name))

def name(func):
    """
    Get name for function. Return None if the callback isn't registered.
    """

    global _reverse_callbacks
    if func in _reverse_callbacks:
        return _reverse_callbacks[func]
    else:
        return None

def register(func, prefix=None):
    """
    Register a callback
    """

    global _callbacks
    global _reverse_callbacks

    if not prefix:
        prefix = func.__name__.replace('<', '').replace('>', '')

    # make unique name based on prefix and function hash
    name = '{}_{}'.format(prefix, str(hash(func)).replace('-', '1'))

    _callbacks[name] = func
    _reverse_callbacks[func] = name

    return name

def unregister(func):
    """
    Unregister a callback
    """

    func_name = name(func)
    if func_name:
        del _reverse_callbacks[func]
        del _callbacks[func_name]
        return func_name
    else:
        return None

def has_callback(item):
    """
    Recursively check for callbacks in a list/dict
    """

    if isinstance(item, list) or isinstance(item, tuple):
        for child in item:
            if has_callback(child):
                return True
        return False
    elif isinstance(item, dict):
        for value in item.values():
            if has_callback(value):
                return True
        return False
    elif callable(item):
        return True
    else:
        return False
