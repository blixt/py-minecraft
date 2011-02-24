# -*- coding: utf-8 -*-

import json
import os
import platform

PATH = 'wrapper.json'
BACKUP_PATH = 'wrapper.backup.json'

_data = None
_defaults = {
    'port': 25564,
    'groups': {
        '@default': {
            'permissions': {
                'place-blocks': False}}},
    'players': {
        '@default': {'group': 'Guest'}}}

class PartialConfig(object):
    """An object returned by the get function if trying to get a config value
    that has a structure below it. This simplifies getting multiple values with
    the same base path.

    >>> player = get('players', 'TestPlayer')
    >>> player.get('group')
    'Guest'

    """
    def __init__(self, *path):
        self.path = path

    def get(self, *path):
        assert len(path) >= 1, 'Get must include path'
        return get(*self.path + path)

    def set(self, *path_and_value):
        assert len(path_and_value) >= 2, 'Set must include path and value'
        set(*self.path + path_and_value)

def _get_helper(value, path, try_default=False):
    for piece in path:
        if not isinstance(value, dict):
            return
        next_value = value.get(piece)
        if next_value is None and try_default:
            next_value = value.get('@default')
        value = next_value
    return value

def get(*path):
    assert len(path) >= 1, 'Get must include path'

    value = _get_helper(_data, path)
    if value is None:
        value = _get_helper(_defaults, path, True)

    if isinstance(value, dict):
        return PartialConfig(*path)

    assert value is None or \
        isinstance(value, (basestring, bool, float, int, list, long)), \
        'Invalid value type'

    return value

def load():
    global _data

    try:
        with open(PATH, 'r') as fh:
            data = json.load(fh)
    except:
        try:
            with open(BACKUP_PATH, 'r') as fh:
                data = json.load(fh)
        except:
            data = None

    _data = data or {}

def save():
    with open(BACKUP_PATH, 'w') as fh:
        json.dump(_data, fh, indent=2)
    if platform.system() == 'Windows':
        os.unlink(PATH)
    os.rename(BACKUP_PATH, PATH)

def set(*path_and_value):
    assert len(path_and_value) >= 2, 'Set must include path and value'

    key, value = path_and_value[-2:]
    if value is None:
        raise NotImplemented('Cannot unset values yet')
    if not isinstance(value, (basestring, bool, float, int, list, long)):
        raise TypeError('Invalid value type')

    # Set up the path up to the last dict.
    path = path_and_value[:-2]
    obj = _data
    for piece in path:
        if piece == '@default':
            raise ValueError('@default is an invalid config key')

        next_obj = obj.get(piece)
        if next_obj is None:
            next_obj = obj[piece] = {}
        elif not isinstance(next_obj, dict):
            raise TypeError(
                'Cannot set %s (tried to use value as struct)' %
                '/'.join(path_and_value[:-1]))
        obj = next_obj

    # Set the value.
    if isinstance(obj.get(key), dict):
        raise TypeError(
            'Cannot set %s (tried to set struct to a value)' %
            '/'.join(path_and_value[:-1]))
    obj[key] = value

    save()

load()
