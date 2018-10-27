#!/usr/bin/env python3

import setuptools
import os

# how hard could it possibly be to include a fucking directory?
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
             fucksetuptools('examples')
print('including data_files: ' + str(data_files))

setuptools.setup(
    name='pycobalt',
    version='1.0.0',
    description='Python API for Cobaltstrike',
    url='no',
    author='anonymous',
    author_email='no',
    data_files=data_files,
    include_package_data=True,
    packages=['pycobalt'],
)
