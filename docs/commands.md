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
register(name, callback)
```

Register a command

**Arguments**:

- `name`: Name of command
- `callback`: Callback for command

## command
```python
command(self, name)
```

Decorator for command registration

