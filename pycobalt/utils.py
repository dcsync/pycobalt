#
# Utils
#

import inspect
import os

def check_args(func, args):
    """
    Check argument list length before calling a function

    For functions with *args there is no maximum argument length. The minimum
    argument length is the number of positional and keyword arguments a
    function has.
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

def signature(func):
    """
    Get stringy function argument signature
    """
    return str(inspect.signature(func))

def basedir(append='', relative=__file__):
    """
    Get base directory relative to 'relative' or __file__
    """
    return os.path.realpath(os.path.dirname(relative)) + '/' + append
