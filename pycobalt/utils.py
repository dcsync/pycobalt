"""
Internal utilities. helpers.py has helper functions for writing PyCobalt
scripts.
"""

import inspect
import os
import re
import collections

def basedir(append='', relative=__file__):
    """
    Get base directory relative to 'relative' or the location of the utils.py
    file.

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

    sig = inspect.signature(func)
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

def yaml_basic_load(yaml):
    """
    Very rudimentary yaml to list-of-dict loader. It only supports a single
    list of dictionaries.

    :param yaml: Yaml to load
    :return: A list of dicts representing the items
    """

    items = []
    new_item = collections.OrderedDict()

    for line in yaml.splitlines():
        line = line.strip()

        # skip blank lines
        if not line:
            continue

        if line.startswith('- '):
            # start new item
            if new_item:
                items.append(new_item)
            line = line[2:]
            new_item = collections.OrderedDict()

        # key-value pair
        m = re.match('([^:]+): (.*)', line)
        if m:
            key = m.group(1)
            value = m.group(2)
            new_item[key] = value
        else:
            raise RuntimeError("yaml_basic_read: Could not parse yaml. It's probably too complex")

    if new_item:
        items.append(new_item)

    return items

def yaml_basic_dump(items):
    """
    Very rudimentary list-of-dict to yaml dumper. It only supports a single
    list of dictionaries.

    :param items: List of dictionaries to dump
    :return: Yaml representing the items
    """

    yaml = ''

    for item in items:
        first = True
        for key, value in item.items():
            # choose prefix
            if first:
                first = False
                prefix = '- '
            else:
                prefix = '  '

            yaml += '{}{}: {}\n'.format(prefix, key, value)

    return yaml
