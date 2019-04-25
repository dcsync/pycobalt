
# pycobalt.helpers

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

## parse_ps
```python
parse_ps(content)
```

Parse output of `bps()` as passed to the callback.

**Arguments**:

- `content`: Output of `bps()`

**Returns**:

List of dictionaries representing the process list, sorted by PID.
         Dictionary fields include: name, ppid, pid, arch, and user.

## parse_jobs
```python
parse_jobs(content)
```

Parse output of `bjobs()` as passed to `beacon_output_jobs callback`.

**Arguments**:

- `content`: Output of `bjobs()` as passed to the `beacon_output_jobs`
                event callback.

**Returns**:

List of dictionaries representing the job list. Dictionary fields
         include: jid, pid, and description.

## parse_ls
```python
parse_ls(content)
```

Parse output of `bls()` as passed to the callback.

**Arguments**:

- `content`: Output of `bls()`

**Returns**:

List of dictionaries representing the file list, sorted by name.
         Dictionary fields include: type, size, modified, and name

## recurse_ls
```python
recurse_ls(bid, directory, callback, depth=9999)
```

Recursively list files. Call callback(path) for each file.

**Arguments**:

- `bid`: Beacon to list files on
- `directory`: Directory to list
- `callback`: Callback to call for each file
- `depth`: Max depth to recurse

## find_process
```python
find_process(bid, proc_name, callback)
```

Find processes by name. Call callback with results.

**Arguments**:

- `bid`: Beacon to use
- `proc_name`: Process name(s) to search for. Can be a list of names or
                  a single name.
- `callback`: Callback for results. Syntax is `callback(procs)` where
                 `procs` is the output of `parse_ps`.

## is_admin
```python
is_admin(bid)
```

Check if beacon is admin (including SYSTEM)

**Arguments**:

- `bid`: Beacon to use

**Returns**:

True if beacon is elevated (i.e. admin with UAC disabled or
         SYSTEM)

## default_listener
```python
default_listener()
```

Make a semi-educated guess at which listener might be the default one

**Returns**:

Possble default listener

## explorer_stomp
```python
explorer_stomp(bid, fname)
```

Stomp time with time of explorer.exe

**Arguments**:

- `bid`: Beacon to use
- `fname`: File to stomp

## upload_to
```python
upload_to(bid, local_file, remote_file, silent=False)
```

Upload local file to a specified remote destination

**Arguments**:

- `bid`: Beacon to use
- `local_file`: File to upload
- `remote_file`: Upload file to this destination
- `silent`: Passed to `bupload_raw`

## real_user
```python
real_user(bid)
```

Get just the username of a beacon.

**Arguments**:

- `bid`: Bid to check

**Returns**:

Username of beacon

## guess_home
```python
guess_home(bid)
```

Guess %userprofile% directory based on beacon user

**Arguments**:

- `bid`: Beacon to use

**Returns**:

Possible %userprofile% (home) directory

## guess_appdata
```python
guess_appdata(bid)
```

Guess %appdata% directory based on beacon user

**Arguments**:

- `bid`: Beacon to use

**Returns**:

Possible %appdata% directory

## guess_localappdata
```python
guess_localappdata(bid)
```

Guess %localappdata% directory based on beacon user

**Arguments**:

- `bid`: Beacon to use

**Returns**:

Possible %localappdata% directory

## guess_temp
```python
guess_temp(bid)
```

Guess %temp% directory based on beacon user

**Arguments**:

- `bid`: Beacon to use

**Returns**:

Possible %temp% directory

## powershell_quote
```python
powershell_quote(arg)
```

Quote a string or list of strings for PowerShell. Returns a string enclosed
in single quotation marks with internal marks escaped. Also removes
newlines.

Can also do a list of strings.

**Arguments**:

- `arg`: Argument to quote (string or list of strings)

**Returns**:

Quoted string or list of strings

## pq
```python
pq(arg)
```

Alias for `powershell_quote`

**Arguments**:

- `arg`: Argument to quote (string or list of strings)

**Returns**:

Quoted string or list of strings

## csharp_quote
```python
csharp_quote(arg)
```

Turn a string or list of strings into C# string literals. Returns a @""
string literal with internal double quotes escaped. Also removes newlines.

**Arguments**:

- `arg`: Argument to quote (string or list of strings)

