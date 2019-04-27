"""
Helper functions for using cobbr's SharpGen

See examples/sharpgen.py for a working set of compile/exec console commands and
aliases. Refer to `README.md` for more usage info.

For more information about SharpGen see:
  - https://posts.specterops.io/operational-challenges-in-offensive-c-355bd232a200
  - https://github.com/cobbr/SharpGen
"""

import textwrap
import tempfile
import hashlib
import os

import pycobalt.utils as utils
import pycobalt.engine as engine
import pycobalt.callbacks as callbacks
import pycobalt.aggressor as aggressor
import pycobalt.helpers as helpers

# Some directly configurable defaults
default_libraries = [
    'System',
    'System.IO',
    'System.Text',
    'System.Linq',
    'System.Security.Principal',
    'System.Collections.Generic',
    'SharpSploit.Credentials',
    'SharpSploit.Enumeration',
    'SharpSploit.Execution',
    'SharpSploit.LateralMovement',
    'SharpSploit.Generic',
    'SharpSploit.Misc',
]
default_runner = 'dotnet'
default_build_paths = ['bin/Release/netcoreapp2.1/SharpGen.dll',
                       'bin/Debug/netcoreapp2.1/SharpGen.dll']

# Location of the sharpgen directory
_sharpgen_location = utils.basedir('../third_party/SharpGen')

# Cache options
_cache_location = '{}/Cache'.format(_sharpgen_location)
_default_cache_enabled = False
_default_cache_overwrite = False

# ConfuserEx options
_default_confuser_config = None
_default_confuser_protections = None

# not currently used. needs more testing. enforcement will be optional.
_confuser_protection_support = {
    # XXX re-build and test
    'anti debug': ('net35', 'net40'),

    # crashed in mono, "Failed to run module constructor due to (null) assembly"
    # XXX re-build and test
    'anti dump': ('net35', 'net40'),

    # XXX re-build and test
    'anti ildasm': ('net35', 'net40'),

    # crashed in mono, "Failed to run module constructor due to (null) assembly"
    # XXX re-build and test
    'anti tamper': ('net35', 'net40'),

    # crashed in .NET 3.5 but not 4.0, missing System.Reflection.Assembly.op_Equality
    'constants': ('net40'),

    # tested with .NET 3.5 and 4.0
    'ctrl flow': ('net35', 'net40'),

    # seems to break everywhere with a segfault?
    'invalid metadata': (),

    # failed to build due to .NET 3.5 missing System.Reflection.MethodInfo.op_Inequality
    'ref proxy': ('net40'),

    # tested with .NET 3.5 and 4.0
    'rename': ('net35', 'net40'),

    # tested with .NET 3.5 and 4.0
    'resources': ('net35', 'net40'),

    # only in XenocodeRCE and mkaring forks
    #'typescramble': ('net35', 'net40'),
}

# will work on this later
#_confuser_protection_params = {
#    'anti debug': {'mode': ('safe', 'win32', 'antinet')},
#    'anti dump': {},
#    'anti ildasm': {},
#    'anti tamper': {'mode': ('normal', 'jit'), 'key': ('normal', 'dynamic')},
#    'constants': {},
#    'ctrl flow': {},
#    'invalid metadata': {},
#    'ref proxy': {},
#    'rename': {},
#    'resources': {},
#}

# Special value, indicates that no change should be made to the SharpGen
# resources.yml and references.yml files.
no_changes = object()

# Other default options
_default_resources = no_changes
_default_references = no_changes
_default_dotnet_framework = 'net35'

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

    global _default_cache_enabled

    _default_cache_enabled = True

    if not _cache_location:
        # reset to <SharpGen>/Cache
        set_cache_location()

def disable_cache():
    """
    Disable the build cache
    """

    global _default_cache_enabled

    _default_cache_enabled = False

def enable_cache_overwrite():
    """
    Enable cache overwrite mode
    """

    global _default_cache_overwrite

    _default_cache_overwrite = True

def disable_cache_overwrite():
    """
    Disable cache overwrite mode
    """

    global _default_cache_overwrite

    _default_cache_overwrite = False

