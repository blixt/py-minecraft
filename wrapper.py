# -*- coding: utf-8 -*-

"""Module for functionality for wrapping a Minecraft server and handling its
packets.

"""

import asyncore

import packets
from proxy import MinecraftForwarder

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = [
    'MinecraftWrapperMeta', 'MinecraftWrapper', 'Player', 'packet_handler']

class MinecraftWrapperMeta(type):
    """Meta-class for setting up packet handlers.

    """
    def __new__(cls, name, bases, dct):
        dct['_handlers'] = {}
        t = type.__new__(cls, name, bases, dct)

        for attr_name in dct.keys():
            attr = dct[attr_name]
            if callable(attr) and hasattr(attr, '_p_handler_keys'):
                keys = getattr(attr, '_p_handler_keys')
                for key in keys:
                    if key not in t._handlers:
                        t._handlers[key] = []
                    t._handlers[key].append(attr_name)

        return t

class MinecraftWrapper(object):
    __metaclass__ = MinecraftWrapperMeta

    def __init__(self):
        self.forwarder = MinecraftForwarder(('', 25564), ('localhost', 25565),
            self.handle_packet)
        self._players = {}

    def handle_packet(self, proxy, packet):
        # Set up a Player object for every client.
        key = proxy if packet.direction == packets.TO_SERVER else proxy.other
        if key not in self._players:
            self._players[key] = Player()
        player = self._players[key]

        # Do some special handling of certain packets.
        if isinstance(packet, packets.minecraft.LogIn):
            # This is a client logging in.
            player.username = packet.username

        key = (packet.__class__, packet.direction)
        if key not in self._handlers:
            return

        for handler in self._handlers[key]:
            getattr(self, handler)(player, packet)

    def start(self):
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            self.forwarder.handle_close()

class Player(object):
    def __init__(self):
        self.username = 'Unknown'

def packet_handler(packet_type, directions=0):
    """Descriptor for marking a method as handling a certain packet type in the
    specified direction.

    If no direction is specified, the directions supported by the packet type
    are used.

    """
    if not directions:
        if issubclass(packet_type, packets.PacketToClient):
            directions |= packets.TO_CLIENT
        if issubclass(packet_type, packets.PacketToServer):
            directions |= packets.TO_SERVER

    keys = []
    if directions & packets.TO_CLIENT:
        keys.append((packet_type, packets.TO_CLIENT))
    if directions & packets.TO_SERVER:
        keys.append((packet_type, packets.TO_SERVER))

    assert keys, 'Invalid direction'

    def decorator(handler):
        handler._p_handler_keys = keys
        return handler
    return decorator
