# pycobalt.gui

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

## popup
```python
popup(name, callback=None, children=None)
```

Create a popup { } block

:param name: Name of menu to associate with
:param callback: Callback to call when opened
:param children: Child menu items
:return: Dictionary representing a popup block

## menu
```python
menu(name, callback=None, children=None)
```

Create a menu { } block

:param name: Name/label of menu
:param callback: Callback to call when opened
:param children: Child menu items
:return: Dictionary representing a menu block

## item
```python
item(name, callback=None)
```

Create an item

:param name: Name/label of item
:param callback: Callback to call when clicked
:return: Dictionary representing an item

## insert_menu
```python
insert_menu(name)
```

Create a menu insertion

:param name: Name of menu insertion
:return: Dictionary representing an insert_menu piece

## separator
```python
separator()
```

Create a separator

:return: Dictionary representing a separator

## check
```python
check(menu)
```

Check to make sure a menu looks valid

:param menu: Menu tree to check
:return: True if menu tree looks valid

## register
```python
register(menu, check_menu=True)
```

Check and register a menu.

:param menu: Menu tree to register
:param check_menu: Check whether the menu should be checked first

