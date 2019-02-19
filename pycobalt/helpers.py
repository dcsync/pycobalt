"""
Helper functions for writing pycobalt scripts

`argument_quote` and `cmd_quote` are from Holger Just
(https://twitter.com/meineerde, https://github.com/meineerde).

https://stackoverflow.com/questions/29213106/how-to-securely-escape-command-line-arguments-for-the-cmd-exe-shell-on-windows

> The problem with quoting command lines for windows is that there are two
> layered parsing engines affected by your quotes. At first, there is the Shell
> (e.g. cmd.exe) which interprets some special characters. Then, there is the
> called program parsing the command line. This often happens with the
> CommandLineToArgvW function provided by Windows, but not always.

> That said, for the general case, e.g. using cmd.exe with a program parsing its
> command line with CommandLineToArgvW, you can use the techniques described by
> Daniel Colascione in Everyone quotes command line arguments the wrong way. I
> have originally tried to adapt this to Ruby and now try to translate this to
> python here.

Thanks Holger!
"""

import re
import base64
import inspect
import argparse
import subprocess
import random
import string

import pycobalt.utils as utils
import pycobalt.engine as engine
import pycobalt.callbacks as callbacks
import pycobalt.aggressor as aggressor

def parse_ps(content):
    """
    Parse output of `bps()` as passed to the callback.

    :param content: Output of `bps()`
    :return: List of dictionaries representing the process list, sorted by PID.
             Dictionary fields include: name, ppid, pid, arch, and user.
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
    Parse output of `bjobs()` as passed to `beacon_output_jobs callback`.

    :param content: Output of `bjobs()` as passed to the `beacon_output_jobs`
                    event callback.
    :return: List of dictionaries representing the job list. Dictionary fields
             include: jid, pid, and description.
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

def parse_ls(content):
    """
    Parse output of `bls()` as passed to the callback.

    :param content: Output of `bls()`
    :return: List of dictionaries representing the file list, sorted by name.
             Dictionary fields include: type, size, modified, and name
    """

    files = []

    # skip first line. it's just the directory name
    lines = content.splitlines()[1:]
    for line in lines:
        new = {}
        new['type'], new['size'], new['modified'], new['name'] = line.split('\t')

        # convert numbers
        new['size'] = int(new['size'])

        # ignore . and ..
        if new['name'] in ['.', '..']:
            continue

        files.append(new)

    # sort it
    files = list(sorted(files, key=lambda item: item['name']))

    return files

def recurse_ls(bid, directory, callback, depth=9999):
    """
    Recursively list files. Call callback(path) for each file.

    :param bid: Beacon to list files on
    :param directory: Directory to list
    :param callback: Callback to call for each file
    :param depth: Max depth to recurse
    """

    if not depth:
        # max depth reached
        return

    def ls_callback(bid, directory, content):
        files = parse_ls(content)
        for f in files:
            path = r'{}\{}'.format(directory, f['name'])

            if f['type'] == 'D':
                # recurse
                recurse_ls(bid, path, callback, depth=depth - 1)
            else:
                callback(path)

    aggressor.bls(bid, directory, ls_callback)

def find_process(bid, proc_name, callback):
    """
    Find processes by name. Call callback with results.

    :param bid: Beacon to use
    :param proc_name: Process name(s) to search for. Can be a list of names or
                      a single name.
    :param callback: Callback for results. Syntax is `callback(procs)` where
                     `procs` is the output of `parse_ps`.
    """

    if isinstance(proc_name, list):
        # already a list
        proc_names = proc_name
    else:
        # make it a list
        proc_names = [proc_name]

    def ps_callback(bid, content):
        procs = parse_ps(content)
        ret = filter(lambda p: p['name'] in proc_names, procs)
        callback(ret)

    aggressor.bps(bid, ps_callback)

def is_admin(bid):
    """
    Check if beacon is admin (including SYSTEM)

    :param bid: Beacon to use
    :return: True if beacon is elevated (i.e. admin with UAC disabled or
             SYSTEM)
    """

    if aggressor.isadmin(bid):
        return True

    user = real_user(bid)
    if user.lower() == 'system':
        return True

    return False;

def default_listener():
    """
    Make a semi-educated guess at which listener might be the default one

    :return: Possble default listener
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

    :param bid: Beacon to use
    :param fname: File to stomp
    """

    aggressor.btimestomp(bid, fname, r'c:/windows/explorer.exe')

def upload_to(bid, local_file, remote_file, silent=False):
    """
    Upload local file to a specified remote destination

    :param bid: Beacon to use
    :param local_file: File to upload
    :param remote_file: Upload file to this destination
    :param silent: Passed to `bupload_raw`
    """

    with open(local_file, 'rb') as fp:
        data = fp.read()

    aggressor.bupload_raw(bid, remote_file, data, local_file, silent=silent)

def real_user(bid):
    """
    Get just the username of a beacon.

    :param bid: Bid to check
    :return: Username of beacon
    """

    return aggressor.beacon_info(bid)['user'].replace(' *', '')

def guess_home(bid):
    """
    Guess %userprofile% directory based on beacon user

    :param bid: Beacon to use
    :return: Possible %userprofile% (home) directory
    """

    return r'c:\users\{}'.format(real_user(bid))

def guess_appdata(bid):
    """
    Guess %appdata% directory based on beacon user

    :param bid: Beacon to use
    :return: Possible %appdata% directory
    """

    return r'{}\AppData\Roaming'.format(guess_home(bid))

def guess_localappdata(bid):
    """
    Guess %localappdata% directory based on beacon user

    :param bid: Beacon to use
    :return: Possible %localappdata% directory
    """

    return r'{}\AppData\Local'.format(guess_home(bid))

def guess_temp(bid):
    """
    Guess %temp% directory based on beacon user

    :param bid: Beacon to use
    :return: Possible %temp% directory
    """

    return r'{}\AppData\Local\Temp'.format(guess_home(bid))

def powershell_quote(arg):
    """
    Quote a powershell string. Returns a string enclosed in single quotation
    marks with internal marks escaped. Also removes newlines.

    Can also do a list of strings.

    :param arg: Argument to quote (string or list of strings)
    :return: Quoted argument
    """

    if isinstance(arg, list) or isinstance(arg, tuple):
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

    :param arg: Argument to quote (string or list of strings)
    :return: Quoted argument
    """

    return powershell_quote(arg)

