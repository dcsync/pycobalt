#
# Utils
#

import inspect
import os

def basedir(append='', relative=__file__):
    """
    Get base directory relative to 'relative' or __file__

    :param append: Text to append to base directory
    :param relative: Get base directory relative to this
    :return: The base directory of this script (or relative) with append on the end
    """

    return os.path.realpath(os.path.dirname(relative)) + '/' + append

def check_args(func, args):
    """
    Check argument list length before calling a function

    For functions with *args there is no maximum argument length. The minimum
    argument length is the number of positional and keyword arguments a
    function has.

    :param func: Function to check
    :param args: Args to check
    :return: True if function arguments are valid
    """

    sig = inspect.signature(func)
    min_args = 0
    max_args = len(sig.parameters)
    for name, info in sig.parameters.items():
        if info.kind == inspect.Parameter.VAR_POSITIONAL:
            # no max arg
            max_args = 9999
        else:
            # positional, kwarg, etc
            if info.default == inspect._empty:
                min_args += 1

    return len(args) >= min_args and len(args) <= max_args

def signature(func, trim=0):
    """
    Get stringy function argument signature

    :param func: Function to get signature for
    :param trim: Trim N arguments from front
    :return: Stringified function argument signature
    """

    sig = inspect.signature(func))
    params = list(sig.parameters.values())[trim:]
    sig = sig.replace(parameters=params)
    return str(sig)

def func():
    """
    Get function object of caller

    :return: Function object of calling function
    """

    tup = inspect.stack()[2]
    return tup[0].f_globals[tup[3]]