**Returns**:

Quoted string or list of strings

## argument_quote
```python
argument_quote(arg)
```

Escape the argument for the cmd.exe shell.
See http://blogs.msdn.com/b/twistylittlepassagesallalike/archive/2011/04/23/everyone-quotes-arguments-the-wrong-way.aspx

First we escape the quote chars to produce a argument suitable for
CommandLineToArgvW. We don't need to do this for simple arguments.

**Arguments**:

- `arg`: Argument to quote

**Returns**:

Quoted argument

## aq
```python
aq(arg)
```

Alias for argument_quote

**Arguments**:

- `arg`: Argument to quote

**Returns**:

Quoted argument

## cmd_quote
```python
cmd_quote(arg)
```

Escape an argument string to be suitable to be passed to
cmd.exe on Windows

This method takes an argument that is expected to already be properly
escaped for the receiving program to be properly parsed. This argument
will be further escaped to pass the interpolation performed by cmd.exe
unchanged.

Any meta-characters will be escaped, removing the ability to e.g. use
redirects or variables.

**Arguments**:

- `arg`: Argument to quote

**Returns**:

Quoted argument

## cq
```python
cq(arg)
```

Alias for cmd_quote

**Arguments**:

- `arg`: Argument to quote

**Returns**:

Quoted argument

## capture
```python
capture(command, stdin=None, shell=False, merge_stderr=False)
```

Run a client/local command and capture its output.

:command: Command to run (list of arguments or string)
:stdin: String to write to stdin
:shell: Run as a shell command
:merge_stderr: Redirect stderr to stdout

**Returns**:

Returns a tuple containing (return_code, stdout, stderr)

## randstr
```python
randstr(minsize=4, maxsize=8)
```

Generate a random ascii string with a length between `minsize` and `maxsize`.
Useful for writing temp files and generating obfuscated scripts on the fly.

**Arguments**:

- `minsize`: Minimum size of string
- `maxsize`: Maximum size of string

**Returns**:

Random string

## obfuscate_tokens
```python
obfuscate_tokens(data, regex='%%[^%]+%%')
```

Obfuscate tokens in a string. By default it will match all %%foo%% tokens
and replace them with random ascii strings (generated with `randstr`).
This is useful for generating obfuscated scripts on the fly.

:data: String containing tokens to obfuscate
:regex: Alternative regex to match

**Returns**:

Obfuscated string

## chunkup
```python
chunkup(item, size=75)
```

Split a string, list, or other indexable object into chunks of size `size`.
If the length of `item` is not divisible by `size` the last chunk will be
shorter than the others.

**Arguments**:

- `item`: Item to split
- `size`: Chunk size

**Returns**:

List of chunks

## powershell_base64
```python
powershell_base64(string)
```

Encode a string as UTF-16LE and base64 it. The output is compatible with
Powershell's -EncodedCommand.

**Arguments**:

- `string`: String to base64

**Returns**:

Base64 encoded string

## fix_multiline_string
```python
fix_multiline_string(string, *args, **kwargs)
```

Fix an indented multi-line string. Example:

    csharp = helpers.code_format('''
                Console.WriteLine("{arg1}" + "{arg2}");
                ''', arg1='ex', arg2='ample')

This will de-indent the code, remove the leading newline, remove trailing
whitespace, and call `string.format()` on it.

**Arguments**:

- `string`: String to format
:param *args: Arguments to pass to `string.format()`
:param *kwargs: Keyword arguments to pass to `string.format()`

**Returns**:

Formatted code

## path_to_unc
```python
path_to_unc(host, path)
```

Convert path to UNC path

    python> path_to_unc('CORP-PC', 'C:\Users\CEO')
    '\\CORP-PC\C$\Users\CEO'

**Arguments**:

- `host`: Host to use
- `path`: Path to convert

**Returns**:

UNC path

## ArgumentParser
```python
ArgumentParser(bid=None, event_log=False, *args, **kwargs)
```

Special version of ArgumentParser that prints to beacon console, Script
Console, or Event Log instead of stdout.

With the exception of the `bid` and `event_log` arguments all constructor
arguments are passed to `argparse.ArgumentParser`.

**Arguments**:

- `bid`: Print errors to this beacon's console (default: script
            console)
- `event_log`: Print errors to Event Log (default: False)
