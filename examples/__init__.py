import sys
import os

def basedir(append='', relative=__file__):
    """
    Get base directory relative to 'relative' or __file__
    """
    return os.path.realpath(os.path.dirname(relative)) + '/' + append

sys.path.insert(0, basedir('..'))
