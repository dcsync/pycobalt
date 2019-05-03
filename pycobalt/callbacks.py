"""
For registering aggressor-to-python function callbacks

Usage example:

    def ps_callback(bid, results):
        engine.message('received ps callback for {}'.format(bid))

    aggressor.bps(bid, ps_callback)

When `aggressor.bps()` serializes its arguments it calls
`serialization.serialized(args),` which will register and serialize all
callbacks.

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

def call(name, args, return_id=None):
    """
    Call a function callback by name

    :param name: Name of callback
    :param args: Arguments to pass to callback (checked by `utils.check_args` first)
    :param return_id: Write a return value to the script with this ID (optional)
    :return: Return value of callback
    """

    engine.debug('Calling callback {}'.format(name))

    global _callbacks
    if name in _callbacks:
        callback = _callbacks[name]
        if utils.check_args(callback, args):
            return_value = callback(*args)

            # send return value
            if return_id:
                return_message = {
                    'value': return_value,
                    'id': return_id
                }
                engine.debug('Return sync: {} {}'.format(return_id, return_value))
                engine.write('return', return_message)

            return True
        else:
            syntax = '{}{}'.format(name, utils.signature(callback))
            raise RuntimeError("{} is an invalid number of arguments for callback '{}'. Syntax: {}".format(len(args), name, syntax))
            return False
    else:
        engine.debug('Tried to call unknown callback: {}'.format(name))
        return False

def name(func):
    """
    Get name for function. Return None if the callback isn't registered.

    :param func: Function to get name for
    :return: Name of function (or None if it's not registered)
    """

    global _reverse_callbacks
    if func in _reverse_callbacks:
        return _reverse_callbacks[func]
    else:
        return None

def register(func, prefix=None):
    """
    Register a callback

    :param func: Function to register
    :param prefix: Prefix of generated name (default: based on function name)
    :return: Name of registered callback
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

    :param func: Function to unregister
    :return: Name of callback (or None if not registered)
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
    Recursively check for callbacks in a list, tuple, or dict

    :param item: Item to check
    :return: True if item contains a callback
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
