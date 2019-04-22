"""
Helper functions for using cobbr's SharpGen

See examples/sharpgen.py for a working set of compile/exec console commands and
aliases. Refer to `README.md` for more usage info.

For more information about SharpGen see:
  - https://posts.specterops.io/operational-challenges-in-offensive-c-355bd232a200
  - https://github.com/cobbr/SharpGen
"""

# TODO cache builds

import tempfile
import hashlib
import os

import pycobalt.utils as utils
import pycobalt.engine as engine
import pycobalt.callbacks as callbacks
import pycobalt.aggressor as aggressor
import pycobalt.helpers as helpers

# Location of the sharpgen directory
_sharpgen_location = utils.basedir('../third_party/SharpGen')

# Cache options
_cache_enabled = False
_cache_location = None

# ConfuserEx options
_confuserex_config = None

def set_location(location):
    """
    Set the SharpGen directory location. By default it will point to the repo
    copy, which is a git submodule.

    This module will find the SharpGen DLL in <location>/bin.

    :param location: Location of the SharpGen directory
    """

    global _sharpgen_location

    _sharpgen_location = location

def enable_cache():
    """
    Enable the build cache

    The cache format is pretty simple. The cache directory stores a bunch of PE
    files. The filename for each PE is the MD5 hash of its source code.

    This could obviously cause problems if you're actively developing some
    fresh new C# and change a compilation option without changing the source.
    """

    global _cache_enabled

    _cache_enabled = True

    if not _cache_location:
        # reset to <SharpGen>/Cache
        set_cache_location()

def disable_cache():
    """
    Disable the build cache
    """

    global _cache_enabled

    _cache_enabled = False

def set_confuse(config):
    """
    Set a default location for ConfuserEx config. This is so you don't have to
    keep passing the `confuse=` compilation keyword argument.

    :param config: ConfuserEx config file
    """

    global _confuserex_config

    _confuserex_config = config

def set_cache_location(location=None):
    """
    Set the build cache location. The default location is SharpGen/Cache.

    :param location: Directory to put cached builds in. If not passed, reset to
                     default location.
    """

    global _sharpgen_location
    global _cache_location

    if location:
        _cache_location = location
    else:
        # reset it
        _cache_location = '{}/Cache'.format(_sharpgen_location)

def _cache_path(source_hash):
    """
    Get the file path for a source hash

    :param source_hash: Source hash
    :return: Full file path to the cached build
    """

    global _cache_location

    return '{}/{}'.format(_cache_location, source_hash)

def clear_cache():
    """
    Clear the build cache
    """

    global _cache_location

    if not os.path.isdir(_cache_location):
        # cache does not exist
        return

    # delete all files in the cache directory
    for fname in os.listdir(_cache_location):
        path = '{}/{}'.format(_cache_location, fname)
        if os.path.isfile(path):
            os.remove(path)

def _cache_add(source_hash, build_file):
    """
    Add a file to the build cache

    :param source_hash: Source hash
    :param build_file: Build filename
    """

    global _cache_location

    # make the build cache directory if needed
    os.makedirs(_cache_location, exist_ok=True)

    path = _cache_path(source_hash)
    with open(path, 'wb+') as cachefp, open(build_file, 'rb') as buildfp:
        data = buildfp.read()
        cachefp.write(data)

def cache_remove(source_hash):
    """
    Remove a file from the build cache if it exists

    :param source_hash: Source hash
    :return: True if the cached build existed
    """

    global _cache_location

    if not os.path.isdir(_cache_location):
        # cache does not exist
        return False

    path = _cache_path(source_hash)

    if os.path.isfile(path):
        # file exists. delete it
        os.remove(path)
        return True
    else:
        # file does not exist
        return False

def cache_lookup(source_hash):
    """
    Look up a source hash in the cache

    :param source_hash: Source hash
    :return: Full file path to the cached build or None if it doesn't exist
    """

    path = _cache_path(source_hash)
    if os.path.isfile(path):
        return path
    else:
        return None

