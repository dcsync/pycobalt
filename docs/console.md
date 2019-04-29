
# pycobalt.console

Helper functions for printing to the Beacon Console and Script Console. This
includes:

  - Modifying the Beacon Console output with Aggressor's undocumented `set
    BEACON_OUTPUT` blocks.
  - Helper functions for coloring and styling text.
  - Helper functions for creating ASCII tables and aligned text in the console.

Changing Beacon Console output (regular example):

    def beacon_output(bid, contents):
        return '<output>
{}
</output>'.format(contents)
    console.register('beacon_output', beacon_output)

Changing Beacon Console output (decorator example):

    @console.modifier('beacon_output')
    def beacon_output(bid, contents):
        return '<output>
{}
</output>'.format(contents)

Printing colored text to the Script Console:

    engine.message(console.red('red text'));

I'm sort of color blind so orange might be red and cyan might be blue. To see
all of Cobalt Strike's color options run this in the Script Console:

    e for ($i = 0; $i < 100; $i++) { println($i . "    " . chr($i) . "test"); }

I've attempted to document the arguments to various output modifiers below.
This documentation is mostly based on Cobalt Strike's
[`default.cna`](https://www.cobaltstrike.com/aggressor-script/default.cna).

Event Log messages
 - `EVENT_PUBLIC`: from, text, when
 - `EVENT_PRIVATE`: from, to, text, when
 - `EVENT_ACTION`: from, text, when
 - `EVENT_JOIN`: from, when
 - `EVENT_QUIT`: from, when
 - `EVENT_NOTIFY`: text, when
 - `EVENT_NEWSITE`: from, text, when
 - `EVENT_NOUSER`: to, when
 - `EVENT_BEACON_INITIAL`: from, when
 - `EVENT_SSH_INITIAL`: from, when
 - `EVENT_USERS`: users
 - `EVENT_SBAR_LEFT`: <no arguments?>
 - `EVENT_SBAR_RIGHT`: lag

Web Log
 - `WEB_HIT`: method, uri, addr, ua, response, size, handler, when

Profiler
 - `PROFILER_HIT`: <five unknown arguments>

Keystrokes
 - `KEYLOGGER_HIT`: <four unknown arguments>

Beacon Console
 - `BEACON_SBAR_LEFT`: bid, metadata
 - `BEACON_SBAR_RIGHT`: bid, metadata
 - `BEACON_CHECKIN`: bid, message
 - `BEACON_ERROR`: bid, message
 - `BEACON_TASKED`: bid, message
 - `BEACON_OUTPUT`: bid, message
 - `BEACON_OUTPUT_ALT`: bid, message
 - `BEACON_OUTPUT_PS`: bid, output (see `helpers.parse_ps`)
 - `BEACON_OUTPUT_LS`: bid, output (see `helpers.parse_ls`)
 - `BEACON_OUTPUT_JOBS`: bid, output (see `helpers.parse_jobs`)
 - `BEACON_OUTPUT_DOWNLOADS`: bid, downloads={'name', 'path', 'size', 'rcvd'}
 - `BEACON_OUTPUT_EXPLOITS`: <no arguments?>
 - `BEACON_OUTPUT_HELP`: <no arguments?>
 - `BEACON_OUTPUT_HELP_COMMAND`: command
 - `BEACON_MODE`: bid?, output
 - `BEACON_INPUT`: bid, user, text, when

Phishing
 - `SENDMAIL_START`: unknown, ntarget, attachment, bounceto, server, subject, templatef, url
 - `SENDMAIL_PRE`: unknown, dest
 - `SENDMAIL_POST`: cid, email, status, message
 - `SENDMAIL_DONE`: <no arguments?>

SSH Beacon Console
 - `SSH_OUTPUT_HELP`: <no arguments?>
 - `SSH_OUTPUT_HELP_COMMAND`: command
 - `SSH_SBAR_LEFT`: bid, metadata
 - `SSH_SBAR_RIGHT`: bid, metadata
 - `SSH_CHECKIN`: bid, message
 - `SSH_ERROR`: bid, message
 - `SSH_TASKED`: bid, message
 - `SSH_OUTPUT`: bid, message
 - `SSH_OUTPUT_ALT`: bid, message
 - `SSH_OUTPUT_DOWNLOADS`: bid, downloads={'name', 'path', 'size', 'rcvd'}
 - `SSH_INPUT`: bid, user, text, when

## is_known
```python
is_known(name)
```

Check if a modifier is one of the known cobaltstrike ones

**Arguments**:

- `name`: Name of modifier

**Returns**:

True if modifier is a known one

## register
```python
register(name, callback, known_only=True)
```

Register an modifier callback.

**Arguments**:

- `name`: Name of modifier (case-insensitive)
- `callback`: Modifier callback
- `known_only`: Only allow known modifiers

**Returns**:

Name of registered callback

## unregister
```python
unregister(callback)
```

Unregister a modifier callback. There's no way to easily unregister a callback in
Aggressor so this will forever leave us with broken callbacks coming back
from the teamserver.

**Arguments**:

- `callback`: Callback to unregister

**Returns**:

Name of unregistered callback

## modifier
```python
modifier(name, known_only=True)
```

Decorator for output modifier registration

## stripped_length
```python
stripped_length(string)
```

Get the length of a string without control codes

**Arguments**:

- `string`: String

**Returns**:

Length of string minus control codes

## justify
```python
justify(string, total, side='left', fill=' ')
```

Justify a string for the console

**Arguments**:

- `string`: String to justify
- `total`: Total size to justify to
- `side`: Side to justify to (center, left, or right)
- `fill`: Character to fill with

**Returns**:

Justified string

## table
```python
table(items, keys=None, show_headers=True)
```

Make a pretty ASCII table

**Arguments**:

- `items`: Items to make a table for (list of dictionaries)
- `keys`: Either a list of dictionary keys or a dictionary containing `{key: pretty_header}`
- `show_headers`: Show the table headers (default: True)

**Returns**:

Pretty ASCII table

## strip
```python
strip(text)
```

Strip control codes from a string.

**Arguments**:

- `text`: String to strip

**Returns**:

Stripped string

## bold
```python
bold(text)
```

Style text bold for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## underline
```python
underline(text)
```

Style text underlined for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## white
```python
white(text)
```

Style text white for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## black
```python
black(text)
```

Style text black for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## blue
```python
blue(text)
```

Style text blue for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## green
```python
green(text)
```

Style text green for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## orange_red
```python
orange_red(text)
```

Style text orange-red for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## red
```python
red(text)
```

Style text red for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## purple
```python
purple(text)
```

Style text purple for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## orange
```python
orange(text)
```

Style text orange for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## yellow
```python
yellow(text)
```

Style text yellow for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## bright_green
```python
bright_green(text)
```

Style text bright-green for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## blue_green
```python
blue_green(text)
```

Style text blue-green for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## cyan
```python
cyan(text)
```

Style text cyan for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## light_purple
```python
light_purple(text)
```

Style text light-purple for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## pink
```python
pink(text)
```

Style text pink for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text

## grey
```python
grey(text)
```

Style text grey for the Script Console and Beacon Console.

**Arguments**:

- `text`: Text to style

**Returns**:

Styled text
