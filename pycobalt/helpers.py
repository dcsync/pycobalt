"""
Helper functions for writing pycobalt scripts
"""

import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.engine as engine

def parse_ps(content):
    """
    Parse output of bps()

    Returns: [{name, ppid, pid, arch, user}...]
    """

    procs = []
    for line in content.splitlines():
        proc = {}
        proc['name'], proc['ppid'], proc['pid'], *others = line.split('\t')

        # convert numbers
        proc['pid'] = int(proc['pid'])
        proc['ppid'] = int(proc['ppid'])

        # get arch
        if len(others) > 1:
            proc['arch'] = others[0]

        # get user
        if len(others) > 2:
            proc['user'] = others[1]

        procs.append(proc)

    # sort it
    procs = list(sorted(procs, key=lambda item: item['pid']))

    return procs

def findprocess(bid, proc_name, callback):
    """
    Find processes by name. Call callback([{name, pid, ppid, arch?, user?}, ...]) with results.
    """

    def ps_callback(bid, content):
        procs = parse_ps(content)
        ret = filter(lambda p: p['name'] == proc_name, procs)
        callback(ret)

    aggressor.bps(bid, ps_callback)

def isAdmin(bid):
    """
    Check if beacon is admin (including SYSTEM)
    """

    if aggressor.isadmin(bid):
        return True

    user = aggressor.beacon_info(bid, 'user')
    if user.lower() == 'system':
        return True

    return False;

def defaultListener():
    """
    Make a semi-educated guess at which listener might be the default one
    """

    listeners = aggressor.listeners_local()

    if not listeners:
        return None

    for listener in listeners:
        if 'http' in listener:
            return listener

    return listeners[0]

def explorerstomp(bid, fname):
    """
    Stomp time with time of explorer.exe
    """

    aggressor.btimestomp(bid, fname, r'c:/windows/explorer.exe')

def uploadto(bid, local_file, remote_file):
    """
    Upload local file to a specified remote destination
    """

    with open(local_file, 'rb') as fp:
        data = fp.read()

    aggressor.bupload_raw(bid, remote_file, data, local_file)

def guessHome(bid):
    """
    Guess %userprofile% directory based on beacon user
    """

    return r'c:\users\{}'.format(aggressor.beacon_info(bid)['user'])

def guessTemp(bid):
    """
    Guess %temp% directory based on beacon user
    """

    return r'{}\AppData\Local\Temp'.format(guessHome(bid))
