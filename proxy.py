# -*- coding: utf-8 -*-

"""Module for handling the proxying of Minecraft client connections to a server
connection, and the handling of packets in-between.

"""

import asyncore
import socket
import sys

import packets

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = [
    'MinecraftForwarder', 'MinecraftProxy']

class MinecraftProxy(asyncore.dispatcher):
    def __init__(self, socket, direction, packet_handler=None):
        self.other = None
        self.packet_handler = packet_handler
        self.packets = []
        self.reader = packets.PacketReader(direction)

        asyncore.dispatcher.__init__(self, socket)

    def handle_close(self):
        if not self.other:
            return

        self.other.close()
        self.close()
        self.other = None

        print 'Connection closed'

    def handle_error(self):
        print 'Error:', sys.exc_info()
        self.handle_close()

    def handle_read(self):
        data = self.recv(8192)
        if self.other:
            self.other.packets += self.reader.read(data)

    def handle_write(self):
        data = []
        while len(self.packets) > 0:
            packet = self.packets.pop(0)
            if self.packet_handler:
                self.packet_handler(self, packet)
            data.append(packet.build())
        self.send(''.join(data))

    def meet(self, other):
        self.other = other
        other.other = self

    def writable(self):
        return len(self.packets) > 0

class MinecraftForwarder(asyncore.dispatcher):
    def __init__(self, listen, forward_to, packet_handler=None):
        self.forward_to = forward_to
        self.packet_handler = packet_handler

        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(listen)
        self.listen(5)

        print 'Listening on %s' % (listen,)

    def handle_accept(self):
        client_connection, source_addr = self.accept()

        print 'Client connected', source_addr
        server_connection = socket.socket()
        server_connection.connect(self.forward_to)

        client = MinecraftProxy(client_connection, packets.TO_SERVER,
            self.packet_handler)
        server = MinecraftProxy(server_connection, packets.TO_CLIENT,
            self.packet_handler)
        server.meet(client)

    def handle_close(self):
        self.close()
        print 'Stopped listening'
