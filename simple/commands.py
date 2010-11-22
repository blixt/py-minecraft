# -*- coding: utf-8 -*-

from packets.minecraft import *
from wrapper import command

_locations = {}

class Location(object):
    def __init__(self, owner, name):
        self.name = name
        self.owner = owner
        self.x = owner.x
        self.y = owner.y
        self.z = owner.z

        _locations[name] = self

@command('l', 'loc', 'location')
def location(player, packet, *args):
    action = args[0]
    name = args[1]
    location = _locations.get(name)

    if action in ('d', 'del', 'delete'):
        if location:
            if location.owner == player:
                del _locations[name]
                player.message(u'§6Deleted location %s".' % name)
            else:
                player.message(u'§6You may not delete that location.')
        else:
            player.message(u'§6That location does not exist.')
    elif action in ('g', 'go', 'goto'):
        if location:
            kwargs = dict(
                x=location.x, y=location.y, z=location.z,
                stance=location.y + 1.62, yaw=0.0, pitch=0.0,
                on_ground=False)
            player.inject(MoveAndLook(**kwargs))
            player.send(MoveAndLookCorrection(**kwargs))
        else:
            player.message(u'§6That location does not exist.')
    elif action in ('s', 'save'):
        if location:
            if location.owner == player:
                location.x = player.x
                location.y = player.y
                location.z = player.z
                player.message(u'§6Updated location "%s".' % name)
            else:
                player.message(u'§6You may not update that location.')
        else:
            location = Location(player, name)
            player.message(u'§6Created location "%s".' % name)
    else:
        player.message(u'§6Action should be one of save, goto, delete.')
