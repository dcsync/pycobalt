
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

**Arguments**:

- `name`: Name of menu to associate with
- `callback`: Callback to call when opened
- `children`: Child menu items

**Returns**:

Dictionary representing a popup block

## menu
```python
menu(name, callback=None, children=None)
```

Create a menu { } block

**Arguments**:

- `name`: Name/label of menu
- `callback`: Callback to call when opened
- `children`: Child menu items

**Returns**:

Dictionary representing a menu block

## item
```python
item(name, callback=None)
```

Create an item

**Arguments**:

- `name`: Name/label of item
- `callback`: Callback to call when clicked

**Returns**:

Dictionary representing an item

## insert_menu
```python
insert_menu(name)
```

Create a menu insertion

**Arguments**:

- `name`: Name of menu insertion

**Returns**:

Dictionary representing an insert_menu piece

## separator
```python
separator()
```

Create a separator

**Returns**:

Dictionary representing a separator

## check
```python
check(menu)
```

Check to make sure a menu looks valid

**Arguments**:

- `menu`: Menu tree to check

**Returns**:

True if menu tree looks valid

## register
```python
register(menu, check_menu=True)
```

Check and register a menu.

**Arguments**:

- `menu`: Menu tree to register
- `check_menu`: Check whether the menu should be checked first
