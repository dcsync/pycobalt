pycobalt
========

PyCobalt is a Python API for Cobalt Strike.

usage
=====

PyCobalt comes in two parts: a Python library and an Aggressor library. The
Python library provides an API which allows Python scripts to call Aggressor
functions and register aliases, commands, and event handlers. The Aggressor
library runs your Python scripts and performs actions on their behalf.

python side
-----------

A Python script for PyCobalt generally looks like this:

	#!/usr/bin/env python3

    import pycobalt.engine as engine

    # prints to the script console
    engine.message('script console message')

	# loop over all beacons
	for beacon in aggressor.beacons():
		# and write to each beacon's console
		aggressor.blog2(beacon['bid'], 'example script')

    # must be called last
    engine.loop()

`engine.loop()` tells PyCobalt to read commands from Cobalt Strike. It's
technically only necessary if your script uses callbacks (for aliases,
events, etc).

PyCobalt uses stdout and stdin to communicate with Cobalt Strike. Try not to
write to stdout (`print`) or read from stdin (`input`) in a PyCobalt
script.

If your script has parser errors Cobalt Strike won't show anything in the script
console. Fatal runtime exceptions will show up in the script console.

PyCobalt includes the following modules:

  - [engine.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/engine.py): main communication code
  - [aggressor.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/aggressor.py): stubs for calling aggressor functions
  - [aliases.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/aliases.py): for beacon console alias registration
  - [commands.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/commands.py): for script console command registration
  - [events.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/events.py): for event handler registration
  - [gui.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/gui.py): for context menu registration
  - [helpers.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/helpers.py):
    assorted helper functions and classes to make writing scripts easier

Head over to the [examples](#examples) section for more information about each module.

cobalt strike side
------------------

An aggressor script for PyCobalt generally looks like this:

	$pycobalt_path = '/root/tools/pycobalt/aggressor';
	include($pycobalt_path . '/pycobalt.cna');
	python(script_resource('my_script.py'));

It's necessary to set the `$pycobalt_path` variable so that PyCobalt can find
its dependencies.

installation
============

python side
-----------

Run `setup.py install` to install the PyCobalt python library.

Or you can run it straight out of the repo if you're familiar with
[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH).

cobalt strike side
------------------

The aggressor library is in the
[aggressor](https://github.com/dcsync/pycobalt/tree/master/aggressor)
directory. it's also installed by `setup.py` at
`/usr/lib/python-*/site-packages/pycobalt-*/aggressor`.

You can include pycobalt.cna straight out of there. It comes with its
dependencies and all. See the [usage](#usage) section for more info.

PyCobalt depends on the
[org.json](https://mvnrepository.com/artifact/org.json/json) java library. a
copy is included in this repo at
[aggressor/jars/json.jar](https://github.com/dcsync/pycobalt/tree/master/aggressor/jars).
You can optionally replace `json.jar` with a more trusted copy.

examples
========

Here are some script examples. For more complete examples see the
[examples](https://github.com/dcsync/pycobalt/tree/master/examples) directory.

script console
--------------

To print a message on the script console:

    import pycobalt.engine as engine

    engine.message('test message')

    engine.loop()

To print an error message on the script console:

    import pycobalt.engine as engine

    engine.message('test message')

    engine.loop()

To print an debug message to the script console:

    import pycobalt.engine as engine

    engine.enable_debug()
    engine.debug('debug message')

    engine.loop()

aggressor functions
-------------------

Calling an aggressor function:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    for beacon in aggressor.beacons():
        engine.message(beacon['user'])

    engine.loop()

Calling an aggressor function with a callback:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    def my_callback(bid, results):
        aggressor.blog2(bid, 'ipconfig: ' + results)

    for beacon in aggressor.beacons():
        bid = beacon['bid']
        aggressor.bipconfig(bid, my_callback)

    engine.loop()

Calling an aggressor function without printing tasking information to the
beacon console (`!` operator):

    ...
    aggressor.bshell(bid, 'whoami', silent=True)
    ...

For notes on using non-primitive objects such as dialog objects see the
[non-primitive objects](#non-primitive-objects).

aliases
-------

Registering an alias:

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
    
    Python syntax: test_alias(bid)

Or you can specify it yourself:

    ...
    @aliases.alias('test_alias', short_help='Tests alias registration', long_help='Test alias\n\nLong help')
    ...

When the alias is called its arguments will be automagically checked against the
arguments of the python function. For example:

    beacon> test_alias foo
    [-] Syntax: test_alias(bid)

To bypass this you can use python's `*` operator:

    import pycobalt.engine as engine
    import pycobalt.aliases as aliases
    import pycobalt.aggressor as aggressor

    @aliases.alias('test_alias')
    def test_alias(bid, *args):
        aggressor.blog2(bid, 'test alias called with args: ' + ', '.join(args))

    engine.loop()

If an unhandled exception occurs in your alias callback PyCobalt will catch it
and print the exception information to the beacon console. For example, while I
was writing the previous example I typed `engine.blog2()` instead of
`aggressor.blog2()` by accident and got this error:

    beacon> test_alias
    [-] Caught Python exception while executing alias 'test_alias': module 'pycobalt.engine' has no attribute 'blog2'
    [-] See Script Console for more details.

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

commands
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

events
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

gui
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
aggressor functions for the same reason.

non-primitive objects
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

helpers
-------

[helpers.py](https://github.com/dcsync/pycobalt/blob/master/pycobalt/helpers.py)
contains helper functions and classes to make writing scripts easier. Here's
the list so far:

  - `parse_ps(content)`: parses the callback output of `bps`. returns a list of
	dictionaries. each dictionary represents a process with all available
    information
  - `findprocess(bid, proc_name, callback)`: calls `bps` to find a process by
	name and calls `callback` with a list of matching processes (as returned
    by `parse_ps`)
  - `isAdmin(bid)`: checks if a beacon is SYSTEM or admin (as returned by
     `isadmin`)
  - `defaultListener()`: gets local listener with 'http' in its name or the
    first listener if there are none
  - `explorerstomp(bid, file)`: stomps a file timestamp with the modification
    time of explorer.exe
  - `uploadto(bid, local_file, remote_file)`: like `aggressor.bupload` but lets
    you specify the remote file path/name.

sleep functions
---------------

You can call arbitrary sleep and aggressor functions like this:

    engine.call('printAll', [['a', 'b', 'c']])

Which turns into:

    printAll(@('a', 'b', 'c'))

To call a sleep function in its own thread without getting its return value:

    engine.call('println', args=['printing from another thread'], fork=True)

You can also eval arbitrary sleep code:

    engine.eval('println("foo")')

`engine.eval` doesn't perform any sort of parameter marshalling or callback
serialization.
