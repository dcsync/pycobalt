"""
For registering event callbacks

Regular example:

    def test_event_action(who, contents, time):
        engine.message('event callback test {} - {} - {}'.format(who, contents, time))
    events.register('event_action', test_event_action)

Decorator example:

    @events.event('event_action')
    def test_event_action(who, contents, time):
        engine.message('event callback test {} - {} - {}'.format(who, contents, time))
"""

_supported_events = [
    'beacon_checkin',
    'beacon_error',
    'beacon_indicator',
    'beacon_initial',
    'beacon_initial_empty',
    'beacon_input',
    'beacon_mode',
    'beacon_output',
    'beacon_output_alt',
    'beacon_output_jobs',
    'beacon_output_ls',
    'beacon_output_ps',
    'beacon_tasked',
    'event_action',
    'event_beacon_initial',
    'event_join',
    'event_newsite',
    'event_notify',
    'event_nouser',
    'event_private',
    'event_public',
    'event_quit',
    'keylogger_hit',
    'profiler_hit',
    'ready',
    'sendmail_done',
    'sendmail_post',
    'sendmail_pre',
    'sendmail_start',
    'ssh_checkin',
    'ssh_error',
    'ssh_indicator',
    'ssh_initial',
    'ssh_input',
    'ssh_output',
    'ssh_output_alt',
    'ssh_tasked',
    'web_hit',
    'any',
    'beacons',
    'heartbeat_10m',
    'heartbeat_10s',
    'heartbeat_15s',
    'heartbeat_1m',
    'heartbeat_1s',
    'heartbeat_20m',
    'heartbeat_30m',
    'heartbeat_30s',
    'heartbeat_5m',
    'heartbeat_5s',
    'heartbeat_60m',
]

import collections

import pycobalt.utils as utils
import pycobalt.engine as engine
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks

def supported(name):
    """
    Check if an event is one of the official cobaltstrike ones
    """

    global _supported_events
    return name in _supported_events
    #raise RuntimeError('tried to register unsupported event: {}'.format(name))

def register(name, callback):
    """
    Register an event callback.
    """

    def event_callback(*args):
        engine.debug('calling callback for event {}'.format(name))
        callback(*args)

    callbacks.register(event_callback, prefix='event_{}'.format(name))
    aggressor.on(name, event_callback)

class event:
    """
    Decorator
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        self.func = func
        register(self.name, self.func)
