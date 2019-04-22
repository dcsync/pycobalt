# pycobalt.engine

For communication with cobaltstrike

## enable_debug
```python
enable_debug()
```

Enable debug messages

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

:param line: Line to write

## write
```python
write(message_type, message='')
```

Write a message to cobaltstrike. Message can be anything serializable by
`serialization.py`. This includes primitives, bytes, lists, dicts, tuples,
and callbacks (automatically registered).

:param message_type: Type/label of message
:param message: Message contents

## handle_message
```python
handle_message(name, message)
```

Handle a received message according to its name

:param name: Name/type/label of message
:param message: Message body

## parse_line
```python
parse_line(line)
```

Parse a serialized input line for passing to `engine.handle_message`.

:param line: Line to parse. Should look like {'name':<name>, 'message':<message>}
:return: Tuple containing 'name' and 'message'

## fork
```python
fork()
```

Tell cobaltstrike to fork into a new thread.

Menu trees have to be registered before we fork into a new thread so this
is called in `engine.loop()` after the registration is finished.

## loop
```python
loop(fork_first=True)
```

Loop forever, handling messages. Does not return until the pipe closes.
Exceptions are printed to the script console.

:param fork_first: Whether to call `fork()` first.

## stop
```python
stop()
```

Stop the script (just exits the process)

## read
```python
read()
```

Read a message line

:return: Tuple containing message name and contents (as returned by
         `parse_line`).

## readiter
```python
readiter()
```

Read message lines

:return: Iterator with an item for each read/parsed line. Each item is the
         same as the return value of `engine.read()`.

## call
```python
call(name, args=None, silent=False, fork=False, sync=True)
```

Call a sleep/aggressor function. You should use the `aggressor.py` helpers
where possible.

:param name: Name of function to call
:param args: Arguments to pass to function
:param silent: Don't print tasking information (! operation) (only works
               for some functions)
:param fork: Call in its own thread
:param sync: Wait for return value
:return: Return value of function if `sync` is True

## eval
```python
eval(code)
```

Eval aggressor code. Does not provide a return value.

:param code: Code to eval

## menu
```python
menu(menu_items)
```

Register a cobaltstrike menu tree

:param menu_items: Menu tree as returned by the `gui.py` helpers.

## error
```python
error(line)
```

Write error notice

:param line: Line to write

## message
```python
message(line)
```

Write script console message. The Aggressor side will add a prefix to your
message. To print raw messages use `aggressor.print` and
`aggressor.println`.

:param line: Line to write

## delete
```python
delete(handle)
```

Delete an object with its serialized handle. This just removed the global
reference. The object will stick around if it's referenced elsewhere.

:param handle: Handle of object to delete

