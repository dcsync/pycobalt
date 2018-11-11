#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)) + '/..')

import pycobalt.engine as engine
import pycobalt.aggressor as aggressor
import pycobalt.gui as gui

def setNotes(bids, note):
    """
    Set notes for multiple beacons
    """
    for bid in bids:
        aggressor.bnote(bid, note)

def main():
    note_items = []
    for note in ['domain &controller!', 'database!', '&using', 'keylogger',
                 'screenshotter', 'standby', 'sandbox', 'do not use',
                 'sysadmin', '!!!']:
        note_items.append(gui.item(note, callback=(lambda note: lambda bids: setNotes(bids, note.replace('&', '')))(note)))

    note_items.append(gui.separator())
    note_items.append(gui.item('&clear', callback=lambda bids: setNotes(bids, '')))

    menu = gui.popup('beacon_bottom', children=[
               gui.menu('&Note', children=note_items)
           ])

    gui.register(menu)

    engine.loop()

if __name__ == '__main__':
    main()
