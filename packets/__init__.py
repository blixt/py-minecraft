# -*- coding: utf-8 -*-

"""Module with classes for parsing a single packet from a Minecraft server, as
well as writing a single packet to a Minecraft server.

"""

import datamarshal
import datamarshal.java

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = [
    'NotAvailableYet', 'Packet', 'PacketInitializer', 'PacketReader',
    'PacketToClient', 'PacketToServer', 'TO_CLIENT', 'TO_SERVER']

TO_CLIENT = 0b10
TO_SERVER = 0b01

# Map of packet ids to packet classes, grouped by server->client and
# client->server directions.
_map_sc = {}
_map_cs = {}

class PacketInitializer(type):
    """Meta-class for setting up packet classes.

    Keeps track of the packet id of the packet classes so that the appropriate
    class for a certain packet id can be fetched.

    """
    def __new__(cls, name, bases, dct):
        t = type.__new__(cls, name, bases, dct)

        if 'id' not in dct:
            # Nothing to do if the class has no "id" attribute.
            return t

        packet_id = dct['id']

        # Keep track of what packet id maps to what class.
        sc = PacketToClient in bases
        cs = PacketToServer in bases
        assert sc or cs, (
            '%s must implement one of PacketToClient, PacketToServer' % name)

        if sc:
            assert packet_id not in _map_sc, (
                '%s redefines server->client packet 0x%02x (%s)' % (
                    name, packet_id, _map_sc[packet_id].__name__))
            _map_sc[packet_id] = t
        if cs:
            assert packet_id not in _map_cs, (
                '%s redefines client->server packet 0x%02x (%s)' % (
                    name, packet_id, _map_cs[packet_id].__name__))
            _map_cs[packet_id] = t

        # TODO: Handle duplicate attributes from inheritance.
        t._values = []
        for attr_name in dct.keys():
            attr = dct[attr_name]
            if isinstance(attr, datamarshal.Marshaler):
                attr._set_up(attr_name)
                t._values.append(attr)
        t._values.sort(key=lambda v: v._creation_index)

        return t

class Packet(object):
    __metaclass__ = PacketInitializer

    def __init__(self, direction=None, **kwargs):
        if direction == TO_SERVER:
            if not isinstance(self, PacketToServer):
                raise ValueError(
                    'Packet %s cannot have direction client->server' % (
                        self.__class__.__name__))
        elif direction == TO_CLIENT:
            if not isinstance(self, PacketToClient):
                raise ValueError(
                    'Packet %s cannot have direction server->client' % (
                        self.__class__.__name__))
        elif direction is not None:
            raise ValueError('Invalid direction')

        self.direction = direction

        for name in kwargs:
            setattr(self, name, kwargs[name])

    def build(self):
        pieces = []
        pieces.append(datamarshal.java.JavaUByte.bytes_from(self.id))

        for val in self._values:
            pieces.append(val.bytes_for(self))

        return ''.join(pieces)

    def __repr__(self):
        cls = self.__class__
        kwargs = []
        for val in self._values:
            try:
                kwargs.append('%s=%r' % (val.name, val.value_for(self)))
            except ValueError:
                pass
        return '%s.%s(%s)' % (cls.__module__, cls.__name__, ', '.join(kwargs))

    def __str__(self):
        return self.__class__.__name__

class PacketToClient(Packet):
    pass

class PacketToServer(Packet):
    pass

class NotAvailableYet:
    """Raised to abort reading when no data is available. Since it is neither
    an error nor an exception it does not inherit from the Exception class.

    """
    # Since this is a light-weight message class, don't allocate dicts for
    # every instance.
    __slots__ = []

class PacketReader(object):
    def __init__(self, direction):
        if direction == TO_SERVER:
            self._map = _map_cs
        elif direction == TO_CLIENT:
            self._map = _map_sc
        else:
            raise ValueError('Invalid direction')

        self.buffer = ''
        self.consumed = 0
        self.direction = direction
        self._packet = None

    def get(self, num):
        """Attempts to get a number of bytes from the reader buffer. If there
        aren't enough bytes available, None will be returned and the buffer
        state will not be affected.

        It's very important that any code not invoked through the read method
        that is calling this method is careful to try for NotAvailableYet as it
        is not an Exception instance and will stop code execution unless
        handled.

        """
        if num < 0:
            raise ValueError('Number of bytes may not be a negative number')
        start = self.consumed
        end = start + num
        if end > len(self.buffer):
            # Raise to tell the caller that all the data is not available yet.
            raise NotAvailableYet
        self.consumed += num
        return self.buffer[start:end]

    def read(self, data):
        """Gives the packet reader more data to work with. This method will
        return a list of Packet instances that were completely read. The list
        may be empty.

        """
        # A list of completely read packets.
        packets = []

        if not data:
            # There was no new data available, so assume nothing can be done.
            return packets

        self.buffer += data

        # Keep looping until we can't read any more.
        while True:
            # Remember current buffer position so that it can be restored
            # something needs before data before it can be read.
            mark = self.consumed
            try:
                if not self._packet:
                    # Start reading a new packet.
                    packet_id = datamarshal.java.JavaUByte.read_bytes(self)
                    if packet_id not in self._map:
                        raise NotImplementedError(
                            'Unimplemented packet 0x%02x' % packet_id)
                    self._packet = self._map[packet_id](self.direction)
                packet = self._packet

                for val in packet._values:
                    if val.has_value(packet):
                        # Skip values that have already been loaded.
                        continue
                    # Update the mark since all data read so far should be
                    # kept.
                    mark = self.consumed
                    val.read(packet, self)
            except NotAvailableYet:
                # Ran out of data; restore the buffer position and exit the
                # loop.
                self.consumed = mark
                break
            else:
                # All data was available, which means the packet has been read.
                # If True, packet has been completely read.
                packets.append(packet)
                self._packet = None

        # Remove all data that was consumed from the buffer.
        self.buffer = self.buffer[self.consumed:]
        self.consumed = 0

        return packets
