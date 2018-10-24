#!/usr/bin/env python3

import time

import communicate
import engine
import events
import commands
import aliases
import aggressor

# Event test
@events.event('event_action')
def event_action(who, contents, time):
    communicate.message('event callback test {} - {} - {}'.format(who, contents, time))

    targets = aggressor.targets()
    communicate.message('received {} targets'.format(len(targets)))

# Command test
@commands.command('test_command')
def test_command():
    communicate.message('command called')

# Alias test
@aliases.alias('test_alias')
def test_alias(bid):
    aggressor.blog(bid, 'alias called for beacon: {}'.format(bid))

# Message test
communicate.message('test message')

# For testing the error handling on the cobalt strike side
#raise RuntimeError('exception test')

engine.loop()
