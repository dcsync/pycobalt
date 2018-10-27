pycobalt
========

pycobalt is a python api for cobaltstrike.

installation
============

pycobalt comes in two parts: a python library and an aggressor library for
cobaltstrike. these libraries communicate with each other.

python side
-----------

run `setup.py install` to install the pycobalt python library.

or you can run it straight out of the repo if you're familiar with `PYTHONPATH`.

cobaltstrike side
-----------------

the aggressor library is in the `aggressor` directory. it's also installed by
`setup.py` at `/usr/lib/python-*/site-packages/pycobalt-*/aggressor`.

you can include pycobalt.cna straight out of there. it comes with its
dependencies and all. see [usage](#usage) for more info.

pycobalt depends on the
[`org.json`](https://mvnrepository.com/artifact/org.json/json) java library. a
copy is included in the repo at `aggressor/jars/json.jar`. you don't have to
install anything to use it but feel feel to replace the jar. I got the copy in
this repo from
[ANGRYPUPPY](https://github.com/vysec/ANGRYPUPPY/tree/master/json) so if it's
backdoored you can blame vysec.

usage
=====

cobaltstrike side
-----------------

an aggressor script for pycobalt generally looks like this:

	$pycobalt_path = '/root/tools/pycobalt/aggressor';
	include($pycobalt_path . '/pycobalt.cna');
	python(script_resource('my_script.py'));

it's necessary to set the `$pycobalt_path` variable so that pycobalt can find
its dependencies.

python side
-----------

a python script for pycobalt generally looks like this:

	#!/usr/bin/env python3

    import pycobalt.engine as engine

    # prints to the script console
    engine.message('script console message')

    # must be called last
    engine.loop()

`engine.loop()` tells pycobalt to read commands from cobaltstrike. it's
technically only necessary if your script uses callbacks (includes for aliases,
events, etc).

pycobalt uses stdout and stdin to communicate with cobaltstrike. try not to
print to stdout (e.g. `print`) or read from stdin (e.g. `input) in a pycobalt
script.

if your script has parser errors cobaltstrike won't show anything in the script
console. fatal runtime exceptions will show up in the script console.

pycobalt includes the following modules:

  - `engine.py`: main communication code
  - `aggressor.py`: contains stubs for calling aggressor functions
  - `aliases.py`: for beacon console alias registration
  - `commands.py`: for script console command registration
  - `events.py`: for event handler registration
  - `gui.py`: for context menu registration
  - `helpers.py`: assorted helper functions and classes to make writing scripts
     easier

for more information about each see the [examples](#examples) section.

examples
========

script console
--------------

to print a message on the script console:

    import pycobalt.engine as engine

    engine.message('test message')

    engine.loop()

to print an error message on the script console:

    import pycobalt.engine as engine

    engine.message('test message')

    engine.loop()

to print an debug message to the script console:

    import pycobalt.engine as engine

    engine.enable_debug()
    engine.debug('debug message')

    engine.loop()

aggressor functions
-------------------

calling an aggressor function:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    for beacon in aggressor.beacons():
        engine.message(beacon['user'])

    engine.loop()

calling an aggressor function with a callback:

    import pycobalt.engine as engine
    import pycobalt.aggressor as aggressor

    def my_callback(bid, results):
        aggressor.blog2(bid, 'ipconfig: ' + results)

    for beacon in aggressor.beacons():
        bid = beacon['bid']
        aggressor.bipconfig(bid, my_callback)

    engine.loop()

calling an aggressor function without printing tasking information to the
beacon console (`!` operator):

    ...
    aggressor.bshell(bid, 'whoami', silent=True)
    ...

aliases
-------

registering an alias:

    import pycobalt.engine as engine
    import pycobalt.aliases as aliases
    import pycobalt.aggressor as aggressor

    @aliases.alias('test_alias')
    def test_alias(bid):
        aggressor.blog2(bid, 'test alias called')

    engine.loop()

registering an alias with help info:

    ...
    @aliases.alias('test_alias', short_help='Tests alias registration')
    ...

by default the long help will be based on the short help and python function
syntax. for example:

    beacon> help test_alias
    Tests alias registration
    
    Python syntax: test_alias(bid)

or you can specify it yourself:

    ...
    @aliases.alias('test_alias', short_help='Tests alias registration', long_help='Test alias\n\nLong help')
    ...

when the alias is called its arguments will be automagically checked against the
arguments of the python function. for example:

    beacon> test_alias foo
    [-] Syntax: test_alias(bid)

to bypass this you can use python's `*` operator:

    import pycobalt.engine as engine
    import pycobalt.aliases as aliases
    import pycobalt.aggressor as aggressor

    @aliases.alias('test_alias')
    def test_alias(bid, *args):
        aggressor.blog2(bid, 'test alias called with args: ' + ', '.join(args))

    engine.loop()

if an unhandled exception occurs in your alias callback pycobalt will catch it
and print the exception information to the beacon console. for example, while I
was writing the previous example I typed `engine.blog2()` instead of
`aggressor.blog2()` by accident and got this error:

    beacon> test_alias
    [-] Caught Python exception while executing alias 'test_alias': module 'pycobalt.engine' has no attribute 'blog2'
    [-] See Script Console for more details.

in the script console:

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

script console commands are similar to beacon console aliases.

    import pycobalt.engine as engine
    import pycobalt.commands as commands

    @commands.command('test_command')
    def test_command():
        engine.message('test_command called')

    engine.loop()

error handling and argument checking is similar. error messages are printed to
the script console.

events
------

registering an event handler:

    import pycobalt.engine as engine
    import pycobalt.events as events

    @events.event('beacon_initial')
    def beacon_initial_handler(bid):
        aggressor.bnote(bid, 'fresh')

    engine.loop()

this will check to make sure the event is one of the official cobaltstrike
ones. to register an arbitrary event (e.g. for use with `fireEvent`):

    ...
    @events.event('myevent', official_only=False)
    ...

gui
---

the following menu tree pieces are supported:

  - popup
  - menu
  - item
  - insert_menu
  - separator

here's an example using all of those:

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

callbacks are called before children are produced.

gui registration must happen before `engine.loop()` is called. `engine.loop()`
creates a new thread in cobaltstrike and trying to register callbacks for menus
created before that point (e.g. `beacon_top`) will result in a thread safety
exception within Java. it's not possible to register menus using the regular
aggressor functions for the same reason.

helpers
-------

`helpers.py` contains helper functions and classes to make writing scripts
easier. here's the list so far:

  - `parse_ps(content)`: parses the callback output of `bps`. returns a list of
    dictionaries, each representing a process with all available information
  - `findprocess(bid, proc_name, callback): calls `bps` to find a process by
	its name and calls `callback` with a list of found processes (as returned
    by `parse_ps`)
  - `isAdmin(bid)`: checks if a beacon is SYSTEM or admin (as returned by
     `isadmin`)
  - `defaultListener()`: gets local listener with 'http' in its name or the
    first listener if there are none
  - `explorerstomp(bid, file)`: stomps a file timestamp with the modification
    time of explorer.exe
  - `uploadto(bid, local_file, remote_file)`: like `bupload` but lets you
    specify the remote file path/name.

sleep functions
---------------

you can call arbitrary sleep and aggressor functions like so:

    engine.call('printAll', args=[['a', 'b', 'c']])

this turns into:

    printAll(@('a', 'b', 'c'))

to call a sleep function in its own thread without getting its return value:

    engine.call('println', args=['printing from another thread'], fork=True)

you can also eval arbitrary sleep code:

    engine.eval('println("foo")')

`engine.eval` does not perform any sort of parameter marshalling or callback
serialization.

hack the planet.
