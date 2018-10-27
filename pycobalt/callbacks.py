"""
For registering aggressor-to-python function callbacks

Usage example:

    def ps_callback(bid, results):
        engine.message('received ps callback for {}'.format(bid))

    aggressor.bps(bid, ps_callback)

When aggressor.bps() serializes its arguments it calls
callbacks.serialized(args), which will register and serialize all callbacks.

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

# for serializing callbacks
_serialize_prefix = '<<--pycobalt callback-->> '

# Call a function callback
def call(name, args):
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

# Get name for function
def name(func):
    global _reverse_callbacks
    if func in _reverse_callbacks:
        return _reverse_callbacks[func]
    else:
        return None

# Register a callback
def register(func, prefix=None):
    global _callbacks
    global _reverse_callbacks

    if not prefix:
        prefix = func.__name__.replace('<', '').replace('>', '')

    # make unique name based on prefix and function hash
    name = '{}_{}'.format(prefix, str(hash(func)).replace('-', '1'))

    _callbacks[name] = func
    _reverse_callbacks[func] = name

    return name

def serialized(item):
    """
    Serialize and register callbacks
    """

    if isinstance(item, list) or isinstance(item, tuple):
        new_list = []
        for child in item:
            new_list.append(serialized(child))
        return new_list
    elif isinstance(item, dict):
        new_dict = {}
        for key, value in item.items():
            new_dict[key] = serialized(value)
        return new_dict
    elif callable(item):
        func_name = name(item)
        if not func_name:
            func_name = register(item)
        return _serialize_prefix + func_name
    else:
        return item

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
