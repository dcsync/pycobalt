#
# For registering script console commands
#
# Regular example:
#
#     def test_command(args):
#         print(args)
#     commandes.register('test_command', test_command)
#
# Decorator example:
#
#     @commandes.command('test_command')
#     def test_command(args):
#         print(args)
#


import pycobalt.engine as engine
import pycobalt.utils as utils

# { name: callback }
_callbacks = {}

def register(name, callback):
    global _callbacks

    engine.command(name)
    _callbacks[name] = callback

def call(name, args):
    global _callbacks

    if name not in _callbacks:
        raise RuntimeError('unknown command: {}'.format(name))

    callback = _callbacks[name]
    if utils.check_args(callback, args):
        callback(*args)
    else:
        syntax = '{}{}'.format(name, utils.signature(callback))
        engine.error("invalid number of arguments passed to command '{}'. syntax: {}".format(name, syntax))

# Decorator
class command:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, func):
        self.func = func
        register(self.name, self.func)
