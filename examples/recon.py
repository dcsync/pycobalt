#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import utils
sys.path.insert(0, utils.basedir('..'))

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.commands as commands
import pycobalt.aliases as aliases
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks

@aliases.alias('wanip', 'Get WAN IP (or WAN IP of the outgoing DNS server)')
def alias_wanip(bid):
    aggressor.bshell(bid, 'nslookup myip.opendns.com. resolver1.opendns.com')

@aliases.alias('basic', 'Perform some basic initial recon')
def alias_basic(bid):
    command = """
whoami /all
wmic os get Caption /value | more
echo Home: %userprofile%
echo Domain: %logonserver%
"""

    aggressor.bshell(bid, command)

    aggressor.bps(bid)
    aggressor.bnet(bid, 'logons')
    aggressor.bnet(bid, 'sessions')
    aggressor.bpwd(bid)

@aliases.alias('network', 'Perform some basic network-related recon')
def alias_network(bid):
    command = """
hostname 2>&1
ipconfig /all 2>&1
nslookup myip.opendns.com. resolver1.opendns.com
"""

    aggressor.bshell(bid, command)

@aliases.alias('patches', 'Get list of patches on system')
def alias_patches(bid):
    command = """
wmic os get Caption /value | more
wmic qfe
"""

    aggressor.bshell(bid, command)

@aliases.alias('domain', 'Get domain info (output may be large)')
def alias_domain(bid):
    aggressor.bnet(bid, 'dclist')
    aggressor.bnet(bid, 'computers')
    aggressor.bnet(bid, 'view')

    command = """
echo Domain: %logonserver%
net group "domain admins" /domain 2>&1
net group /domain 2>&1
net group "Exchange Trusted Subsystem" /domain
net accounts /domain
"""

    aggressor.bshell(bid, command)

@aliases.alias('apps', 'Get list of app uninstallers')
def alias_apps(bid):
    command = r"""
Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* |
Select-Object DisplayName, InstallDate |
Sort-Object -Property DisplayName |
Format-Table -AutoSize
"""

    aggressor.bpowerpick(bid, command)

@aliases.alias('appdata', 'List folders in Local and Roaming AppData')
def alias_appdata(bid):
    command = """
ls $env:localappdata
ls $env:appdata
"""

    aggressor.bpowerpick(bid, command)

@aliases.alias('docs', 'List common document folders')
def alias_docs(bid):
    command = ''

    for d in ['Desktop', 'Documents', 'Downloads']:
        command += 'ls $env:userprofile\\{}\n'.format(d)

    aggressor.bpowerpick(bid, command)

engine.loop()
