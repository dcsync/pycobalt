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

@aliases.alias('ls-time', 'List files, sorted by time')
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

@aliases.alias('find', 'Find a file by pattern and/or number of days old')
def alias_find(bid, directory, pattern=None, days=None):
    command = ''

    if days:
        command += '$date = (Get-Date).AddDays(-{}); '.format(days)

    command += "gci -Recurse -Path '{}' ".format(directory)
    if pattern:
        command += "-Include '{}' ".format(pattern)

    if days:
        command += '| ? { $_.LastWriteTime -ge $date }'

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
