#!/bin/bash

docs=docs
main_module=pycobalt
modules=(
aggressor
aliases
bot
callbacks
commands
engine
events
gui
helpers
serialization
sharpgen
)
level='+'

mkdir -p $docs

for module in ${modules[@]} ; do
	markdown=$docs/$module.md

	echo "Generating pydoc for $module at $markdown"
	pydocmd simple "$main_module.$module$level" > $markdown &
done
