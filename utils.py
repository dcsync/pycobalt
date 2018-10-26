#
# Utils
#

import inspect

# for verifying alias and command arg types
def verify_args(args, arg_types):
    # do not verify
    if arg_types == None:
        return True

    # check length
    if len(args) != len(arg_types):
        return False

    # check types
    for arg, arg_type in zip(args, arg_types):
        if not isinstance(arg, arg_type):
            return False

    # all good
    return True

# Check arguments before passing to function
def check_args(func, args):
    sig = inspect.signature(func)
    min_args = 0
    max_args = len(sig.parameters)
    for name, info in sig.parameters.items():
        if info.kind == inspect.Parameter.VAR_POSITIONAL:
            # no max arg
            max_args = 9999
        else:
            if not info.default:
                min_args += 1

    return len(args) >= min_args and len(args) <= max_args

# Get function signature
def signature(func):
    return str(inspect.signature(func))
