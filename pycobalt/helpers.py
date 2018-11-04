"""
Helper functions for writing pycobalt scripts
"""

import argparse
import inspect
import re

import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.engine as engine
import pycobalt.utils as utils

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

def parse_jobs(content):
    """
    Parse output of bjobs() as passed to beacon_output_jobs callback.

    Returns: [{jid, pid, description}...]
    """

    jobs = []

    for line in content.splitlines():
        job = {}
        job['jid'], job['pid'], job['description'] = line.split('\t')

        # convert numbers
        job['jid'] = int(job['jid'])
        job['pid'] = int(job['pid'])

        jobs.append(job)

    return jobs

def find_process(bid, proc_name, callback):
    """
    Find processes by name. Call callback([{name, pid, ppid, arch?, user?}, ...]) with results.
    """

    def ps_callback(bid, content):
        procs = parse_ps(content)
        ret = filter(lambda p: p['name'] == proc_name, procs)
        callback(ret)

    aggressor.bps(bid, ps_callback)

def is_admin(bid):
    """
    Check if beacon is admin (including SYSTEM)
    """

    if aggressor.isadmin(bid):
        return True

    user = aggressor.beacon_info(bid, 'user')
    if user.lower() == 'system':
        return True

    return False;

def default_listener():
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

def explorer_stomp(bid, fname):
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

def guess_home(bid):
    """
    Guess %userprofile% directory based on beacon user
    """

    return r'c:\users\{}'.format(aggressor.beacon_info(bid)['user'])

def guess_temp(bid):
    """
    Guess %temp% directory based on beacon user
    """

    return r'{}\AppData\Local\Temp'.format(guess_home(bid))

def powershell_quote(arg):
    """
    Quote a powershell string. Returns a string enclosed in single quotation
    marks with internal marks escaped. Also removes newlines.

    Can also do a list of strings.
    """

    if isinstance(arg, list) or isinstance(item, tuple):
        # recurse list
        return [powershell_quote(child) for child in arg]
    else:
        # remove newlines
        new_string = str(arg).replace('\n', '').replace('\r', '')

        # quote ' characters
        new_string = new_string.replace("'", "''")

        # enclose in '
        new_string = "'{}'".format(new_string)

        return new_string

def pq(arg):
    """
    Alias for `powershell_quote`
    """

    return powershell_quote(arg)

# argument_quote and cmd_quote from Holger Just (https://twitter.com/meineerde, https://github.com/meineerde).
# https://stackoverflow.com/questions/29213106/how-to-securely-escape-command-line-arguments-for-the-cmd-exe-shell-on-windows
#
# > The problem with quoting command lines for windows is that there are two
# > layered parsing engines affected by your quotes. At first, there is the Shell
# > (e.g. cmd.exe) which interprets some special characters. Then, there is the
# > called program parsing the command line. This often happens with the
# > CommandLineToArgvW function provided by Windows, but not always.
#
# > That said, for the general case, e.g. using cmd.exe with a program parsing its
# > command line with CommandLineToArgvW, you can use the techniques described by
# > Daniel Colascione in Everyone quotes command line arguments the wrong way. I
# > have originally tried to adapt this to Ruby and now try to translate this to
# > python here.
#
# thanks Holger!
def argument_quote(arg):
    """
    Escape the argument for the cmd.exe shell.
    See http://blogs.msdn.com/b/twistylittlepassagesallalike/archive/2011/04/23/everyone-quotes-arguments-the-wrong-way.aspx

    First we escape the quote chars to produce a argument suitable for
    CommandLineToArgvW. We don't need to do this for simple arguments.
    """

    if not arg or re.search(r'(["\s])', arg):
        arg = '"' + arg.replace('"', r'\"') + '"'

    return escape_for_cmd_exe(arg)

def aq(arg):
    """
    Alias for argument_quote
    """

    return argument_quote(arg)

def cmd_quote(arg):
    """
    Escape an argument string to be suitable to be passed to
    cmd.exe on Windows

    This method takes an argument that is expected to already be properly
    escaped for the receiving program to be properly parsed. This argument
    will be further escaped to pass the interpolation performed by cmd.exe
    unchanged.

    Any meta-characters will be escaped, removing the ability to e.g. use
    redirects or variables.

    @param arg [String] a single command line argument to escape for cmd.exe
    @return [String] an escaped string suitable to be passed as a program
      argument to cmd.exe
    """

    meta_chars = '()%!^"<>&|'
    meta_re = re.compile('(' + '|'.join(re.escape(char) for char in list(meta_chars)) + ')')
    meta_map = { char: "^%s" % char for char in meta_chars }

    def escape_meta_chars(m):
        char = m.group(1)
        return meta_map[char]

    return meta_re.sub(escape_meta_chars, arg)

def cq(arg):
    """
    Alias for cmd_quote
    """

    return cmd_quote(arg)

class ArgumentParser(argparse.ArgumentParser):
    """
    Special version of ArgumentParser that prints to beacon console or script
    console instead of stdout
    """

    def __init__(self, bid=None, *args, **kwargs):
        self.bid = bid

        if 'prog' not in kwargs:
            # fix prog name
            kwargs['prog'] = 'command'

        super().__init__(*args, **kwargs)

    def error(self, message):
        if self.bid:
            # print to beacon console
            aggressor.berror(self.bid, message)
        else:
            # print to script console
            engine.error(message)
        raise argparse.ArgumentError('exit')

    def exit(self, status=0, message=None):
        self.error(message)

    def print_usage(self, file=None):
        self.error(super().format_usage())

    def print_help(self, file=None):
        self.error(super().format_help())