def set_confuser_config(config):
    """
    Set a default location for ConfuserEx config. This is so you don't have to
    keep passing the `confuser_config=` compilation keyword argument.

    This setting will disable anything set with `set_confuser_protections()`
    but is overridden by the `confuser_protections=` keyword argument.

    :param config: ConfuserEx config file
    """

    global _default_confuser_config
    global _default_confuser_protections

    _default_confuser_config = config
    _default_confuser_protections = None

def set_confuser_protections(protections):
    """
    Set a the default ConfuserEx protections. This is so you don't have to
    keep passing the `confuser_protections=` compilation keyword argument.

    This setting will disable anything set with `set_confuser_config()`
    but is overridden by the `confuser_config=` keyword argument.

    The protections passed may be either:
     - A list containing protection names
     - A dictionary of dictionaries containing {protection: {argument, value}}

    Example calls:
    
        # use protections resources and rename
        sharpgen.set_confuser_protections(['resources', 'rename'])

        # use protections resources and rename with mode=dynamic argument for
        # resources
        sharpgen.set_confuser_protections({'resources': {'mode': 'dynamic'},
                                           'rename': None})

    :param protections: ConfuserEx protections file
    """

    global _default_confuser_config
    global _default_confuser_protections

    _default_confuser_protections = protections
    _default_confuser_config = None

def set_resources(resources=None):
    """
    Set the resource whitelist default. Call with no arguments to disable all
    resources by default.

    The `resources=` argument overrides this. The `add_resources=` argument
    adds to the list passed here.

    Use the special value `sharpgen.no_changes` to indicate that no changes
    should be made to the `resources.yml` file.

    :param resources: Default resouce whitelist
    """

    global _default_resources

    if not resources:
        resources = []

    _default_resources = resources

def set_references(references=['mscorlib.dll', 'System.dll', 'System.Core.dll']):
    """
    Set the reference whitelist default. Call with no arguments disable all
    references except mscorlib.dll, System.dll, and System.Core.dll by default.

    The `references=` argument overrides this. The `add_references=` argument
    adds to the list passed here.

    Use the special value `sharpgen.no_changes` to indicate that no changes
    should be made to the `references.yml` file.

    :param references: Default reference whitelist
    """

    global _default_references

    if not references:
        references = []

    _default_references = references

def set_dotnet_framework(version):
    """
    Set the default .NET Framework version. This is overridden by the
    `dotnet_framework=` keyword argument.

    :param version: .NET Framework version ('net35' or 'net40')
    """

    global _default_dotnet_framework

    # check dotnet_framework
    if version not in ('net35', 'net40'):
        raise RuntimeError('Argument version must be net35 or net40')

    _default_dotnet_framework = version

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

    return hashlib.md5(source.encode()).hexdigest()

def cache_file_hash(source_file):
    """
    Get a hash of some source code file

    :param source: Source code file
    :return: MD5 hash of source code
    """

    with open(source_file, 'r') as fp:
        return cache_source_hash(fp.read())

def _find_sharpgen_dll(location, paths=None):
    """
    Find a SharpGen DLL in a SharpGen directory

    :param location: Location of SharpGen directory
    :param paths: Paths to search within the SharpGen directory (default:
                  sharpgen.default_build_paths)
    :return: Location of SharpGen DLL
    :raises: RuntimeError: If a copy of the DLL isn't found
    """

    # make sure SharpGen directory exists
    if not location or not os.path.isdir(location):
        raise RuntimeError("SharpGen directory '{}' does not exist".format(_sharpgen_location))

    if not paths:
        # default paths are sharpgen.default_build_paths
        global default_build_paths
        paths = default_build_paths

    # look for dlls
    for path in paths:
        full_path = '{}/{}'.format(location, path)
        if os.path.isfile(full_path):
            # found one
            return full_path

    # couldn't find it
    raise RuntimeError("Didn't find any copies of SharpGen.dll in {}/bin. Did you build it?".format(location))

