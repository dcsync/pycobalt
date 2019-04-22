# pycobalt.events

For registering event callbacks

Regular example:

def test_event_action(who, contents, time):
engine.message('event callback test {} - {} - {}'.format(who, contents, time))
events.register('event_action', test_event_action)

Decorator example:

@events.event('event_action')
def test_event_action(who, contents, time):
engine.message('event callback test {} - {} - {}'.format(who, contents, time))

## is_official
```python
is_official(name)
```

Check if an event is one of the official cobaltstrike ones

**Arguments**:

- `name`: Name of event

**Returns**:

True if event is an official one

## register
```python
register(name, callback, official_only=True)
```

Register an event callback.

**Arguments**:

- `name`: Name of event
- `callback`: Event callback
- `official_only`: Only allow official callbacks

**Returns**:

Name of registered callback

## unregister
```python
unregister(callback)
```

Unregister an event callback. There's no way to unregister an event with
aggressor so this will forever leave us with broken callbacks coming back
from the teamserver.

**Arguments**:

- `callback`: Callback to unregister

**Returns**:

Name of unregistered callback

## event
```python
event(self, name, official_only=True)
```

Decorator for event registration