def cache_lookup_file(source_file):
    """
    Look up a source file in the cache

    :param source_file: Source file
    :return: Full file path to the cached build or None if it doesn't exist
    """

    source_hash = cache_file_hash(source)
    return cache_lookup(source_hash)

def cache_lookup_code(source):
    """
    Look up some source code in the cache

    :param source: Source code
    :return: Full file path to the cached build or None if it doesn't exist
    """

    source_hash = cache_source_hash(source)
    return cache_lookup(source_hash)

def cache_retrieve(source_hash, out):
    """
    Retrieve a file from the build cache if it exists

    :param source_hash: Source hash
    :param out: Output file to copy cached build to
    :return: True if a cached build was copied to `out` successfully
    """

    path = cache_lookup(source_hash)
    if path:
        # copy cached build to output file
        with open(path, 'rb') as cachedfp, open(out, 'wb+') as outfp:
            data = cachedfp.read()
            outfp.write(data)
        return True
    else:
        return False

def cache_source_hash(source):
    """
    Get a hash of some source code

    :param source: String containing source code
    :return: MD5 hash of source code
    """

    return hashlib.md5(source).hexdigest()

def cache_file_hash(source_file):
    """
    Get a hash of some source code file

    :param source: Source code file
    :return: MD5 hash of source code
    """

    with open(source_file, 'rb') as fp:
        return cache_source_hash(fp.read())

def _find_sharpgen_dll(location):
    """
    Find a SharpGen DLL in a SharpGen directory

    :param location: Location of SharpGen directory
    :return: Location of SharpGen DLL
    :raises: RuntimeError: If a copy of the DLL isn't found
    """

    # make sure SharpGen directory exists
    if not location or not os.path.isdir(location):
        raise RuntimeError("SharpGen directory '{}' does not exist".format(_sharpgen_location))

    candidates = ['bin/Release/netcoreapp2.1/SharpGen.dll',
                  'bin/Debug/netcoreapp2.1/SharpGen.dll']

    # look for dlls
    for candidate in candidates:
        full_path = '{}/{}'.format(location, candidate)
        if os.path.isfile(full_path):
            # found one
            return full_path

    # couldn't find it
    raise RuntimeError("Didn't find any copies of SharpGen.dll in {}/bin. Did you build it?".format(location))

