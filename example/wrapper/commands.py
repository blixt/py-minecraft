# -*- coding: utf-8 -*-

from minecraft.packet import *
from minecraft.wrapper import command

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
    if len(args) > 1:
        name = args[1]
        location = _locations.get(name)

    if action in ('d', 'rm', 'del', 'delete', 'remove'):
        if location:
            if location.owner == player:
                del _locations[name]
                player.message(u'§6Deleted location §f%s§6.' % name)
            else:
                player.message(u'§6You may not delete that location.')
        else:
            player.message(u'§6That location does not exist.')
    elif action in ('g', 'go', 'goto'):
        if location:
            # The server doesn't care how far you move in one go. However, it
            # does care about whether there are blocks in the way. So to be
            # able to warp past mountains etc., first move the player up to 128
            # (above the block placement limit) and then move the player to the
            # desired X, Z and then move the player to the appropriate Y.

            # Move the player up.
            kwargs = dict(x=player.x, y=128, z=player.z, stance=129.62,
                          yaw=0.0, pitch=0.0, on_ground=False)
            player.inject(MoveAndLook(**kwargs))

            # Move the player to X, Z.
            kwargs['x'] = location.x
            kwargs['z'] = location.z
            player.inject(MoveAndLook(**kwargs))

            # Move the player down.
            kwargs['y'] = location.y
            kwargs['stance'] = kwargs['y'] + 1.62
            player.inject(MoveAndLook(**kwargs))

            # Tell the client its new position.
            player.send(MoveAndLookCorrection(**kwargs))
        else:
            player.message(u'§6That location does not exist.')
    elif action in ('l', 'ls', 'list'):
        if _locations:
            player.message(u'§6, §f'.join(_locations))
        else:
            player.message(u'§6There are no locations to list.')
    elif action in ('s', 'save'):
        if location:
            if location.owner == player:
                location.x = player.x
                location.y = player.y
                location.z = player.z
                player.message(u'§6Updated location §f%s§6.' % name)
            else:
                player.message(u'§6You may not update that location.')
        else:
            location = Location(player, name)
            player.message(u'§6Created location §f%s§6.' % name)
    else:
        player.message(u'§6Action should be one of list, save, goto, delete.')
