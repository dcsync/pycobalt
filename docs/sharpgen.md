# pycobalt.sharpgen

Helper functions for using cobbr's SharpGen

See examples/sharpgen.py for a working set of compile/exec console commands and
aliases. Refer to `README.md` for more usage info.

For more information about SharpGen see:
- https://posts.specterops.io/operational-challenges-in-offensive-c-355bd232a200
- https://github.com/cobbr/SharpGen

## set_location
```python
set_location(location)
```

Set the SharpGen directory location. By default it will point to the repo
copy, which is a git submodule.

This module will find the SharpGen DLL in <location>/bin.

**Arguments**:

- `location`: Location of the SharpGen directory

## enable_cache
```python
enable_cache()
```

Enable the build cache

The cache format is pretty simple. The cache directory stores a bunch of PE
files. The filename for each PE is the MD5 hash of its source code.

This could obviously cause problems if you're actively developing some
fresh new C# and change a compilation option without changing the source.

## disable_cache
```python
disable_cache()
```

Disable the build cache

## set_confuse
```python
set_confuse(config)
```

Set a default location for ConfuserEx config. This is so you don't have to
keep passing the `confuse=` compilation keyword argument.

**Arguments**:

- `config`: ConfuserEx config file

## set_cache_location
```python
set_cache_location(location=None)
```

Set the build cache location. The default location is SharpGen/Cache.

**Arguments**:

- `location`: Directory to put cached builds in. If not passed, reset to
default location.

## clear_cache
```python
clear_cache()
```

Clear the build cache

## cache_remove
```python
cache_remove(source_hash)
```

Remove a file from the build cache if it exists

**Arguments**:

- `source_hash`: Source hash

**Returns**:

True if the cached build existed

## cache_lookup
```python
cache_lookup(source_hash)
```

Look up a source hash in the cache

**Arguments**:

- `source_hash`: Source hash

**Returns**:

Full file path to the cached build or None if it doesn't exist

## cache_lookup_file
```python
cache_lookup_file(source_file)
```

Look up a source file in the cache

**Arguments**:

- `source_file`: Source file

**Returns**:

Full file path to the cached build or None if it doesn't exist

## cache_lookup_code
```python
cache_lookup_code(source)
```

Look up some source code in the cache

**Arguments**:

- `source`: Source code

**Returns**:

Full file path to the cached build or None if it doesn't exist

## cache_retrieve
```python
cache_retrieve(source_hash, out)
```

Retrieve a file from the build cache if it exists

**Arguments**:

- `source_hash`: Source hash
- `out`: Output file to copy cached build to

**Returns**:

True if a cached build was copied to `out` successfully

## cache_source_hash
```python
cache_source_hash(source)
```

Get a hash of some source code

**Arguments**:

- `source`: String containing source code

**Returns**:

MD5 hash of source code

## cache_file_hash
```python
cache_file_hash(source_file)
```

Get a hash of some source code file

**Arguments**:

- `source`: Source code file

**Returns**:

MD5 hash of source code

## wrap_code
```python
wrap_code(source, function_name='Main', function_type='void', class_name=None, libraries=None)
```

Wrap a piece of source code in a class and function, similar to what
SharpGen does. We perform the function wrapping here in order to have more
control over the final product.

**Arguments**:

- `source`: Source to wrap
- `function_name`: Function name (default: Main)
- `function_type`: Function type (default: void)
- `class_name`: Class name (default: random)
- `libraries`: List of librares to use (default: sharpgen.default_libraries)

## compile
```python
compile(source, use_wrapper=True, assembly_name=None, class_name=None, function_name=None, function_type=None, libraries=None, output_kind='console', platform='x86', confuse=None, dotnet_framework='net35', optimization=True, out=None, additional_options=None, resources=None, references=None, cache=None, overwrite_cache=False, no_cache_write=False, sharpgen_location=None, sharpgen_runner=None)
```

Compile some C# code using SharpGen.

**Arguments**:

- `source`: Source to compile

- `use_wrapper`: Use a class and function Main code wrapper (default: True)
- `class_name`: Name of generated class (default: random)
- `function_name`: Name of function for wrapper (default: Main for .exe, Execute for .dll)
- `function_type`: Function return type (default: void for .exe, object for .dll)
- `libraries`: Libraries to use in the wrapper (default: sharpgen.default_libraries)

- `assembly_name`: Name of generated assembly (default: random)
- `output_kind`: Type of output (exe/console or dll/library) (default: console)
- `platform`: Platform to compile for (any/AnyCpy, x86, or x64) (default: x86)
- `confuse`: ConfuserEx configuration file. Set a default for this
option with `set_confuse(<file>)`.
- `dotnet_framework`: .NET version to compile against (net35 or net40) (default: net35)
- `optimization`: Perform code optimization (default: True)
- `out`: Output file (default: file in /tmp)

- `additional_options`: List of additional SharpGen options/flags
(passed through raw)

- `resources`: List of resources to whitelist (by Name). These must be
present in your resources.yml file.
- `references`: List of references to whitelist (by File). These must be
present in your references.yml file.

- `cache`: Use the build cache. Not setting this option will use the
global settings (`enable_cache()`/`disable_cache()`). By
default the build cache is off.
- `overwrite_cache`: Force overwriting this build in the cache (disable
cache retrieval but not writing)
- `no_cache_write`: Allow for cache retrieval but not cache writing

- `sharpgen_location`: Location of SharpGen directory (default: location
passed to `set_location()` or PyCobalt repo copy)
- `sharpgen_runner`: Program used to run the SharpGen dll (default:
sharpgen.default_runner or 'dotnet')

**Returns**:

Tuple containing (out, cached) where `out` is the name of the
output file and `cached` is a boolean containing True if the build
is from the build cache

**Raises**:

- `RuntimeError`: If one of the options is invalid

## compile_file
```python
compile_file(source_file, **kwargs)
```

Compile a file using SharpGen.

**Arguments**:

- `source_file`: Source file to compile
- `use_wrapper`: Use wrapper (default: False)
:param **kwargs: Other compilation arguments passed to `compile`.

**Returns**:

Tuple containing (out, cached) where `out` is the name of the
output file and `cached` is a boolean containing True if the build
is from the build cache

**Raises**:

- `RuntimeError`: If one of the options is invalid

## execute_file
```python
execute_file(bid, source, args, **kwargs)
```

Compile and execute a C# file

**Arguments**:

- `bid`: Beacon to execute on
- `source`: Source file to compile
- `args`: Arguments used for execution
:param **kwargs: Compilation arguments passed to `compile_file`.

**Returns**:

True if the executed build was from the build cache

**Raises**:

- `RuntimeError`: If one of the options is invalid

## execute
```python
execute(bid, code, args, **kwargs)
```

Compile and execute some C# code

**Arguments**:

- `bid`: Beacon to execute on
- `code`: Code to compile
- `args`: Arguments used for execution
:param **kwargs: Compilation arguments passed to `compile_file`.

**Returns**:

True if the executed build was from the build cache

**Raises**:

- `RuntimeError`: If one of the options is invalid

