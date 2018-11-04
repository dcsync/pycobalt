#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import utils
sys.path.insert(0, utils.basedir('..'))

import textwrap

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.commands as commands
import pycobalt.aliases as aliases
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks
import pycobalt.helpers as helpers

@aliases.alias('pp', 'Alias for powerpick')
def alias_pp(bid, *args):
    command = ' '.join(args)
    aggressor.bpowerpick(bid, command)

@aliases.alias('psh', 'Alias for powershell')
def alias_psh(bid, *args):
    command = ' '.join(args)
    aggressor.bpowershell(bid, command)

@aliases.alias('s', 'Alias for shell')
def alias_s(bid, *args):
    command = ' '.join(args)
    aggressor.bshell(bid, command)

@aliases.alias('lsr', 'Recursively list files')
def alias_lsr(bid, *dirs):
    # default dir is .
    if not dirs:
        dirs = ['.']

    command = ''
    for d in dirs:
        command += 'Get-ChildItem -Recurse "{}"\n'.format(d)

    aggressor.bpowerpick(bid, command)

@aliases.alias('rmr', 'Recursively delete files and directories')
def alias_rmr(bid, *dirs):
    if not dirs:
        aggressor.berror('rmr: specify some directories to kill')
        return

    command = ''
    for d in dirs:
        command += 'Remove-Item -Recurse -Force "{}"\n'.format(d)
    
    aggressor.bpowerpick(bid, command)

@aliases.alias('cat', 'View files')
def alias_cat(bid, *files):
    if not files:
        aggressor.berror('cat: specify some files to cat')
        return

    command = '\n'.join(['type {}'.format(f) for f in files])

    aggressor.bshell(bid, command)

@aliases.alias('dl', 'Download a file')
def alias_dl(bid, *args):
    fname = ' '.join(args)
    aggressor.bdownload(bid, fname)

@aliases.alias('df', 'Show filesystem info')
def alias_df(bid):
    aggressor.bpowerpick(bid, 'Get-PSDrive')

@aliases.alias('pb', 'Open process browser')
def alias_pb(bid):
    aggressor.openProcessBrowser(bid)

@aliases.alias('info', 'Show beacon info')
def alias_info(bid):
    out = "Beacon info:\n\n"
    for key, value in aggressor.beacon_info(bid).items():
        out += ' - {}: {}\n'.format(key, value)

    aggressor.blog2(bid, out)

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
def alias_killall(bid, proc_name):
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
def alias_pgrep(bid, proc_name):
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
def alias_cl(bid, *args):
    directory = ' '.join(args)
    aggressor.bcd(bid, directory)
    aggressor.bls(bid)
    aggressor.bpwd(bid, silent=True)

@aliases.alias('l', 'Run ls on multiple directories')
def alias_l(bid, *dirs):
    # default dir is .
    if not dirs:
        dirs = ['.']

    for d in dirs:
        aggressor.bls(bid, d)

@aliases.alias('remove', 'Remove this beacon')
def alias_remove(bid):
    aggressor.beacon_remove(bid)

@aliases.alias('list-drives', 'Run ls in each drive')
def alias_list_drives(bid):
    aggressor.bpowerpick(bid, 'get-psdrive -psprovider filesystem | foreach-object { ls $_.root; }')

@aliases.alias('log', 'Display message on beacon console')
def alias_log(bid, *args):
    msg = ' '.join(args)
    aggressor.blog(bid, msg)

@aliases.alias('log2', 'Display message on beacon console')
def alias_log2(bid, *args):
    msg = ' '.join(args)
    aggressor.blog2(bid, msg)

@aliases.alias('error', 'Display error on beacon console')
def alias_error(bid, *args):
    msg = ' '.join(args)
    aggressor.berror(bid, msg)

@aliases.alias('estomp')
def alias_estomp(bid, fname):
    helpers.explorer_stomp(bid, fname)

@aliases.alias('uploadto', 'Upload file to a specified location')
def alias_uploadto(bid, local_file, remote_file):
    helpers.uploadto(bid, local_file, remote_file)

@aliases.alias('lst', 'List files, sorted by time')
def alias_ls_time(bid, *dirs):
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
def alias_curl(bid, url):
    aggressor.bpowerpick(bid, '(New-Object System.Net.WebClient).DownloadString("{}")'.format(url))

@aliases.alias('headers', 'Get response headers for webpage (sends GET request)')
def alias_head(bid, url):
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
def alias_host(bid, host):
    aggressor.bshell(bid, 'nslookup "{}"'.format(host))

@aliases.alias('home', 'Change to probable home directory')
def alias_home(bid):
    user = aggressor.binfo(bid, 'user')
    home = r'c:\users\{}'.format(user)
    aggressor.bcd(bid, home)

engine.loop()
