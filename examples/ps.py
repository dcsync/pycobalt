#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)) + '/..')

import re
import textwrap
import datetime
import collections
import copy
import time

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.aliases as aliases
import pycobalt.helpers as helpers
import pycobalt.commands as commands
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.console as console

import utils

# file containing process descriptions
elist_file = utils.basedir('elist.txt')

# optional: log unknown processes to a file
unknowns_file = None

def shadowbrokers_executables():
    """
    Get list of .exe descriptions from the Shadow Brokers leak.

    :return: Dictionary with executable name as key and description as value
    """

    apps = {}
    with open(elist_file, 'r') as fp:
        for line in fp:
            exe, desc = line.split('\t')
            exe = exe.lower().strip()
            apps[exe] = desc.strip()

    return apps

process_descriptions = shadowbrokers_executables()
browsers = (
    'chrome',
    'chromium',
    'firefox',
    'iexplore',
    'MicrosoftEdge',
    'opera'
)

@console.modifier('beacon_output_ps')
def _(bid, content, when):
    procs = helpers.parse_ps(content)

    def get_children(pid):
        ret = []
        for proc in procs:
            if proc['ppid'] == pid and proc['pid'] != pid:
                ret.append(proc)
        return ret

    def get_trunks(procs):
        all_pids = [proc['pid'] for proc in procs]
        ret = []
        for proc in procs:
            if proc['ppid'] not in all_pids or proc['ppid'] == proc['pid']:
                ret.append(proc)
        return ret

    def make_tree(proc, indent=0, our_children=False):
        # are we in our beacon's process tree?
        if proc['pid'] == int(aggressor.beacon_info(bid, 'pid')):
            our_children = True

        # output proc info
        proc = copy.copy(proc)

        # add app description
        exe = proc['name'].lower()
        if exe in process_descriptions:
            proc['description'] = process_descriptions[exe]
        else:
            # write unknowns to a file
            if unknowns_file:
                if os.path.isfile(unknowns_file):
                    with open(unknowns_file, 'r') as fp:
                        names = set([line.strip() for line in fp])
                else:
                    names = set()

                names.add(proc['name'])

                with open(unknowns_file, 'w+') as fp:
                    fp.write('\n'.join(sorted(names)))

        # clean up name
        if proc['name'].lower().endswith('.exe'):
            proc['clean_name'] = proc['name'][:-4]
        else:
            proc['clean_name'] = proc['name']

        # indented name
        proc['indented'] = ' ' * indent + proc['clean_name']
        if our_children:
            # child processes
            proc['indented'] = console.orange(proc['indented'])
        elif 'description' in proc and '!!!' in proc['description']:
            # dangerous processes
            proc['indented'] = console.red(proc['indented'])
        elif 'description' in proc and '+++' in proc['description']:
            # potentially dangerous processes
            proc['indented'] = console.red(proc['indented'])
        elif proc['name'].lower() in browsers:
            # browser processes
            proc['indented'] = console.cyan(proc['indented'])

        # current proc is first one
        output_procs = [proc]

        # recurse children
        children = get_children(proc['pid'])
        for child in children:
            output_procs += make_tree(child, indent + 4, our_children=our_children)

        return output_procs

    tree_procs = []
    for trunk in get_trunks(procs):
        tree_procs += make_tree(trunk)

    headers = collections.OrderedDict((('pid', 'PID'),
                                       ('ppid', 'PPID'),
                                       ('indented', 'Name'),
                                       ('description', 'Description'),
                                       ('user', 'User'),
                                       ('session', 'Session')))

    time.sleep(10)

    return console.table(tree_procs, keys=headers)

engine.loop()
