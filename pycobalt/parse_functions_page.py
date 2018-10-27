#!/usr/bin/env python3

"""
Generate aggressor.py based on the aggressor documentation functions.html page.
"""

import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.cobaltstrike.com/aggressor-script/functions.html'
out = 'aggressor.py'

sleep_functions = [
    'print',
    'println',
]

def main():
    print('downloading list')

    data = ''
    data += '''\
"""
For calling aggressor functions

Warning: This file is auto-generated by ./parse_functions_page.py
"""

import pycobalt.engine as engine

'''

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    print('parsing')

    # <h2><a href="#-is64">-is64</a></h2>
    functions = {}
    container = soup.find('div', {'class': 'col-lg-12'})
    
    # get names
    names = []
    for h2 in container.find_all('h2'):
        for a in h2.find_all('a'):
            names.append(a.text)

    # get docs
    docs = []
    for div in container.find_all('div'):
        doc = '\n'.join(['    ' + line.rstrip().encode('utf-8', 'ignore').decode('utf-8', 'ignore') for line in div.text.splitlines()])
        docs.append(doc)

    # zip together
    for name, doc in zip(names, docs):
        functions[name] = doc

    # add sleep functions
    for func in sleep_functions:
        functions[func] = None

    print('found {} functions'.format(len(functions)))

    for func, doc in functions.items():
        #max_arg = 0

        # find max arg
        #if '# Arguments' in doc:
        #    for match in re.finditer('\$([0-9]+)', doc):
        #        num = int(match.group(1))
        #        max_arg = max(num, max_arg)
        if not doc:
            doc = ''

        pyname = func.replace('-', '')
        if func.startswith('b'):
            data += '''
def {pyname}(*args, silent=False, fork=False):
    r""""{doc}"""

    return engine.call('{name}', args, silent=silent, fork=fork)

'''.format(name=func, pyname=pyname, doc=doc)
        else:
            data += '''
def {pyname}(*args, fork=False):
    r"""{doc}"""

    return engine.call('{name}', args, fork=fork)

'''.format(name=func, pyname=pyname, doc=doc)

    print('writing to {}'.format(out))
    with open(out, 'w+') as out_fp:
        out_fp.write(data)

if __name__ == '__main__':
    main()