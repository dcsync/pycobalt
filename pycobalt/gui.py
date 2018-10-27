"""
A menu is made up of a dictionary tree

Fields include:
  - type: type of item
  - name: name of item (or menu text)
  - callback: callback (called before children are produced)
  - children: child items

Types include:
  - popup
  - menu
  - item
  - insert_menu
  - separator

Example:

  menu = { 'type': 'popup', 'name': 'beacon_top', 'callback': foo, 'children': [
      {'type': 'menu', 'name': 'Thing', 'children': [
          {'type': 'item', 'name': 'Stuff', 'callback': open_gui_thing}
      ]}
  ]}
  gui.register(menu)

Example using the helper functions:

  menu = gui.popup('beacon_top', callback=foo, children=[
      gui.menu('Thing', children=[
          gui.item('Stuff', callback=open_gui_thing)
      ])
  ])
  gui.register(menu)

The callback is passed cobaltstrike's @_ array as its arguments
"""

import pycobalt.engine as engine
import pycobalt.aggressor as aggressor

def popup(name, callback=None, children=None):
    """
    Create a popup { } block
    """

    ret = {
            'name': name,
            'type': 'popup'
          }
    if callback:
        ret['callback'] = callback
    if children:
        ret['children'] = children
    return ret

def menu(name, callback=None, children=None):
    """
    Create a menu { } block
    """

    ret = {
            'name': name,
            'type': 'menu'
          }
    if callback:
        ret['callback'] = callback
    if children:
        ret['children'] = children
    return ret

def item(name, callback=None):
    """
    Create an item
    """

    ret = {
            'name': name,
            'type': 'item'
          }
    if callback:
        ret['callback'] = callback
    return ret

def insert_menu(name):
    """
    Create a menu insertion
    """

    ret = {
            'name': name,
            'type': 'insert_menu'
          }
    return ret

def separator():
    """
    Create a separator
    """

    ret = {
            'type': 'separator'
          }
    return ret

def check(menu):
    """
    Check to make sure a menu looks valid
    """

    # Check children
    if 'children' in menu:
        for child in menu['children']:
            if not check(child):
                return False

    # Type is required
    if 'type' not in menu:
        return False
    
    # Check type
    if menu['type'] not in ['popup', 'menu', 'item', 'insert_menu', 'separator']:
        return False

    # Name is required for most
    if 'name' not in menu and menu['type'] != 'separator':
        return False

    # Items of type insert_menu cannot have callbacks or children
    if menu['type'] == 'insert_menu' and ('callback' in menu or 'children' in menu):
        return False

    # Items of type item cannot have children
    if menu['type'] == 'item' and 'children' in menu:
        return False

    # Callback must be callable
    if 'callback' in menu and not callable(menu['callback']):
        return False
    
    return True

def register(menu):
    """
    Check and register a menu

    To bypass check() call engine.menu() directly.
    """

    # check it
    if not check(menu):
        raise RuntimeError('Invalid menu: {}'.format(menu))

    engine.menu(menu)