def wrap_code(source, function_name='Main', function_type='void',
              class_name=None, libraries=None, add_return=True):
    """
    Wrap a piece of source code in a class and function, similar to what
    SharpGen does. We perform the function wrapping here in order to have more
    control over the final product.

    :param source: Source to wrap
    :param function_name: Function name (default: Main)
    :param function_type: Function type (default: void)
    :param class_name: Class name (default: random)
    :param libraries: List of librares to use (default: sharpgen.default_libraries)
    :param add_return: Add return statement if needed (default: True)
    :return: Generated code
    """

    if not class_name:
        # default class_name is random
        class_name = utils.random_string(5, 10)

    if not libraries:
        # default libraries are sharpgen.default_libraries
        global default_libraries
        libraries = default_libraries

    # add return statement. not sure why this is necessary.
    if add_return and function_type == 'void' and 'return;' not in source:
        source += '\nreturn;'

    out = ''

    # add libraries
    for library in libraries:
        out += 'using {};\n'.format(library)
    out += '\n'

    # indent the code
    source = '\n'.join([' ' * 12 + line for line in source.splitlines()])

    # wrap the code
    out += helpers.fix_multiline_string("""
    public static class {class_name}
    {{
        static {function_type} {function_name}(string[] args)
        {{
{source}
        }}
    }}
    """.format(source=source, function_name=function_name,
               class_name=class_name, function_type=function_type))

    return out

def generate_confuser_config(protections):
    """
    Generate a ConfuserEx config file.

    The protections passed may be either:
     - A list containing protection names
     - A dictionary of dictionaries containing {protection: {argument, value}}

    :param protections: List of protection names or a dictionary of
                        dictionaries containing protections and their
                        arguments.
    :return: Generated ConfuserEx config file
    """

    config = textwrap.dedent("""\
        <project baseDir="{0}" outputDir="{1}" xmlns="http://confuser.codeplex.com">
          <module path="{2}">
            <rule pattern="true" inherit="false">
        """)

    indent = ' ' * 6
    if isinstance(protections, dict):
        # protections is a dictionary of dictionaries
        # format is {protection: {argument, value}}
        for protection, arguments in protections.items():
            config += indent + '<protection id="{}">\n'.format(protection)

            # generate arguments
            if arguments:
                if not isinstance(arguments, dict):
                    raise RuntimeError('Invalid arguments passed for ConfuserEx protection: {}'.format(protection))

                for name, value in arguments.items():
                    config += indent + '  <argument name="{}" value="{}" />\n'.format(name, value)

            config += indent + '</protection>\n'
    else:
        # protections is just a list of protections with no arguments
        for protection in protections:
            config += indent + '<protection id="{}" />\n'.format(protection)

    config += textwrap.dedent("""\
            </rule>
          </module>
        </project>
        """)

    return config

