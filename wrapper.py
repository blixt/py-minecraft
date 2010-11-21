# -*- coding: utf-8 -*-

"""Module for functionality for wrapping a Minecraft server and handling its
packets.

"""

import asyncore

from proxy import MinecraftForwarder

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = [
    'MinecraftWrapperMeta', 'MinecraftWrapper', 'packet_handler']

class MinecraftWrapperMeta(type):
    """Meta-class for setting up packet handlers.

    """
    def __new__(cls, name, bases, dct):
        dct['_handlers'] = {}
        t = type.__new__(cls, name, bases, dct)

        for attr_name in dct.keys():
            attr = dct[attr_name]
            if callable(attr) and hasattr(attr, '_p_handler_key'):
                key = getattr(attr, '_p_handler_key')
                if key not in t._handlers:
                    t._handlers[key] = []
                t._handlers[key].append(attr_name)

        return t

class MinecraftWrapper(object):
    __metaclass__ = MinecraftWrapperMeta

    def __init__(self):
        self.forwarder = MinecraftForwarder(('', 25564), ('localhost', 25565),
            self.handle_packet)

    def handle_packet(self, packet):
        key = (packet.__class__, packet.direction)
        if key not in self._handlers:
            return

        for handler in self._handlers[key]:
            getattr(self, handler)(packet)

    def start(self):
        asyncore.loop()

def packet_handler(packet_type, direction):
    key = (packet_type, direction)
    def decorator(handler):
        handler._p_handler_key = key
        return handler
    return decorator
