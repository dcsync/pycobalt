#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)) + '/..')

def set_notes(bids, note):
    """
    Set notes for multiple beacons
    """
    for bid in bids:
        aggressor.bnote(bid, note)

def main():
    note_items = []
    for note in ['domain &controller!', 'database!', '&using', 'keylogger',
                 'screenshotter', 'standby', 'sandbox', 'dead', 'new', 'do not use',
                 'sysadmin', '!!!']:
        note_items.append(gui.item(note, callback=(lambda note: lambda bids: set_notes(bids, note.replace('&', '')))(note)))

    note_items.append(gui.separator())
    note_items.append(gui.item('&clear', callback=lambda bids: set_notes(bids, '')))

    menu = gui.popup('beacon_bottom', children=[
               gui.menu('&Note', children=note_items)
           ])

    gui.register(menu)

    engine.loop()

if __name__ == '__main__':
    main()
