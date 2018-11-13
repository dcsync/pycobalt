#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)) + '/..')

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.aliases as aliases
import pycobalt.helpers as helpers
import pycobalt.commands as commands
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.sharpgen as sharpgen

@aliases.alias('sharpgen-execute', 'Execute C# code using SharpGen')
def _(bid, code, *args):
    aggressor.btask(bid, 'Tasked beacon to execute C# code: {}'.format(code))
    try:
        sharpgen.execute(bid, code, *args)
    except RuntimeError as e:
        aggressor.berror(bid, 'SharpGen failed. See script console for more details')

@aliases.alias('sharpgen-execute-file', 'Execute C# code from a file using SharpGen')
def _(bid, source, *args):
    aggressor.btask(bid, 'Tasked beacon to execute C# code from: {}'.format(source))
    try:
        sharpgen.execute_file(bid, source, *args)
    except RuntimeError as e:
        aggressor.berror(bid, 'SharpGen failed. See script console for more details')

# Compile C# code using SharpGen
@commands.command('sharpgen-compile')
def _(code, out, *args):
    engine.message('Compiling C# code: {}'.format(code))
    try:
        sharpgen.compile(code, out=out, additional_options=args)
        engine.message('All finished! Output is in: {}'.format(out))
    except RuntimeError as e:
        engine.error('SharpGen failed. See above for more details')

# Compile C# code from file using SharpGen
@commands.command('sharpgen-compile-file')
def _(source, out, *args):
    engine.message('Compiling C# code from: {}'.format(source))
    try:
        sharpgen.compile_file(source, out=out, additional_options=args)
        engine.message('All finished! Output is in: {}'.format(out))
    except RuntimeError as e:
        engine.error('SharpGen failed. See above for more details')

engine.loop()
