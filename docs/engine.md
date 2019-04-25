
# pycobalt.engine

For communication with Cobalt Strike

## enable_debug
```python
enable_debug()
```

Enable debug messages on the Python side

To enable the Aggressor debug messages run `python-debug` in the Script
Console or set `$pycobalt_debug_on = true` in your Aggressor script.

## disable_debug
```python
disable_debug()
```

Disable debug messages

## debug
```python
debug(line)
```

Write script console debug message

**Arguments**:

- `line`: Line to write

## write
```python
write(message_type, message='')
```

Write a message to Cobalt Strike. Message can be anything serializable by
`serialization.py`. This includes primitives, bytes, lists, dicts, tuples,
and callbacks (automatically registered).

**Arguments**:

- `message_type`: Type/label of message
- `message`: Message contents

## handle_message
```python
handle_message(name, message)
```

Handle a received message according to its name

**Arguments**:

- `name`: Name/type/label of message
- `message`: Message body

## parse_line
```python
parse_line(line)
```

Parse a serialized input line for passing to `engine.handle_message`.

**Arguments**:

- `line`: Line to parse. Should look like {'name':<name>, 'message':<message>}

**Returns**:

Tuple containing 'name' and 'message'

## fork
```python
fork()
```

Tell Cobalt Strike to fork into a new thread.

Menu trees have to be registered before we fork into a new thread so this
is called in `engine.loop()` after the registration is finished.

## read_pipe
```python
read_pipe()
```

read_pipe a message line

**Returns**:

Tuple containing message name and contents (as returned by
         `parse_line`).

## read_pipe_iter
```python
read_pipe_iter()
```

read_pipe message lines

**Returns**:

Iterator with an item for each read_pipe/parsed line. Each item is the
         same as the return value of `engine.read_pipe()`.

## loop
```python
loop(fork_first=True)
```

Loop forever, handling messages. Does not return until the pipe closes.
Exceptions are printed to the script console.

**Arguments**:

- `fork_first`: Whether to call `fork()` first.

## stop
```python
stop()
```

Stop the script (just exits the process)

## call
```python
call(name, args=None, silent=False, fork=False, sync=True)
```

Call a sleep/aggressor function. You should use the `aggressor.py` helpers
where possible.

**Arguments**:

- `name`: Name of function to call
- `args`: Arguments to pass to function
- `silent`: Don't print tasking information (! operation) (only works
               for some functions)
- `fork`: Call in its own thread
- `sync`: Wait for return value

**Returns**:

Return value of function if `sync` is True

## eval
```python
eval(code)
```

Eval aggressor code. Does not provide a return value.

**Arguments**:

- `code`: Code to eval

## menu
```python
menu(menu_items)
```

Register a Cobalt Strike menu tree

**Arguments**:

- `menu_items`: Menu tree as returned by the `gui.py` helpers.

## error
```python
error(line)
```

Write error notice

**Arguments**:

- `line`: Line to write

## message
```python
message(line)
```

Write script console message. The Aggressor side will add a prefix to your
message. To print raw messages use `aggressor.print` and
`aggressor.println`.

**Arguments**:

- `line`: Line to write

## delete
```python
delete(handle)
```

Delete an object with its serialized handle. This just removed the global
reference. The object will stick around if it's referenced elsewhere.

**Arguments**:

- `handle`: Handle of object to delete
