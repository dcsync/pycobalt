#!/usr/bin/env python3

import time

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
    engine.message('command called')

# Alias test
@aliases.alias('test_alias')
def test_alias(bid):
    aggressor.blog(bid, 'alias called for beacon: {}'.format(bid))

# Message test
engine.message('test message')

# For testing the error handling on the cobalt strike side
#raise RuntimeError('exception test')

engine.loop()
