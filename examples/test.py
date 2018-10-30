#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import utils
sys.path.insert(0, utils.basedir('..'))

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.commands as commands
import pycobalt.aliases as aliases
import pycobalt.aggressor as aggressor

# Event test
@events.event('event_action')
def event_action(who, contents, time):
    engine.message('event callback test {} - {} - {}'.format(who, contents, time))

    targets = aggressor.targets()
    engine.message('received {} targets'.format(len(targets)))

# Command test
@commands.command('test_command')
def test_command():
    engine.message('test_command called')

# Alias test
@aliases.alias('test_alias')
def test_alias(bid):
    aggressor.blog(bid, 'test_alias called for beacon: {}'.format(bid))

# Message test
engine.message('test message')

# For testing the error handling on the cobaltstrike side
#raise RuntimeError('exception test')

#import argparse
#@aliases.alias('test_alias')
#def test_alias(bid, *args):
#    parser = argparse.ArgumentParser()
#    parser.add_argument('-t', '--test', action='store_true',
#            help='argparse test')
#    try: parsed = parser.parse_args(args)
#    except: return
#
#    if parsed.test:
#        aggressor.blog2(bid, 'test alias called')

engine.loop()