def compile(
                    # Input options
                    source,

                    # Wrapper options
                    use_wrapper=True,
                    assembly_name=None,
                    class_name=None,
                    function_name=None,
                    function_type=None,
                    libraries=None,

                    # Compilation options
                    output_kind='console',
                    platform='AnyCpu',
                    dotnet_framework=None, 
                    optimization=True,
                    out=None,

                    # Confuser options
                    confuser_config=None,
                    confuser_protections=None,

                    # Additional SharpGen options (passed through raw)
                    additional_options=None,

                    # Resources/references
                    resources=None,
                    references=None,
                    add_resources=None,
                    add_references=None,

                    # Cache options
                    cache=None,
                    cache_overwrite=None,
                    no_cache_write=False,

                    # Dependency info
                    sharpgen_location=None,
                    sharpgen_runner=None
                ):
    """
    Compile some C# code using SharpGen.

    :param source: Source to compile

    :param use_wrapper: Use a class and function Main code wrapper (default: True)
    :param class_name: Name of generated class (default: random)
    :param function_name: Name of function for wrapper (default: Main for .exe, Execute for .dll)
    :param function_type: Function return type (default: void for .exe, object for .dll)
    :param libraries: Libraries to use (C# `using`) in the wrapper (default:
                      `sharpgen.default_libraries`).

    :param assembly_name: Name of generated assembly (default: random)
    :param output_kind: Type of output (exe/console or dll/library) (default: console)
    :param platform: Platform to compile for (any/AnyCpu, x86, or x64) (default: AnyCpu)
    :param confuser_config: ConfuserEx configuration file. Set a default for this
                            option with `set_confuser_config(<file>)`.
    :param confuser_protections: ConfuserEx protections to enable. Setting this
                                 argument will generate a temporary ConfuserEx
                                 config file for this build. For more
                                 information and to set a default for this
                                 option see `set_confuser_protections(<protections>)`.
    :param dotnet_framework: .NET Framework version to compile against
                             (net35 or net40) (default: value passed to
                             `set_dotnet_framework(<version>)` or net35)
    :param optimization: Perform code optimization (default: True)
    :param out: Output file (default: file in /tmp)

    :param additional_options: List of additional SharpGen options/flags
                               (passed through raw)

    :param resources: List of resources to whitelist (by Name). This option
                      temporarily modifies your `resources.yml` file so listed
                      resources must be present in that file. By default
                      resources.yml will not be touched. Call
                      `set_resources(<resources>)` to change the default.
    :param references: List of references to whitelist (by File). This option
                      temporarily modifies your `references.yml` file so listed
                      references must be present in that file. By default
                       references.yml will not be touched. Call
                      `set_references(<references>)` to change the default.
    :param add_resources: List of resources to add, on top of the defaults (see
                          `set_resources(<resources>)`)
    :param add_references: List of references to add, on top of the defaults
                           (see `set_references(<references>)`)

    :param cache: Use the build cache. Not setting this option will use the
                  global settings (`enable_cache()`/`disable_cache()`). By
                  default the build cache is off.
    :param cache_overwrite: Force overwriting this build in the cache (disable
                            cache retrieval but not writing). The default is
                            `False` unless `enable_cache_overwrite()` is called.
    :param no_cache_write: Allow for cache retrieval but not cache writing

    :param sharpgen_location: Location of SharpGen directory (default: location
                              passed to `set_location()` or PyCobalt repo copy)
    :param sharpgen_runner: Program used to run the SharpGen dll (default:
                            sharpgen.default_runner or 'dotnet')

    :return: Tuple containing (out, cached) where `out` is the name of the
             output file and `cached` is a boolean containing True if the build
             is from the build cache
    :raises RuntimeError: If one of the options is invalid
    """

    # check output_kind
    if output_kind not in ('exe', 'console', 'dll', 'library'):
        raise RuntimeError('Argument output_kind must be exe/console or dll/library')
    if output_kind == 'exe':
        output_kind = 'console'
    if output_kind == 'library':
        output_kind = 'dll'

    # check dotnet_framework
    if not dotnet_framework:
        global _default_dotnet_framework
        dotnet_framework = _default_dotnet_framework
    if dotnet_framework not in ('net35', 'net40'):
        raise RuntimeError('Argument dotnet_framework must be net35 or net40')

    if not out:
        # use a temporary output file
        if output_kind == 'dll':
            suffix = '_build.dll'
        else:
            suffix = '_build.exe'
        out = tempfile.NamedTemporaryFile(prefix='pycobalt.sharpgen.', suffix=suffix, delete=False).name

    # cache settings
    # set default cache_overwrite
    global _default_cache_overwrite
    if not cache_overwrite is None:
        cache_overwrite = _default_cache_overwrite

    # determine cache write and retrieval settings based on `cache`,
    # `cache_overwrite`, and `no_cache_write`
    global _default_cache_enabled
    if cache is None:
        # use global settings
        cache_write = _default_cache_enabled and not no_cache_write
        cache_retrieval = _default_cache_enabled and not cache_overwrite
    else:
        # override global settings
        cache_write = cache and not no_cache_write
        cache_retrieval = cache and not cache_overwrite

    if cache_retrieval or cache_write:
        # get cache source hash
        source_hash = cache_source_hash(source)

    if cache_retrieval:
        # try to retrieve build from cache
        if cache_retrieve(source_hash, out):
            # successfully retrieved file from the cache
            engine.debug('Retrieved {} from the SharpGen cache'.format(source_hash))
            return out, True

    # default sharpgen_location
    if not sharpgen_location:
        global _sharpgen_location
        sharpgen_location = _sharpgen_location

    # find SharpGen.dll
    sharpgen_dll = _find_sharpgen_dll(_sharpgen_location)

    # wrapper options
    if use_wrapper:
        if not function_name:
            if output_kind == 'dll':
                function_name = 'Execute'
            else:
                function_name = 'Main'

        if not function_type:
            if output_kind == 'dll':
                function_type = 'object'
            else:
                function_type = 'void'

        source = wrap_code(source, function_name=function_name,
                           function_type=function_type, class_name=class_name,
                           libraries=libraries)

    # check platform
    platform = platform.lower()
    if platform not in ('any', 'anycpu', 'x86', 'x64'):
        raise RuntimeError('Argument platform must be any/AnyCpu, x86, or x64')
    if platform in ('any', 'anycpu'):
        platform = 'AnyCpu'

    args = []

    # compiler options
    args += ['--dotnet-framework', dotnet_framework,
             '--output-kind', output_kind,
             '--platform', platform]

    if not optimization:
        args.append('--no-optimization')

    if assembly_name:
        args += ['--assembly-name', assembly_name]

    # ConfuserEx config
    # if neither flag is passed, pick a global default
    if not (confuser_config or confuser_protections):
        global _default_confuser_config
        global _default_confuser_protections
        if _default_confuser_config:
            confuser_config = _default_confuser_config
        elif _default_confuser_protections:
            confuser_protections = _default_confuser_protections

    # check to make sure both arguments were not passed
    if confuser_protections and confuser_config:
        raise RuntimeError('Arguments confuser_protections and confuser_config are not compatible together')

    # if confuser_protections is passed generate a ConfuserEx config file
    confuser_tempfile = None
    if confuser_protections:
        # this is cleaned up way at the bottom of the function
        confuser_tempfile = tempfile.NamedTemporaryFile('w+', prefix='pycobalt.sharpgen.', suffix='_confuser_config.cr')

        config = generate_confuser_config(confuser_protections)

        engine.debug('Confuser config: ' + config)

        confuser_tempfile.write(config)
        confuser_tempfile.flush()

        confuser_config = confuser_tempfile.name

    if confuser_config:
        args += ['--confuse', confuser_config]

    # additional options
    if additional_options:
        args += additional_options

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
            if item[key].lower() in [item.lower() for item in enabled_items]:
                item['Enabled'] = 'true'
            else:
                item['Enabled'] = 'false'

        # dump new yaml
        return utils.yaml_basic_dump(items)

    resources_yaml_file = '{}/Resources/resources.yml'.format(sharpgen_location)
    references_yaml_file = '{}/References/references.yml'.format(sharpgen_location)

    original_resources_yaml = None
    original_references_yaml = None

    # figure out resources behavior
    global _default_resources
    if resources is None:
        resources = _default_resources

    if add_resources:
        if resources is None:
            resources = add_resources
        else:
            resources.extend(add_resources)

    # figure out references behavior
    global _default_references
    if references is None:
        references = _default_references

    if add_references:
        if references is None:
            references = add_references
        else:
            references.extend(add_references)

    # this feels a bit ugly but I can't think of a better way to do it
    try:
        # pick resources?
        if resources is not no_changes:
            # read in original yaml
            with open(resources_yaml_file, 'r') as fp:
                original_resources_yaml = fp.read()

            # filter yaml
            new_yaml = filter_yaml(original_resources_yaml, 'Name', resources)

            engine.debug('Temporarily overwriting {} with:\n{}'.format(resources_yaml_file, new_yaml))

            # overwrite yaml file with new yaml
            with open(resources_yaml_file, 'w+') as fp:
                fp.write(new_yaml)

        # pick references?
        if references is not no_changes:
            # read in original yaml
            with open(references_yaml_file, 'r') as fp:
                original_references_yaml = fp.read()

            # filter yaml
            new_yaml = filter_yaml(original_references_yaml, 'File', references)

            engine.debug('Temporarily overwriting {} with:\n{}'.format(references_yaml_file, new_yaml))

            # overwrite yaml file with new yaml
            with open(references_yaml_file, 'w+') as fp:
                fp.write(new_yaml)

        # write source to a file and build it
        with tempfile.NamedTemporaryFile('w+', prefix='pycobalt.sharpgen.', suffix='_code.cs') as source_file:
            source_file.write(source)
            source_file.flush()

            # in and out
            args += ['--file', out,
                     '--source-file', source_file.name]

            if not sharpgen_runner:
                # default sharpgen_runner is default_runner ('dotnet' by
                # default)
                global default_runner
                sharpgen_runner = default_runner

            # call the SharpGen dll
            args = [sharpgen_runner, sharpgen_dll] + args
            engine.debug('Compiling code: ' + source)
            engine.debug('Running SharpGen: ' + str(args))
            code, output, _ = helpers.capture(args, merge_stderr=True)
            engine.debug('Finished running SharpGen')

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

            if code == -12 and os.path.isfile(out):
                # confuser failed. remove the un-confused output binary.
                try: os.remove(out)
                except: pass

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
        engine.debug('Adding {} to SharpGen cache'.format(source_hash))
        _cache_add(source_hash, out)

    if confuser_tempfile:
        # we have to explictly close the tempfile here. otherwise python's
        # garbage collector might "optimize" out the object early, causing the
        # file to be deleted.
        confuser_tempfile.close()

    return out, False

