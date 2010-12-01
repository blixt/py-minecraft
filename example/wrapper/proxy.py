# -*- coding: utf-8 -*-

"""Module for handling the proxying of Minecraft client connections to a server
connection, and the handling of packets in-between.

"""

import asyncore
import socket
import sys
import traceback

import autoproto.marshal.java
import autoproto.packet

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = [
    'MinecraftForwarder', 'MinecraftProxy']

class MinecraftProxy(asyncore.dispatcher):
    def __init__(self, socket, direction, packet_handler=None):
        self.other = None
        self.packet_handler = packet_handler
        self.packets = []
        self.reader = autoproto.packet.PacketReader(
            autoproto.marshal.java.JavaUByte, direction)

        asyncore.dispatcher.__init__(self, socket)

    def handle_close(self):
        if not self.other:
            return

        self.other.close()
        self.close()
        self.other = None

        print 'Connection closed'

    def handle_error(self):
        t, v, tb = sys.exc_info()
        print 'ERROR: %s' % v
        traceback.print_tb(tb)

        self.handle_close()

    def handle_read(self):
        data = self.recv(8192)
        if self.other:
            self.other.packets += self.reader.read(data)

    def handle_write(self):
        data = []

        # Send all packets in the queue.
        # XXX: Maybe limit this to a certain number of packets in case all the
        #      writing is holding up the rest of the thread.
        while len(self.packets) > 0:
            # Get the next packet to be sent.
            packet = self.packets.pop(0)
            # Pass the packet to the packet handler.
            if self.packet_handler:
                self.packet_handler(self, packet)
            # Forward the packet as long as it has not been suppressed.
            if not packet.suppressed:
                data.append(packet.build())

        # Send all the data that should be sent.
        self.send(''.join(data))

    def meet(self, other):
        """Connect this proxy with another. Basically, set up forwarding from a
        client to a server and vice versa.

        """
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

        client = MinecraftProxy(client_connection, autoproto.packet.TO_SERVER,
            self.packet_handler)
        server = MinecraftProxy(server_connection, autoproto.packet.TO_CLIENT,
            self.packet_handler)
        server.meet(client)

    def handle_close(self):
        self.close()
        print 'Stopped listening'
