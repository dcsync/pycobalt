PyCobalt
========

PyCobalt is a Python API for Cobalt Strike.

Usage
=====

PyCobalt comes in two parts: a Python library and an Aggressor library.

Python Side
-----------

A Python script for PyCobalt looks like this:

    #!/usr/bin/env python3

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor
    import pycobalt.aliases as aliases

	# register this function as a beacon console alias
    @aliases.alias('example-alias')
    def example_alias(bid):
        aggressor.blog2(bid, 'example alias')

    # read commands from cobaltstrike. must be called last
    engine.loop()

`engine.loop()` tells PyCobalt to read commands from Cobalt Strike. It's
only necessary if your script uses callbacks (for aliases, events, etc).

Fatal runtime exceptions and Python parser errors will show up in the script
console.

PyCobalt includes the following modules:

  - [engine.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/engine.py): Main communication code
  - [aggressor.py](#aggressor): Stubs for calling Aggressor functions
  - [aliases.py](#aliases): Beacon console alias registration
  - [commands.py](#commands): Script console command registration
  - [events.py](#events): Event handler registration
  - [gui.py](#gui): Context menu registration
  - [bot.py](#bot): Event Log bot toolkit
  - [helpers.py](#helpers):
    Assorted helper functions and classes to make writing scripts easier
  - [sharpgen.py](#sharpgen):
	Helper functions for using [SharpGen](https://github.com/cobbr/SharpGen) with Cobalt Strike

Head over to the [examples](#examples) section for more information about each module.

Cobalt Strike Side
------------------

An Aggressor script for PyCobalt looks like this:

    $pycobalt_path = '/root/tools/pycobalt/aggressor';
    include($pycobalt_path . '/pycobalt.cna');
    python(script_resource('my_script.py'));

It's necessary to set the `$pycobalt_path` variable so that PyCobalt can find
its dependencies.

Installation
============

Python Side
-----------

Run `setup.py install` to install the PyCobalt python library.

Or you can run it straight out of the repo if you're familiar with
[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH).

Cobalt Strike Side
------------------

The Aggressor library is in the
[aggressor](https://github.com/dcsync/pycobalt/tree/master/aggressor)
directory. it's also installed by `setup.py` at
`/usr/lib/python-*/site-packages/pycobalt-*/aggressor`.

You can include pycobalt.cna straight out of there. It comes with its
dependencies and all. See the [usage](#usage) section for more info.

PyCobalt depends on the
[org.json](https://mvnrepository.com/artifact/org.json/json) Java library. A
copy is included in this repo at
[aggressor/jars/json.jar](https://github.com/dcsync/pycobalt/tree/master/aggressor/jars).
You can optionally replace `json.jar` with a more trusted copy. It's PyCobalt's
only binary dependency.

Examples
========

Here are some script examples. For more complete examples see the
[examples](https://github.com/dcsync/pycobalt/tree/master/examples) directory.

Script Console
--------------

To print a message on the script console:

    import pycobalt.engine as engine

    engine.message('test message')

This shows up in the script console as:

    [pycobalt example.py] test message

To print an error message on the script console:

    import pycobalt.engine as engine

    engine.error('test error')

This shows up in the script console as:

    [pycobalt example.py error] test error

To print debug messages to the script console:

    import pycobalt.engine as engine

    engine.enable_debug()
    engine.debug('debug message 1')
    engine.debug('debug message 2')
    engine.disable_debug()
    engine.debug('debug message 3')

This shows up in the script console as:

    [pycobalt example.py debug] debug message 1
    [pycobalt example.py debug] debug message 2

To print raw stuff to the script console you can just call the Aggressor print
functions:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    aggressor.println('raw message')

Aggressor
---------

Calling an Aggressor function:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    for beacon in aggressor.beacons():
        engine.message(beacon['user'])

Calling an Aggressor function with a callback:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    def my_callback(bid, results):
        aggressor.blog2(bid, 'ipconfig: ' + results)

    for beacon in aggressor.beacons():
        bid = beacon['bid']
        aggressor.bipconfig(bid, my_callback)

    engine.loop()

Calling an Aggressor function without printing tasking information to the
beacon console (`!` operator, only supported by certain functions):

    ...
    aggressor.bshell(bid, 'whoami', silent=True)
    ...

For notes on using non-primitive objects such as dialog objects see the
[non-primitive objects](#non-primitive-objects) section.

Aliases
-------

Registering a beacon console alias:

    import pycobalt.engine as engine
    import pycobalt.aliases as aliases
    import pycobalt.aggressor as aggressor

    @aliases.alias('test_alias')
    def test_alias(bid):
        aggressor.blog2(bid, 'test alias called')

    engine.loop()

Registering an alias with help info:

    ...
    @aliases.alias('test_alias', short_help='Tests alias registration')
    ...

By default the long help will be based on the short help and python function
syntax. For example:

    beacon> help test_alias
    Tests alias registration
    
    Syntax: test_alias

Or you can specify the long help yourself:

    ...
    @aliases.alias('test_alias', 'Tests alias registration', 'Test alias\n\nLong help')
    ...

When the alias is called its arguments will be automagically checked against the
arguments of the python function. For example:

    beacon> test_alias foo
    [-] Syntax: test_alias

To bypass this you can use python's `*` operator:

    import pycobalt.engine as engine
    import pycobalt.aliases as aliases
    import pycobalt.aggressor as aggressor

    @aliases.alias('test_alias')
    def test_alias(bid, *args):
        aggressor.blog2(bid, 'test alias called with args: ' + ', '.join(args))

    engine.loop()

This also allows you to use Python's argparse with aliases. For more
information about using argparse see the [helpers](#helpers) section.

If an unhandled exception occurs in your alias callback PyCobalt will catch it
and print the exception information to the beacon console. For example, while I
was writing the previous example I typed `engine.blog2()` instead of
`aggressor.blog2()` by accident and got this error:

    beacon> test_alias
    [-] Caught Python exception while executing alias 'test_alias': module 'pycobalt.engine' has no attribute 'blog2'
        See Script Console for more details.

In the script console:

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

Commands
--------

Script console commands are similar to beacon console aliases.

    import pycobalt.engine as engine
    import pycobalt.commands as commands

    @commands.command('test_command')
    def test_command():
        engine.message('test_command called')

    engine.loop()

Error handling and argument checking is similar. Error messages are printed to
the script console.

Events
------

Registering an event handler:

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

GUI
---

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

Bot
---

[bot.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/bot.py)
provides tools for registering Event Log bot commands.

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

Helpers
-------

[helpers.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/helpers.py)
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

There's a `helpers.ArgumentParser` class which extends
`argparse.ArgumentParser` to support printing to the beacon console, script
console, or event log. Here's an example using it with an alias:

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

In the beacon console:

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

To use `helpers.ArgumentParser` with the event log pass `event_log=True` to the
constructor. This is useful for creating bots.

SharpGen
--------

[sharpgen.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/helpers.py)
provides helpers for compiling and executing C# code with
[SharpGen](https://github.com/cobbr/SharpGen). It provides the following functions:

  - `compile_file(source, ...)`: Compile a C# file. By default this creates a
                                 temporary output file and returns its name.
  - `compile(code, ...)`: Compile inline C# code. By default this creates a
                          temporary output file and returns its name.
  - `execute_file(bid, source, ...)`: Compile and execute a C# file.
  - `execute(bid, code, ...)`: Compile and execute inline C# code.

These functions have a number of shared keyword arguments. See the
[`compile_file`](https://github.com/dcsync/pycobalt/blob/master/pycobalt/sharpgen.py#L83)
function's pydoc for the full list.

You need a compiled version of SharpGen to use this module. By default it
points to the repo copy (`pycobalt/third_party/SharpGen`). You can use that copy
but it's a Git submodule so you'll need to initialize and build it first. To do
that run:

    git submodule init
    git submodule update
    cd third_party/SharpGen
    dotnet build

You can use your own copy of SharpGen by calling `sharpgen.set_location('<your
copy>')` or by passing it on the `sharpgen_location=` parameter to any of the
four compile/execute functions.

Here's a basic usage example:

    import pycobalt.sharpgen
    sharpgen.set_location('/root/tools/SharpGen')

    @aliases.alias('sharpgen-exec')
    def _(bid, code):
        sharpgen.execute(bid, code)

See
[examples/sharpgen.py](https://github.com/dcsync/pycobalt/tree/master/examples/sharpgen.py)
for console commands and beacon aliases to go with each compile/execute function.

Non-Primitive Objects
---------------------

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

Sleep Functions
---------------

You can call arbitrary Sleep and Aggressor functions (including your own
Aggressor functions) like this:

    engine.call('printAll', [['a', 'b', 'c']])

Which turns into:

    printAll(@('a', 'b', 'c'))

To call a Sleep function in its own thread without getting its return value:

    engine.call('println', args=['printing from another thread'], fork=True)

You can also eval arbitrary Sleep code:

    engine.eval('println("foo")')

`engine.eval` doesn't perform any sort of parameter marshalling or callback
serialization.
