#!/bin/bash

docs=docs
main_module=pycobalt
modules=(
	aggressor
	aliases
	callbacks
	commands
	engine
	events
	gui
	helpers
	sharpgen
	console
	#bot
)
level='+'
preprocessor=pydocmd.restructuredtext.Preprocessor

mkdir -p $docs

for module in ${modules[@]} ; do
	markdown=$docs/$module.md

	echo "Generating pydoc for $module at $markdown"
	pydocmd simple -c "preprocessor=$preprocessor" "$main_module.$module$level" > $markdown
done
