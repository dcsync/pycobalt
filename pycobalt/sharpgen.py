"""
Helper functions for using cobbr's SharpGen

See examples/sharpgen.py for a working set of compile/exec console commands and
aliases. Refer to `README.md` for more usage info.

For more information about SharpGen see:
  - https://posts.specterops.io/operational-challenges-in-offensive-c-355bd232a200
  - https://github.com/cobbr/SharpGen
"""

# TODO cache builds
# TODO add --no-wrapper flag

import tempfile
import os

import pycobalt.utils as utils
import pycobalt.engine as engine
import pycobalt.callbacks as callbacks
import pycobalt.aggressor as aggressor
import pycobalt.helpers as helpers

# Location of the sharpgen directory
_sharpgen_location = utils.basedir('../third_party/SharpGen')

def set_location(location):
    """
    Set the SharpGen directory location. By default it will point to the repo
    copy, which is a git submodule.

    This module will find the SharpGen DLL in <location>/Releases.

    :param location: Location of the SharpGen directory
    """

    global _sharpgen_location
    _sharpgen_location = location

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
        if os.path.exists(full_path):
            # found one
            return full_path

    # couldn't find it
    raise RuntimeError("Didn't find any copies of SharpGen.dll in {}/bin. Did you build it?".format(location))

def compile_file(
                    # Input options
                    source,

                    # SharpGen options
                    dotnet_framework='net35', output_kind='console', platform='x86',
                    no_optimization=False, assembly_name=None, class_name=None,
                    confuse=None, out=None,

                    # Additional SharpGen options (passed through raw)
                    additional_options=None,

                    # Resources/references
                    resources=None,
                    references=None,

                    # Dependency info
                    sharpgen_location=None
                ):
    """
    Compile a file using SharpGen.

    :param source: File name to compile
    :param dotnet_framework: .NET version to compile against (net35 or net40) (SharpGen's --dotnet-framework)
    :param output_kind: Type of output (console or dll) (SharpGen's --output-kind)
    :param platform: Platform to compile for (AnyCpy, x86, or x64) (SharpGen's --platform)
    :param no_optimization: Do not perform code optimization (SharpGen's --no-optimization)
    :param assembly_name: Name of generated assembly (SharpGen's --assembly-name)
    :param class_name: Name of generated class (SharpGen's --class-name)
    :param confuse: ConfuserEx configuration file (SharpGen's --confuse)
    :param out: Output file (SharpGen's --file)
    :param additional_options: List of additional SharpGen options/flags
                               (passed through raw)
    :param resources: List of resources to include (by Name). These must be
                      present in your resources.yml file.
    :param references: List of references to include (by File). These must be
                       present in your references.yml file.
    :param sharpgen_location: Location of SharpGen directory (default: location
                              passed to `set_location()` or repo copy)
    :return: Name of output file
    :raises: RuntimeError: If one of the options is invalid
    """

    global _sharpgen_location

    # default sharpgen_location
    if not sharpgen_location:
        sharpgen_location = _sharpgen_location

    sharpgen_dll = _find_sharpgen_dll(_sharpgen_location)

    # python 3.5 typing is still too new so I do this instead
    # check dotnet_framework
    if dotnet_framework not in ['net35', 'net40']:
        raise RuntimeError('compile_file: dotnet_framework must be net35 or net40')

    # check output_kind
    if output_kind not in ['console', 'dll']:
        raise RuntimeError('compile_file: output_kind must be console or dll')

    # check platform
    if platform not in ['AnyCpy', 'x86', 'x64']:
        raise RuntimeError('compile_file: platform must be AnyCpy, x86, or x64')

    args = ['dotnet', sharpgen_dll,
            '--dotnet-framework', dotnet_framework,
            '--output-kind', output_kind,
            '--platform', platform]

    # other options
    if no_optimization:
        args.append('--no-optimization')

    if assembly_name:
        args += ['--assembly-name', assembly_name]

    if class_name:
        args += ['--class-name', class_name]

    if confuse:
        args += ['--confuse', confuse]

    if additional_options:
        args += additional_options

    resources_yaml_overwritten = False
    references_yaml_overwritten = False

    # this is a bit ugly but I can't think of a better way to do it
    try:
        if resources is not None:
            # pick resources
            resources_yaml_file = '{}/Resources/resources.yml'.format(sharpgen_location)

            # read in original yaml
            with open(resources_yaml_file, 'r') as fp:
                original_resources_yaml = fp.read()

            # and parse it
            items = utils.yaml_basic_load(original_resources_yaml)

            # filter out the items we want
            for item in items:
                if item['Name'] in resources:
                    item['Enabled'] = 'true'
                else:
                    item['Enabled'] = 'false'

            # overwrite yaml file with new yaml
            with open(resources_yaml_file, 'w+') as fp:
                new_yaml = utils.yaml_basic_dump(items)
                fp.write(new_yaml)

            resources_yaml_overwritten = True

        if references is not None:
            # pick references
            references_yaml_file = '{}/References/references.yml'.format(sharpgen_location)

            # read in original yaml
            with open(references_yaml_file, 'r') as fp:
                original_references_yaml = fp.read()

            # and parse it
            items = utils.yaml_basic_load(original_references_yaml)

            # filter out the items we want
            for item in items:
                if item['File'] in references:
                    item['Enabled'] = 'true'
                else:
                    item['Enabled'] = 'false'

            # overwrite yaml file with new yaml
            with open(references_yaml_file, 'w+') as fp:
                new_yaml = utils.yaml_basic_dump(items)
                fp.write(new_yaml)

            references_yaml_overwritten = True

        if not out:
            # use a temporary file
            if output_type == 'dll':
                suffix = '.dll'
            else:
                suffix = '.exe'
            out = tempfile.NamedTemporaryFile(prefix='pycobalt.sharpgen.', suffix=suffix, delete=False).name

        args += ['--file', out,
                 '--source-file', source]

        engine.debug('running SharpGen: ' + ' '.join(args)) 
        code, output, _ = helpers.capture(args, merge_stderr=True)
        output = output.decode()
        engine.debug('SharpGen return: {}'.format(code))
        engine.debug('SharpGen output: {}'.format(output))

        if code != 0:
            # SharpGen failed
            engine.message('SharpGen invocation: {}'.format(' '.join(args)))
            engine.message('SharpGen error code: {}'.format(code))
            engine.message('SharpGen error output:\n' + output)
            engine.message('End SharpGen error output')
            raise RuntimeError('SharpGen failed with code {}'.format(code))
    finally:
        if resources_yaml_overwritten:
            # set the resources yaml back to the original
            with open(resources_yaml_file, 'w+') as fp:
                fp.write(original_resources_yaml)

        if references_yaml_overwritten:
            # set the references yaml back to the original
            with open(references_yaml_file, 'w+') as fp:
                fp.write(original_references_yaml)

    return out

def compile(code, **kwargs):
    """
    Compile some C# code

    :param code: Code to compile
    :param **kwargs: Compilation arguments passed to `compile_file`
    :return: Name of output file
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
    """

    compiled = compile_file(source, **kwargs)
    # TODO quote args correctly
    quoted_args = ' '.join(args)
    aggressor.bexecute_assembly(bid, compiled, quoted_args, silent=True)
    os.remove(compiled)

def execute(bid, code, *args, **kwargs):
    """
    Compile and execute some C# code

    :param bid: Beacon to execute on
    :param code: Code to compile
    :param *args: Arguments used for execution
    :param **kwargs: Compilation arguments passed to `compile_file`. Don't use
                     the `out` flag because this will delete the exe after.
    
    """

    compiled = compile(code, **kwargs)
    # TODO quote args correctly
    quoted_args = ' '.join(args)
    aggressor.bexecute_assembly(bid, compiled, quoted_args, silent=True)
    os.remove(compiled)
