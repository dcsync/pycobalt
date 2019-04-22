
# pycobalt.callbacks

For registering aggressor-to-python function callbacks

Usage example:

    def ps_callback(bid, results):
        engine.message('received ps callback for {}'.format(bid))

    aggressor.bps(bid, ps_callback)

When aggressor.bps() serializes its arguments it calls
serialization.serialized(args), which will register and serialize all callbacks.

To register a callback manually (useful for setting the serialized name manually):

    def ps_callback(bid, results):
        engine.message('received ps callback for {}'.format(bid))

    callbacks.register(ps_callback, prefix='our_ps_callback')
    aggressor.bps(bid, ps_callback)

## call
```python
call(name, args)
```

Call a function callback by name

**Arguments**:

- `name`: Name of callback
- `args`: Arguments to pass to callback (checked by `utils.check_args` first)

## name
```python
name(func)
```

Get name for function. Return None if the callback isn't registered.

**Arguments**:

- `func`: Function to get name for

**Returns**:

Name of function (or None if it's not registered)

## register
```python
register(func, prefix=None)
```

Register a callback

**Arguments**:

- `func`: Function to register
- `prefix`: Prefix of generated name (default: based on function name)

**Returns**:

Name of registered callback

## unregister
```python
unregister(func)
```

Unregister a callback

**Arguments**:

- `func`: Function to unregister

**Returns**:

Name of callback (or None if not registered)

## has_callback
```python
has_callback(item)
```

Recursively check for callbacks in a list, tuple, or dict

**Arguments**:

- `item`: Item to check

**Returns**:

True if item contains a callback
