#!/usr/bin/env python3

import setuptools
import os

# change to script directory
os.chdir(os.path.realpath(os.path.dirname(__file__)))

# how hard could it possibly be to include a directory?
#
#  - MANIFEST.in apparently does nothing (even with include_package_data)
#  - package_data apparently does nothing
#  - data_files doesn't work with directories or wildcards
#  - over 500 questions on stackoverflow from people trying to include
#    non-python files in their packages
#  - setuptools maintainer described data_files as 'evil' and suggested
#    deprecating it. had to be convinced that it could be useful for non-library
#    packages
#  - practically no mention of data_files on the setuptools developer's
#    guide
def fucksetuptools(d):
    ret = []
    for folder, subs, files in os.walk(d):
        for filename in files:
            ret.append((folder, ['{}/{}'.format(folder, filename)]))
    return ret

data_files = fucksetuptools('aggressor') + \
             fucksetuptools('examples') + \
             fucksetuptools('third_party') + \
             fucksetuptools('.git')

print('including data_files: ' + str(data_files))

setuptools.setup(
    name='pycobalt',
    version='1.2.0',
    description='Python API for Cobaltstrike',
    url='no',
    author='dcsync',
    author_email='dcsync@protonmail.com',
    data_files=data_files,
    include_package_data=True,
    packages=['pycobalt'],
)