def compile_file(source_file, **kwargs):
    """
    Compile a file using SharpGen.

    :param source_file: Source file to compile
    :param use_wrapper: Use wrapper (default: False)
    :param **kwargs: Other compilation arguments passed to `compile`.
    :return: Tuple containing (out, cached) where `out` is the name of the
             output file and `cached` is a boolean containing True if the build
             is from the build cache
    :raises RuntimeError: If one of the options is invalid
    """

    # change default use_wrapper value to False
    if 'use_wrapper' not in kwargs:
        kwargs['use_wrapper'] = False

    # read source file
    with open(source_file, 'r') as fp:
        source = fp.read()

    return compile(source, **kwargs)

def execute_file(bid, source, args, delete_after=True, silent=True, **kwargs):
    """
    Compile and execute a C# file

    :param bid: Beacon to execute on
    :param source: Source file to compile
    :param args: Arguments used for execution
    :param delete_after: Delete the generated .exe after (default: True)
    :param silent: Tell `bexecute_assembly` not to print anything (default: True)
    :param **kwargs: Compilation arguments passed to `compile_file`.
    :return: True if the executed build was from the build cache
    :raises RuntimeError: If one of the options is invalid
    """

    # check for `out` argument
    if 'out' in kwargs:
        raise RuntimeError('Do not use the out parameter with execute_file()')

    compiled, from_cache = compile_file(source, **kwargs)

    quoted_args = helpers.execute_assembly_quote(args)
    aggressor.bexecute_assembly(bid, compiled, quoted_args, silent=silent)

    # cleanup
    if delete_after:
        os.remove(compiled)

    return from_cache

def execute(bid, code, args, delete_after=True, silent=True, **kwargs):
    """
    Compile and execute some C# code

    :param bid: Beacon to execute on
    :param code: Code to compile
    :param args: Arguments used for execution
    :param delete_after: Delete the generated .exe after (default: True)
    :param silent: Tell `bexecute_assembly` not to print anything (default: True)
    :param **kwargs: Compilation arguments passed to `compile_file`.
    :return: True if the executed build was from the build cache
    :raises RuntimeError: If one of the options is invalid
    """

    # check for `out` argument
    if 'out' in kwargs:
        raise RuntimeError('Do not use the out parameter with execute()')

    compiled, from_cache = compile(code, **kwargs)

    quoted_args = helpers.execute_assembly_quote(args)
    aggressor.bexecute_assembly(bid, compiled, quoted_args, silent=silent)

    # cleanup
    if delete_after:
        os.remove(compiled)

    return from_cache