def compile_file(
                    # Input options
                    source,

                    # SharpGen options
                    wrapper=True,
                    dotnet_framework='net35', output_kind='console', platform='x86',
                    optimization=True, assembly_name=None, class_name=None,
                    confuse=None, out=None,

                    # Additional SharpGen options (passed through raw)
                    additional_options=None,

                    # Resources/references
                    resources=None,
                    references=None,

                    # Cache options
                    cache=None,
                    overwrite_cache=False,
                    no_cache_write=False,

                    # Dependency info
                    sharpgen_location=None
                ):
    """
    Compile a file using SharpGen.

    :param source: File name to compile
    :param wrapper: Use SharpGen's code wrapper (inverse of the dcsync/SharpGen fork's --no-wrapper)
    :param dotnet_framework: .NET version to compile against (net35 or net40) (SharpGen's --dotnet-framework)
    :param output_kind: Type of output (console or dll) (SharpGen's --output-kind)
    :param platform: Platform to compile for (any/AnyCpy, x86, or x64) (SharpGen's --platform)
    :param optimization: Perform code optimization (inverse of SharpGen's --no-optimization)
    :param assembly_name: Name of generated assembly (SharpGen's --assembly-name)
    :param class_name: Name of generated class (SharpGen's --class-name)
    :param confuse: ConfuserEx configuration file (SharpGen's --confuse). Set a
                    default for this option with `set_confuse(<file>)`.
    :param out: Output file (SharpGen's --file)
    :param additional_options: List of additional SharpGen options/flags
                               (passed through raw)

    :param resources: List of resources to include (by Name). These must be
                      present in your resources.yml file.
    :param references: List of references to include (by File). These must be
                       present in your references.yml file.

    :param cache: Use the build cache. Not setting this option will use the
                  global settings (`enable_cache()`/`disable_cache()`).
    :param overwrite_cache: Force overwriting this build in the cache (disable
                            cache retrieval but not writing)
    :param no_cache_write: Allow for cache retrieval but not cache writing

    :param sharpgen_location: Location of SharpGen directory (default: location
                              passed to `set_location()` or PyCobalt repo copy)

    :return: Tuple containing (out, cached) where `out` is the name of the
             output file and `cached` is a boolean containing True if the build
             is from the build cache
    :raises: RuntimeError: If one of the options is invalid
    """

    if not out:
        # use a temporary output file
        if output_kind == 'dll':
            suffix = '.dll'
        else:
            suffix = '.exe'
        out = tempfile.NamedTemporaryFile(prefix='pycobalt.sharpgen.', suffix=suffix, delete=False).name

    # build cache settings
    global _cache_enabled
    if cache is None:
        # use global settings
        cache_write = _cache_enabled and not no_cache_write
        cache_retrieval = _cache_enabled and not overwrite_cache
    else:
        # override global settings
        cache_write = cache and not no_cache_write
        cache_retrieval = cache and not overwrite_cache

    if cache_retrieval or cache_write:
        # get source hash for build cache
        source_hash = cache_file_hash(source)

    if cache_retrieval:
        # try to retrieve build from cache
        if cache_retrieve(source_hash, out):
            # successfully retrieved file from the cache
            return out, True

    # default sharpgen_location
    if not sharpgen_location:
        global _sharpgen_location
        sharpgen_location = _sharpgen_location

    # find SharpGen.dll
    sharpgen_dll = _find_sharpgen_dll(_sharpgen_location)

    # python 3.5 typing is still too new so I do this instead
    # check dotnet_framework
    if dotnet_framework not in ('net35', 'net40'):
        raise RuntimeError('compile_file: dotnet_framework must be net35 or net40')

    # check output_kind
    if output_kind not in ('console', 'dll'):
        raise RuntimeError('compile_file: output_kind must be console or dll')

    # check platform
    platform = platform.lower()
    if platform not in ('any', 'anycpy', 'x86', 'x64'):
        raise RuntimeError('compile_file: platform must be any/AnyCpy, x86, or x64')
    if platform in ('any', 'anycpy'):
        platform = 'AnyCpy'

    args = ['dotnet', sharpgen_dll,
            '--dotnet-framework', dotnet_framework,
            '--output-kind', output_kind,
            '--platform', platform]

    # other options
    if not wrapper:
        args.append('--no-wrapper')

    if not optimization:
        args.append('--no-optimization')

    if assembly_name:
        args += ['--assembly-name', assembly_name]

    if class_name:
        args += ['--class-name', class_name]

    global _confuserex_config
    if confuse:
        args += ['--confuse', confuse]
    elif _confuserex_config:
        # see `set_confuse()`
        args += ['--confuse', _confuserex_config]

    if additional_options:
        args += additional_options

    resources_yaml_file = '{}/Resources/resources.yml'.format(sharpgen_location)
    references_yaml_file = '{}/References/references.yml'.format(sharpgen_location)

    original_resources_yaml = None
    original_references_yaml = None

    def filter_yaml(yaml, key, enabled_items):
        """
        Filter references.yml or resources.yml

        :param yaml: Original yaml
        :param key: Key to filter on
        :param enabled_items: Values to filter on
        :return: Filtered yaml
        """

        # parse content
        items = utils.yaml_basic_load(yaml)

        # filter out the items we want
        for item in items:
            if item[key].lower() in enabled_items.lower():
                item['Enabled'] = 'true'
            else:
                item['Enabled'] = 'false'

        # dump new yaml
        return utils.yaml_basic_dump(items)

    # this is a bit ugly but I can't think of a better way to do it
    try:
        # pick resources?
        if resources is not None:
            # read in original yaml
            with open(resources_yaml_file, 'r') as fp:
                original_resources_yaml = fp.read()

            # filter yaml
            new_yaml = filter_yaml(original_resources_yaml, 'Name', resources)

            # overwrite yaml file with new yaml
            with open(resources_yaml_file, 'w+') as fp:
                fp.write(new_yaml)

        # pick references?
        if references is not None:
            # read in original yaml
            with open(references_yaml_file, 'r') as fp:
                original_references_yaml = fp.read()

            # filter yaml
            new_yaml = filter_yaml(original_references_yaml, 'File', references)

            # overwrite yaml file with new yaml
            with open(references_yaml_file, 'w+') as fp:
                fp.write(new_yaml)

        args += ['--file', out,
                 '--source-file', source]

        engine.debug('running SharpGen: ' + ' '.join(args)) 
        code, output, _ = helpers.capture(args, merge_stderr=True)

        # debug
        #output = output.decode()
        #engine.debug('SharpGen return: {}'.format(code))
        #engine.debug('SharpGen output: {}'.format(output))

        if code != 0 or not os.path.getsize(out):
            # SharpGen failed
            output = output.decode()
            engine.message('SharpGen invocation: {}'.format(' '.join(args)))
            engine.message('SharpGen error code: {}'.format(code))
            engine.message('SharpGen error output:\n' + output)
            engine.message('End SharpGen error output')
            raise RuntimeError('SharpGen failed with code {}'.format(code))
    finally:
        if original_resources_yaml:
            # set the resources yaml back to the original
            with open(resources_yaml_file, 'w+') as fp:
                fp.write(original_resources_yaml)

        if original_references_yaml:
            # set the references yaml back to the original
            with open(references_yaml_file, 'w+') as fp:
                fp.write(original_references_yaml)

    if cache_write and os.path.isfile(out):
        # copy build to the cache
        _cache_add(source_hash, out)

    return out, False

