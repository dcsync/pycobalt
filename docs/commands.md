
# pycobalt.commands

For registering script console commands

Regular example:

    def test_command(args):
        print(args)
    commandes.register('test_command', test_command)

Decorator example:

    @commands.command('test_command')
    def test_command(args):
        print(args)

## register
```python
register(name, callback, quote_replacement=None)
```

Register a command

Regarding the `quote_replacement` argument: Cobalt Strike's Script Console
uses double quotes to enclose arguments with spaces in them. There's no way
to escape double quotes within those quotes though. Set `quote_replacement`
to a string and PyCobalt will replace it with " in each argument.

**Arguments**:

- `name`: Name of command
- `callback`: Callback for command
- `quote_replacement`: Replace this string with " in each
                          argument.

## command
```python
command(name, quote_replacement=None)
```

Decorator for command registration
