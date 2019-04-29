PyCobalt is a Python API for Cobalt Strike.

# Quick Start

Have Python3+ installed on Linux. PyCobalt probably works on macOS and Windows
as well. I only test it on Linux though.

First you're going to install the PyCobalt Python library. To do that run
`python3 setup.py install`. If you need more installation help head over to the
[Installation](#installation) section.

Now you're ready to start writing PyCobalt scripts. A Python script for
PyCobalt looks like this:

    #!/usr/bin/env python3

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor
    import pycobalt.aliases as aliases

    # register this function as a Beacon Console alias
    @aliases.alias('example-alias')
    def example_alias(bid):
        aggressor.blog2(bid, 'example alias')

    # read commands from cobaltstrike. must be called last
    engine.loop()

You need to execute this Python script from an Aggressor script. An Aggressor
script for PyCobalt looks like this:

    $pycobalt_path = '/root/pycobalt/aggressor';
    include($pycobalt_path . '/pycobalt.cna');
    python(script_resource('example.py'));

It's necessary to set the `$pycobalt_path` variable so that PyCobalt can find
its dependencies.

Now load this Aggressor script into Cobalt Strike. Open up the Cobalt Strike
Script Console and you'll see this:

    [pycobalt] Executing script /root/pycobalt/example.py

PyCobalt comes with some Script Console commands:

    aggressor> python-list
    [pycobalt] Running scripts:
     -  /root/pycobalt/example.py

    aggressor> python-stop /root/pycobalt/example.py
    [pycobalt] Asking script to stop: /root/pycobalt/example.py
    [pycobalt] Script process exited: /root/pycobalt/example.py

    aggressor> python /root/pycobalt/example.py
    [pycobalt] Executing script /root/pycobalt/example.py

    aggressor> python-stop-all
    [pycobalt] Asking script to stop: /root/pycobalt/example.py
    [pycobalt] Script process exited: /root/pycobalt/example.py

When you reload your Aggressor script you should explicitly stop the Python
scripts first. Otherwise they'll run forever doing nothing.

    aggressor> python-stop-all
    [pycobalt] Asking script to stop: /root/pycobalt/example.py
    [pycobalt] Script process exited: /root/pycobalt/example.py

    aggressor> reload example.cna
    [pycobalt] Executing script /root/pycobalt/example.py

You can restart individual scripts as well:

    aggressor> python /root/pycobalt/example.py
    [pycobalt] /root/pycobalt/example.py is already running. Restarting.
    [pycobalt] Asking script to stop: /root/pycobalt/example.py 
    [pycobalt] Script process exited: /root/pycobalt/example.py
    [pycobalt] Executing script /root/pycobalt/example.py 

For these commands to work properly you can only call PyCobalt in one Aggressor
script. Personally I have a single all.cna file with a bunch of calls to
`python()` and  `include()`.

# PyCobalt Python Library

PyCobalt includes several Python modules. Here's the full list, with links to
usage and examples:

  - [pycobalt.engine](#script-console-messages): Main communication code
  - [pycobalt.aggressor](#aggressor): Stubs for calling Aggressor functions
  - [pycobalt.aliases](#aliases): Beacon Console alias registration
  - [pycobalt.commands](#commands): Script Console command registration
  - [pycobalt.events](#events): Event handler registration
  - [pycobalt.console](#console): Output modifiers and console colors
  - [pycobalt.gui](#gui): Context menu registration
  - [pycobalt.helpers](#helpers):
    Assorted helper functions and classes to make writing scripts easier
  - [pycobalt.bot](#bot): Event Log bot toolkit
  - [pycobalt.sharpgen](#sharpgen):
       Helper functions for using [SharpGen](https://github.com/cobbr/SharpGen)

For full pydoc documentation head over to the
[docs/](https://github.com/dcsync/pycobalt/tree/master/docs) directory.

# Usage and Examples

Here are some script examples. For more complete examples see the
[examples](https://github.com/dcsync/pycobalt/tree/master/examples) directory.

## Script Console Messages

To print a message on the Script Console:

    import pycobalt.engine as engine

    engine.message('test message')

    engine.loop()

This shows up in the Script Console as:

    [pycobalt example.py] test message

To print an error message on the Script Console:

    import pycobalt.engine as engine

    engine.error('test error')

    engine.loop()

This shows up in the Script Console as:

    [pycobalt example.py error] test error

To print debug messages to the Script Console:

    import pycobalt.engine as engine

    engine.enable_debug()
    engine.debug('debug message 1')
    engine.debug('debug message 2')
    engine.disable_debug()
    engine.debug('debug message 3')

    engine.loop()

This shows up in the Script Console as:

    [pycobalt example.py debug] debug message 1
    [pycobalt example.py debug] debug message 2

To print raw stuff to the Script Console you can just call the Aggressor print
functions:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    aggressor.println('raw message')

    engine.loop()

## Aggressor

[pycobalt.aggressor](https://github.com/dcsync/pycobalt/tree/master/docs/aggressor.md)
provides wrappers for all ~300
[Aggressor](https://www.cobaltstrike.com/aggressor-script/functions.html)
functions and some [Sleep](http://sleep.dashnine.org/manual/index.html)
functions. Here's how you call an Aggressor function:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    for beacon in aggressor.beacons():
        engine.message(beacon['user'])

    engine.loop()

To call an Aggressor function with a callback:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    def my_callback(bid, results):
        aggressor.blog2(bid, 'ipconfig: ' + results)

    for beacon in aggressor.beacons():
        bid = beacon['bid']
        aggressor.bipconfig(bid, my_callback)

    engine.loop()

To call an Aggressor function without printing tasking information to the
Beacon Console (`!` operator, only supported by certain functions):

    ...
    aggressor.bshell(bid, 'whoami', silent=True)
    ...

For information on calling Sleep or Aggressor functions that aren't in
pycobalt.aggressor (including your own Aggressor functions) see the [Sleep
Functions](#sleep-functions) section below.

For notes on using non-primitive objects such as dialog objects see the
[Non-Primitive Objects](#non-primitive-objects) section.

## Aliases

[pycobalt.aliases](https://github.com/dcsync/pycobalt/tree/master/docs/aliases.md)
provides the ability to register Beacon Console aliases.

    import pycobalt.engine as engine
    import pycobalt.aliases as aliases
    import pycobalt.aggressor as aggressor

    @aliases.alias('test_alias')
    def test_alias(bid, arg1, arg2='test'):
        aggressor.blog2(bid, 'test alias called with args {} {}'.format(arg1, arg2))

    engine.loop()

You can register help info with an alias and it will show up when you run
Cobalt Strike's `help` command:

    ...
    @aliases.alias('test_alias', short_help='Tests alias registration')
    ...

By default the long help will be based on the short help and Python function
syntax. For example:

    beacon> help test_alias
    Tests alias registration
    
    Syntax: test_alias arg1 [arg2=test]

Or you can specify the long help yourself:

    ...
    @aliases.alias('test_alias', 'Tests alias registration', 'Test alias\n\nLong help')
    ...

### Argument Checking

When the alias is called its arguments will be automagically checked against the
arguments of the Python function. For example:

    beacon> test_alias 1 2 3
    [-] Syntax: test_alias arg1 [arg2=test]

To bypass this you can use python's `*` operator:

    import pycobalt.engine as engine
    import pycobalt.aliases as aliases
    import pycobalt.aggressor as aggressor

    @aliases.alias('test_alias', 'Tests alias registration')
    def test_alias(bid, *args):
        aggressor.blog2(bid, 'test alias called with args: ' + ', '.join(args))

    engine.loop()

This also allows you to use Python's argparse with aliases. For more
information about using argparse see the [Argparse](#argparse) section below.

### Exception Handling

If an unhandled exception occurs in your alias callback PyCobalt will catch it
and print the exception information to the Beacon Console. For example, while I
was writing the previous example I typed `engine.blog2()` instead of
`aggressor.blog2()` by accident and got this error:

    beacon> test_alias
    [-] Caught Python exception while executing alias 'test_alias': module 'pycobalt.engine' has no attribute 'blog2'
        See Script Console for more details.

In the Script Console:

    ...
    [pycobalt script error] exception: module 'pycobalt.engine' has no attribute 'blog2'
    [pycobalt script error] traceback: Traceback (most recent call last):
      File "/usr/lib/python3.7/site-packages/pycobalt-1.0.0-py3.7.egg/pycobalt/engine.py", line 122, in loop
        handle_message(name, message)
      File "/usr/lib/python3.7/site-packages/pycobalt-1.0.0-py3.7.egg/pycobalt/engine.py", line 89, in handle_message
        callbacks.call(callback_name, callback_args)
      File "/usr/lib/python3.7/site-packages/pycobalt-1.0.0-py3.7.egg/pycobalt/callbacks.py", line 42, in call
        callback(*args)
      File "/usr/lib/python3.7/site-packages/pycobalt-1.0.0-py3.7.egg/pycobalt/aliases.py", line 36, in alias_callback
        raise e
      File "/usr/lib/python3.7/site-packages/pycobalt-1.0.0-py3.7.egg/pycobalt/aliases.py", line 32, in alias_callback
        callback(*args)
      File "/sandboxed/tools/cobaltstrike/scripts/recon.py", line 170, in test_alias
        engine.blog2(bid, 'test alias called with args: ' + ', '.join(args))
    AttributeError: module 'pycobalt.engine' has no attribute 'blog2'

### Double Quotes

Cobalt Strike's Beacon and Script Consoles allow you to pass arguments
containing spaces if they're enclosed in double quotes. There's no way to
escape double quotes and pass arguments containing both spaces and double
quotes though. As a bit of a workaround PyCobalt includes an optional quote
replacement mechanism.

To use it simply pass `quote_replacement=<string>` to the alias registration
function or decorator. For example:

    ...
    @aliases.alias('test_alias', quote_replacement='^')
    def test_alias(bid, *args):
        aggressor.blog2(bid, 'test alias called with args: ' + ', '.join(args))
    ...

    beacon> test_alias "a ^b^" ^c^
    test alias called with args: a "b", "c"

## Commands

[pycobalt.commands](https://github.com/dcsync/pycobalt/tree/master/docs/commands.md)
provides the ability to register Script Console commands.

    import pycobalt.engine as engine
    import pycobalt.commands as commands

    @commands.command('test_command')
    def test_command():
        engine.message('test_command called')

    engine.loop()

[Exception handling](#exception-handling), [argument
checking](#argument-checking), and [double quote replacement](#double-quotes)
is similar to that of aliases. Exceptions are printed to the Script Console.

## Events

[pycobalt.events](https://github.com/dcsync/pycobalt/tree/master/docs/events.md)
provides the ability to register event handlers (Aggressor's `on` function).

    import pycobalt.engine as engine
    import pycobalt.events as events

    @events.event('beacon_initial')
    def beacon_initial_handler(bid):
        aggressor.bnote(bid, 'fresh')

    engine.loop()

This will raise an exception if the event isn't one of the official
Cobalt Strike ones. To register an arbitrary event (e.g. for use with
`fireEvent`):

    ...
    @events.event('myevent', official_only=False)
    ...

The arguments to your event callback are checked against incoming events. If
they don't match an Exception will be printed to the Script Console.

## Console

[pycobalt.console](https://github.com/dcsync/pycobalt/tree/master/docs/console.md)
provides helpers for working with console output. This includes:

 - Registering console output modifiers (Aggressor's `set BEACON_OUTPUT`).
 - Helper functions for coloring and styling text.
 - Helper functions for creating ASCII tables and aligned text in the console.

### Output Modifiers

Here's how you register output modifiers:

    import pycobalt.engine as engine
    import pycobalt.console as console

    # this is case-insensitive
    @console.modifier('beacon_input')
    def _(bid, user, text, when):
        # the return text is what you'll see in the Beacon Console
        return user + '> ' + text

    engine.loop()

Output modifiers aren't officially documented. I attempted to document them
over at
[docs/console.md](https://github.com/dcsync/pycobalt/tree/master/docs/console.md).

As usual the arguments to your modifier callbacks are checked. If
they don't match an Exception will be printed to the Script Console and an
error message will be returned in place of your callback's return value.

Unlike alias, command, and event callbacks, output modifier callbacks are
called in Cobalt Strike's main thread. In order to avoid freezing up the entire
application PyCobalt will timeout and return/print an error if your callback
doesn't return within 8 seconds. You may modify this timeout by setting
[`$pycobalt_timeout`](#aggressor-configuration).

### Console Colors

This module also contains console color and style helpers. 

	...
	@aliases.alias('red', 'Print red text to the Beacon Console')
	def _(bid, red_text, plain_text=''):
		aggressor.blog2(bid, console.red(red_text) + plain_text)
	...

Alternatively you may use the escape codes directly:

	...
	@aliases.alias('red', 'Print red text to the Beacon Console')
	def _(bid, red_text, plain_text=''):
		aggressor.blog2(bid, console.codes['red'] + red_text + console.codes['reset'] + plain_text)
	...

There are a bunch of colors and styles. See
[docs/console.md](https://github.com/dcsync/pycobalt/tree/master/docs/console.md)
for the full list.

### PS Command Example

Inspired by the Shadow Brokers leak I set out to improve the output of my `ps`
command.

	beacon> ps
	...
    | PID  | PPID |          Name          |                  Description                   |     User     | Session |
    +------+------+------------------------+------------------------------------------------+--------------+---------+
    |    0 |    0 | [System Process]       | System Idle Process                            |              |         |
    |    4 |    0 |     System             | System Kernel                                  |              |         |
    |  260 |    4 |         smss           | Session Manager Subsystem                      |              |         |
    |  355 |  344 | csrss                  | Client-Server Runtime Server Subsystem         |              |         |
    |  418 |  344 | wininit                | Vista background service launcher              |              |         |
    |  519 |  418 |     services           | Windows Service Controller                     |              |         |
    |  201 |  519 |         svchost        | Microsoft Service Host Process (check path)    |              |         |
    |  300 |  519 |         svchost        | Microsoft Service Host Process (check path)    |              |         |
	...

The code
([`examples/ps.py`](https://github.com/dcsync/pycobalt/tree/master/examples/ps.py))
uses every feature in this module.

## GUI

[pycobalt.gui](https://github.com/dcsync/pycobalt/tree/master/docs/gui.md)
provides the ability to register menu trees.

The following menu tree pieces are supported:

  - popup
  - menu
  - item
  - insert_menu
  - separator

Here's an example using all of those:

    import pycobalt.engine as engine
    import pycobalt.gui as gui

    def beacon_top_callback(bids):
        engine.message('showing menu for: ' + ', '.format(bids))

    def node_sysadmin(bids):
        for bid in bids:
            aggressor.bnote(bid, 'sysadmin!')

    menu = gui.popup('beacon_top', callback=beacon_top_callback, children=[
        gui.menu('Note', children=[
            gui.insert_menu('note_top'),
            gui.item('sysadmin', callback=note_sysadmin),
            gui.separator(),
            gui.insert_menu('note_bottom'),
        ])
    ])
    gui.register(menu)

    engine.loop()

Callbacks are called before children are produced.

GUI registration must happen before `engine.loop()` is called. `engine.loop()`
creates a new thread in Cobalt Strike and trying to register callbacks for menus
created before that point (e.g. `beacon_top`) will result in a thread safety
exception within Java. It's not possible to register menus using the regular
Aggressor functions for the same reason.

The one downside to this is that you can't generate the menu labels dynamically
from within the menu callbacks.

## Bot

[pycobalt.bot](https://github.com/dcsync/pycobalt/blob/master/pycobalt/bot.py)
provides tools for creating Event Log bots.

For example:

    import pycobalt.bot as bot
    import pycobalt.engine as engine

    bot.set_prefix('!')
    bot.set_triggers(bot.PRIVMSG, bot.PREFIX, bot.ADDRESSED)
    bot.add_help()

    @bot.command('test-command', 'Tests bot')
    def _(*args):
        for arg in args:
            bot.say(arg)

    engine.loop()

Using the example:

    event> !help test-command
    10/19 10:21:01 <bot> test-command: Tests bot
    Syntax: test-command(*args)

    event> !test-command arg1 "arg 2" arg3
    10/19 10:24:13 <bot> arg1
    10/19 10:24:13 <bot> arg 2
    10/19 10:24:13 <bot> arg3

See
[examples/bot.py](https://github.com/dcsync/pycobalt/blob/master/examples/bot.py)
for more examples.

## Helpers

[pycobalt.helpers](https://github.com/dcsync/pycobalt/tree/master/docs/helpers.md)
contains helper functions and classes to make writing scripts easier. Here are
some of the functions available:

  - `parse_jobs(content)`: Parses the output of `bjobs` as returned by the
    `beacon_output_jobs` event. Returns a list of dictionaries. Each dictionary
    represents a job with the following fields: `jid` (job ID), `pid` (process
    ID), and `description`.
  - `parse_ps(content)`: Parses the callback output of `bps`. Returns a list of
    dictionaries. Each dictionary represents a process with the following
    fileds: `name`, `pid`, `ppid`, `arch` (if available), and `user` (if available).
  - `parse_ls(content)`: Parses the callback output of `bls`. Returns a list of
    dictionaries. Each dictionary represents a file with the following fields:
    `type` (D/F), `size` (in bytes), `modified` (date and time), and `name`.
  - `recurse_ls(bid, directory, callback, depth=9999)`: Recursively list files
    with `bls` and call `callback(path)` for each file.
  - `find_process(bid, proc_name, callback)`: Calls `bps` to find a process by
    name and calls `callback` with a list of matching processes (as returned
    by `parse_ps`).
  - `explorer_stomp(bid, file)`: Stomps a file timestamp with the modification
    time of explorer.exe.
  - `upload_to(bid, local_file, remote_file)`: Like `aggressor.bupload` but lets
    you specify the remote file path/name.
  - `powershell_quote(arg)`/`pq(arg)`: Quote a string for use as an argument to
    a Powershell function. Encloses in single quotation marks with internal
    quotation marks escaped.
  - `argument_quote(arg)`/`aq(arg)`: Quote a string for
    use as an argument to a cmd.exe command that uses `CommandLineToArgvW`.
    Read [this](https://stackoverflow.com/questions/29213106/how-to-securely-escape-command-line-arguments-for-the-cmd-exe-shell-on-windows).
  - `cmd_quote(arg)`/`cq(arg)`: Quote a string for use as an arguent to a
    cmd.exe command that does not use `CommandLineToArgvW`.
  - `powershell_base64(string)`: Encode a string as UTF-16LE and base64 it. The
    output is compatible with Powershell's -EncodedCommand flag.

### Argparse

There's a `helpers.ArgumentParser` class which extends
`argparse.ArgumentParser` to support printing to the Beacon Console, script
console, or Event Log. Here's an example using it with an alias:

    @aliases.alias('outlook', 'Retrieve an outlook folder', 'See `outlook -h`')
    def _(bid, *args):
        parser = helpers.ArgumentParser(bid=bid, prog='outlook')
        parser.add_argument('-f', '--folder', help='Folder name to grab')
        parser.add_argument('-s', '--subject', help='Match subject line (glob)')
        parser.add_argument('-t', '--top', metavar='N', type=int, help='Only show top N results')
        parser.add_argument('-d', '--dump', action='store_true', help='Get full dump')
        parser.add_argument('-o', '--out', help='Output file')
        try: args = parser.parse_args(args)
        except: return
        ...

In the Beacon Console:

    beacon> outlook -h
    [-] usage: outlook [-h] [-f FOLDER] [-s SUBJECT] [-t N] [-d] [-o OUT]
    
    optional arguments:
      -h, --help            show this help message and exit
      -f FOLDER, --folder FOLDER
                            Folder name to grab
      -s SUBJECT, --subject SUBJECT
                            Match subject line (glob)
      -t N, --top N         Only show top N results
      -d, --dump            Get full dump
      -o OUT, --out OUT     Output file

    beacon> outlook -z
    [-] unrecognized arguments: -z

To use `helpers.ArgumentParser` with the Event Log pass `event_log=True` to the
constructor. This is useful for creating [bots](#bot).

## SharpGen

[pycobalt.sharpgen](https://github.com/dcsync/pycobalt/tree/master/docs/sharpgen.md)
provides helpers for compiling and executing C# code with
[SharpGen](https://github.com/cobbr/SharpGen).

With the help of SharpGen I've managed to mostly replace PowerShell in my
personal Cobalt Strike setup. Read [this blog
post](https://cobbr.io/SharpGen.html) first if you're interested in using
SharpGen.

### Functions

The main functions are as follows:

  - `compile_file(source, ...)`: Compile a C# file. By default this creates a
                                 temporary output file and returns its name.
  - `compile(code, ...)`: Compile inline C# code. By default this creates a
                          temporary output file and returns its name.
  - `execute_file(bid, source, ...)`: Compile and execute a C# file.
  - `execute(bid, code, ...)`: Compile and execute inline C# code.

These functions have a large number of shared keyword arguments. See the
[module docs](https://github.com/dcsync/pycobalt/tree/master/docs/sharpgen.md)
for the full list.

### Examples

Here's a basic usage example:

    import pycobalt.sharpgen as sharpgen
    sharpgen.set_location('/root/tools/SharpGen')

    @aliases.alias('sharpgen-exec')
    def _(bid, code):
        sharpgen.execute(bid, code)

See
[examples/sharpgen.py](https://github.com/dcsync/pycobalt/tree/master/examples/sharpgen.py)
for example Script Console commands and Beacon Console aliases to go with each
compile/execute function (including a full version of `sharpgen-exec`).

This module is also pretty useful on its own, independent of Cobalt Strike.

### Build Cache

PyCobalt's SharpGen module includes an optional build cache. Using it is pretty
simple:

    import pycobalt.sharpgen as sharpgen
    sharpgen.enable_cache()

    @aliases.alias('sharpgen-exec')
    def _(bid, code, *args):
        from_cache = sharpgen.execute(bid, code, args)
        if from_cache:
            aggressor.blog2(bid, 'Build was executed from the cache')

The cache works by MD5 hashing your source code before it's compiled. When you
call `compile_file`, `compile`, `execute_file`, or `execute` with the cache
enabled PyCobalt will search the cache for your code's hash. If it finds the
hash it will return a cached build. Otherwise it will compile your code and add
a successful build to the cache.

By default the cache location will be a directory named `Cache` within your
SharpGen directory. You can change the cache location with the
`sharpgen.set_cache_location(<location>)` function.

You can enable or disable the cache for individual compilation calls by passing
`cache=True` or `cache=False` respectively. To force an overwrite of a cached
build you may pass `overwrite_cache=True`.

To clear the entire cache call `sharpgen.clear_cache()`.

There are other caching-related functions. You'll need to read the [module
docs](https://github.com/dcsync/pycobalt/tree/master/docs/sharpgen.md) or [the
code](https://github.com/dcsync/pycobalt/tree/master/pycobalt/sharpgen.py) for
more info.

### Setting up SharpGen

You need a compiled version of SharpGen to use this module. By default it
points to the repo copy (`pycobalt/third_party/SharpGen`) which is a Git
submodule of [github.com/cobbr/SharpGen](https://github.com/cobbr/SharpGen).
To use it you'll need to initialize and build it first. To do that run:

    git submodule init
    git submodule update
    cd third_party/SharpGen
    dotnet build

You can use your own copy of SharpGen by calling `sharpgen.set_location('<your
copy>')` or by passing it on the `sharpgen_location=` parameter to any of the
four compile/execute functions.

## Advanced Usage

### Aggressor Configuration

The PyCobalt Aggressor scripts are configurable with some variables.

Configuration variables for `pycobalt.cna`:

 - `$pycobalt_path`: Directory containing `pycobalt.cna` (default: `script_resource()`)
 - `$pycobalt_python`: Location of the Python interpreter (default: `"/usr/bin/env python3"`)
 - `$pycobalt_debug_on`: Enable debug messages (boolean, default: `false`)
 - `$pycobalt_timeout`: Global timeout value in milliseconds to use for various
                        operations (default: `8000`)

Configuration variables for `json.cna`:

 - `$json_path`: Directory containing `json.cna` (default: `$pycobalt_path`)
 - `$json_jar_file`: Full file path of `json.jar` (default: `$json_path . '/jars/json.jar'`)

### Non-Primitive Objects

When passed from Cobalt Strike to Python a non-primitive object's reference is
stored. A string identifying this stored reference is passed to Python (let's
call it a "serialized reference"). When passed back to Cobalt Strike the
serialized reference is deserialized back into the original object reference.

Non-primitive objects are effectively opaque on the Python side.

This also means there's a global reference to every non-primitive object
sitting around. To save memory PyCobalt allows you to remove an object's global
reference after you're finished referencing it:

    ...
    dialog = aggressor.dialog('Test dialog', {}, callback)
    ...
    aggressor.dialog_show(dialog)
    engine.delete(dialog)

I figure passing serialized references around is better than serializing entire
Java objects. There's a Python library called javaobj which supports
serializing and deserializing Java objects. It doesn't work well with complex
Java objects though.

### Sleep Functions

You can call arbitrary [Sleep](http://sleep.dashnine.org/manual/index.html) and
[Aggressor](https://www.cobaltstrike.com/aggressor-script/functions.html)
functions (including your own Aggressor functions) like this:

    engine.call('printAll', [['a', 'b', 'c']])

Which turns into:

    printAll(@('a', 'b', 'c'))

To call a Sleep function in its own thread without getting its return value:

    engine.call('println', args=['printing from another thread'], fork=True)

You can also eval arbitrary Sleep code:

    engine.eval('println("foo")')

`engine.eval` doesn't perform any sort of parameter marshalling or callback
serialization.

### Installation

#### Python Side

Run `setup.py install` to install the PyCobalt python library.

Or you can run it straight out of the repo if you're familiar with
[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH).

#### Cobalt Strike Side

The Aggressor library is in the
[aggressor](https://github.com/dcsync/pycobalt/tree/master/aggressor)
directory. It's also installed by `setup.py` at
`/usr/lib/python-*/site-packages/pycobalt-*/aggressor`.

You can include pycobalt.cna straight out of the repo. It comes with its
dependencies and all.

PyCobalt depends on the
[org.json](https://mvnrepository.com/artifact/org.json/json) Java library. A
copy is included in this repo at
[aggressor/jars/json.jar](https://github.com/dcsync/pycobalt/tree/master/aggressor/jars).
You can optionally replace `json.jar` with a more trusted copy. It's PyCobalt's
only binary dependency.
