#
# For registering script console commands
# Due to a limitation in cobalt strike these are only callable with the prefix 'py'
# For example: $ py test_command 1 2 3
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


import communicate
import utils

# { name: callback }
_callbacks = {}

def register(name, callback):
    global _callbacks

    communicate.command(name)
    _callbacks[name] = callback

def call(name, args):
    global _callbacks

    if name not in _callbacks:
        raise RuntimeError('unknown command: {}'.format(name))

    callback = _callbacks[name]
    if utils.check_args(callback, args):
        callback(*args)
    else:
        communicate.error("invalid number of arguments passed to command '{}'".format(name))

# Decorator
class command:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, func):
        self.func = func
        register(self.name, self.func)
