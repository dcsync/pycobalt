#!/bin/bash
# Check a script to make sure it runs correctly.

script=$1
timeout=5

if ! timeout $timeout grep -m1 -q '"name": "fork"' <("$script") ; then
	echo "script didn't call engine.fork() within $timeout seconds"
else
	echo 'script looks good!'
fi