def compile(code, **kwargs):
    """
    Compile some C# code

    :param code: Code to compile
    :param **kwargs: Compilation arguments passed to `compile_file`
    :return: Tuple containing (out, cached) where `out` is the name of the
             output file and `cached` is a boolean containing True if the build
             is from the build cache
    """

    with tempfile.NamedTemporaryFile('w+', prefix='pycobalt.sharpgen.', suffix='.cs') as temp:
        temp.write(code)
        temp.flush()
        return compile_file(temp.name, **kwargs)

def execute_file(bid, source, *args, **kwargs):
    """
    Compile and execute a C# file

    :param bid: Beacon to execute on
    :param source: Source file to compile
    :param *args: Arguments used for execution
    :param **kwargs: Compilation arguments passed to `compile_file`. Don't use
                     the `out` flag because this will delete the exe after.
    :return: True if the executed build was from the build cache
    """

    compiled, from_cache = compile_file(source, **kwargs)
    # TODO quote args correctly
    quoted_args = ' '.join(args)
    aggressor.bexecute_assembly(bid, compiled, quoted_args, silent=True)
    os.remove(compiled)

    return from_cache

def execute(bid, code, *args, **kwargs):
    """
    Compile and execute some C# code

    :param bid: Beacon to execute on
    :param code: Code to compile
    :param *args: Arguments used for execution
    :param **kwargs: Compilation arguments passed to `compile_file`. Don't use
                     the `out` flag because this will delete the exe after.
    :return: True if the executed build was from the build cache
    """

    compiled, from_cache = compile(code, **kwargs)
    # TODO is there a way to quote arguments
    quoted_args = ' '.join(args)
    aggressor.bexecute_assembly(bid, compiled, quoted_args, silent=True)
    os.remove(compiled)

    return from_cache
