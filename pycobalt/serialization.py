import json
import base64

import pycobalt.callbacks as callbacks

# for serializing callbacks
_serialize_callback_prefix = '<<--pycobalt callback-->> '
# for serializing bytes
_serialize_bytes_prefix = '<<--pycobalt bytes-->> '

def _serialize_special(item):
    """
    Serialize and register callbacks and other special objects
    """

    if isinstance(item, list) or isinstance(item, tuple):
        # recurse lists
        new_list = []
        for child in item:
            new_list.append(_serialize_special(child))
        return new_list
    elif isinstance(item, dict):
        # recurse dicts
        new_dict = {}
        for key, value in item.items():
            new_dict[key] = _serialize_special(value)
        return new_dict
    elif callable(item):
        # serialize callbacks
        func_name = callbacks.name(item)
        if not func_name:
            func_name = callbacks.register(item)
        return _serialize_callback_prefix + func_name
    elif isinstance(item, bytes):
        # serialize bytes
        return _serialize_bytes_prefix + base64.b64encode(item).decode()
    else:
        # item is json-serializable
        return item

def serialized(item):
    """
    Serialize messages. This serializes special objects before serializing with
    json.
    """

    return json.dumps(_serialize_special(item))
