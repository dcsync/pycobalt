#!/bin/bash

{
	echo '{"name": "event", "message": {"name": "event_action", "args": ["a", "b", "c"]}}'
	echo '{"name": "command", "message": {"name": "test", "args": []}}'
	echo '{"name": "alias", "message": {"name": "test", "args": []}}'
} |
./test.py