def argument_quote(arg):
    """
    Escape the argument for the cmd.exe shell.
    See http://blogs.msdn.com/b/twistylittlepassagesallalike/archive/2011/04/23/everyone-quotes-arguments-the-wrong-way.aspx

    First we escape the quote chars to produce a argument suitable for
    CommandLineToArgvW. We don't need to do this for simple arguments.

    :param arg: Argument to quote
    :return: Quoted argument
    """

    if isinstance(arg, list) or isinstance(arg, tuple):
        # recurse list
        return [argument_quote(child) for child in arg]
    else:
        if not arg or re.search(r'(["\s])', arg):
            arg = '"' + arg.replace('"', r'\"') + '"'

        return escape_for_cmd_exe(arg)

def aq(arg):
    """
    Alias for argument_quote

    :param arg: Argument to quote
    :return: Quoted argument
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

    :param arg: Argument to quote
    :return: Quoted argument
    """

    if isinstance(arg, list) or isinstance(arg, tuple):
        # recurse list
        return [cmd_quote(child) for child in arg]
    else:
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

    :param arg: Argument to quote
    :return: Quoted argument
    """

    return cmd_quote(arg)

def capture(command, stdin=None, shell=False, merge_stderr=False):
    """
    Run a command and capture its output.

    :command: Command to run (list of arguments or string)
    :stdin: String to write to stdin
    :shell: Run as a shell command
    :merge_stderr: Redirect stderr to stdout

    :return: Returns a tuple containing code, stdout, stderr
    """

    if merge_stderr:
        # redirect to stdout
        stderr = subprocess.STDOUT
    else:
        stderr = subprocess.PIPE

    proc = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=stderr)

    stdout, stderr = proc.communicate(input=stdin)
    code = proc.poll()

    return code, stdout, stderr

def randstr(minsize=4, maxsize=8):
    """
    Generate a random ascii string with a length between `minsize` and `maxsize`.
    Useful for writing temp files and generating obfuscated scripts on the fly.

    :param minsize: Minimum size of string
    :param maxsize: Maximum size of string
    :return: Random string
    """

    size = random.randint(minsize, maxsize + 1)
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(size))

def obfuscate_tokens(data, regex=r'%%[^%]+%%'):
    """
    Obfuscate tokens in a string. By default it will match all %%foo%% tokens
    and replace them with random ascii strings (generated with `randstr`).
    This is useful for generating obfuscated scripts on the fly.

    :data: String containing tokens to obfuscate
    :regex: Alternative regex to match
    :return: Obfuscated string
    """

    # get tokens
    matches = re.finditer(regex, data)
    tokens = [m.group(0) for m in matches]
    unique = set(tokens)

    def gentokens(factor=5):
        while True:
            yield randstr(3 * factor, 5 * factor)

    token_iter = iter(unique)
    replace_iter = gentokens()
    for token, replace in zip(token_iter, replace_iter):
        while replace in data:
            replace = next(replace_iter)
        data = data.replace(token, replace)

    return data

def chunkup(item, size=75):
    """
    Split a string, list, or other indexable object into chunks of size `size`.
    If the length of `item` is not divisible by `size` the last chunk will be
    shorter than the others.

    :param item: Item to split
    :param size: Chunk size
    :return: List of chunks
    """

    chunks = [
	    item[i:i + size] for i in range(0, len(item), size)
	]
    return chunks

def powershell_base64(string):
    """
    Encode a string as UTF-16LE and base64 it. The output is compatible with
    Powershell's -EncodedCommand.

    :param string: String to base64
    :return: Base64 encoded string
    """

    return base64.b64encode(string.encode('UTF-16LE')).decode()

class ArgumentParser(argparse.ArgumentParser):
    """
    Special version of ArgumentParser that prints to beacon console or script
    console instead of stdout.
    """

    def __init__(self, bid=None, event_log=False, *args, **kwargs):
        """
        With the exception of the `bid` argument all arguments are passed to
        `argparse.ArgumentParser`.

        :param bid: Print errors to this beacon's console (default: script
                    console)
        :param event_log: Print errors to Event Log
        """

        self.bid = bid
        self.event_log = event_log

        if 'prog' not in kwargs:
            # fix prog name
            kwargs['prog'] = 'command'

        super().__init__(*args, **kwargs)

    def error(self, message):
        if self.bid:
            # print to beacon console
            aggressor.berror(self.bid, message)
        elif self.event_log:
            aggressor.say('\n' + message)
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
