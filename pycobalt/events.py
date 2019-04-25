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

_official_events = (
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
    'beacons',
    'any',

    # heartbeats
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

    # data model
    'applications',
    'archives',
    'beacons',
    'credentials',
    'downloads',
    'keystrokes',
    'screenshots',
    'services',
    'sites',
    'socks',
    'targets',
)

import collections

import pycobalt.utils as utils
import pycobalt.engine as engine
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks

def is_official(name):
    """
    Check if an event is one of the official cobaltstrike ones

    :param name: Name of event
    :return: True if event is an official one
    """

    global _official_events
    return name in _official_events

def register(name, callback, official_only=True):
    """
    Register an event callback.

    :param name: Name of event
    :param callback: Event callback
    :param official_only: Only allow official callbacks
    :return: Name of registered callback
    """

    def event_callback(*args):
        engine.debug('calling callback for event {}'.format(name))
        callback(*args)

    if official_only and not is_official(name):
        raise RuntimeError('Tried to register an unofficial event: {name}. Try events.event("{name}", official_only=False).'.format(name=name))

    callback_name = callbacks.register(event_callback, prefix='event_{}'.format(name))
    aggressor.on(name, event_callback)
    return callback_name

def unregister(callback):
    """
    Unregister an event callback. There's no way to unregister an event with
    aggressor so this will forever leave us with broken callbacks coming back
    from the teamserver.

    :param callback: Callback to unregister
    :return: Name of unregistered callback
    """

    return callbacks.unregister(callback)

class event:
    """
    Decorator for event registration
    """

    def __init__(self, name, official_only=True):
        """
        :param name: Name of event
        :param official_only: Only allow official callbacks
        """

        self.name = name
        self.official_only = official_only

    def __call__(self, func):
        self.func = func
        register(self.name, self.func, official_only=self.official_only)
