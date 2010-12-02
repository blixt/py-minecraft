# -*- coding: utf-8 -*-

"""Module for defining classes that handle the conversion between bytes and
data structures.

"""

import struct

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = ['Array', 'Marshaler', 'MarshalerInitializer']

class MarshalerInitializer(type):
    """Meta-class for setting up new classes with the base type Marshaler.

    """
    def __new__(cls, name, bases, dct):
        # Pre-calculate the size of the value, if possible.
        if 'format' in dct:
            dct['size'] = struct.calcsize(dct['format'])
        return type.__new__(cls, name, bases, dct)

class Marshaler(object):
    __metaclass__ = MarshalerInitializer
    _counter = 0

    def __init__(self, default=None):
        self.default = default

        # Keep track of the order that Marshaler instances are created so that
        # the field order can be known by packets.
        self._creation_index = Marshaler._counter
        Marshaler._counter += 1

    def __get__(self, instance, owner):
        return getattr(instance, '_' + self.name, self.default)

    def __set__(self, instance, value):
        setattr(instance, '_' + self.name, value)

    def _set_up(self, name):
        self.name = name

    @classmethod
    def bytes_from(cls, value):
        """Returns a byte string for the specified value.

        This is the method that should be overridden for defining the binary
        format of the data.

        """
        return struct.pack(cls.format, value)

    @classmethod
    def read_bytes(cls, reader):
        """Reads a value from the specified reader.

        This is the method that should be overridden for defining data load
        behavior.

        """
        data = reader.get(cls.size)
        # XXX: Ignores formats with more than one value.
        return struct.unpack(cls.format, data)[0]

    def bytes_for(self, packet):
        """Returns the byte string for the value of this field for the
        specified packet.

        """
        return self.bytes_from(self.value_for(packet))

    def has_value(self, packet):
        """Returns True if the specified Packet has a value set for this
        Marshaler. Default values do not count.

        """
        return hasattr(packet, '_' + self.name)

    def read(self, packet, reader):
        """Reads the value from the specified PacketReader and sets the
        appropriate field of the specified packet.

        """
        self.__set__(packet, self.read_value(packet, reader))

    def read_value(self, packet, reader):
        """Responsible for returning a value given a packet and a reader.

        If the read_bytes function depends on packet-specific values, override
        this method to provide those values to it.

        """
        return self.read_bytes(reader)

    def value_for(self, packet):
        """Returns the value of this field for the specified packet, or the
        default value if the packet does not have a value set.

        """
        value = self.__get__(packet, packet.__class__)
        if value is None:
            raise ValueError(
                'Missing value for %s and no default specified' % self.name)
        return value

class Array(Marshaler):
    def __init__(self, length_type, item_type, **kwargs):
        """Initializes an array field. The length of the array is determined
        using length_type. If length_type is a number, that number is used as
        a fixed length instead. Every item in the array is read/written as
        item_type.

        """
        super(Array, self).__init__(**kwargs)
        self.length_type = length_type
        self.item_type = item_type

    @classmethod
    def bytes_from(cls, value, length_type, item_type, **item_kwargs):
        """Takes a list and gets the bytes for every item through the item_type
        class. The length of the list is witten using length_type. If
        length_type is a number, no value is written, but the list is checked
        make sure that it's the length specified by length_type.

        The item_kwargs argument is a dictionary of keyword arguments to pass
        on to the bytes_from method of the item_type class.

        """
        pieces = []

        if isinstance(length_type, (int, long)):
            assert len(value) == length_type, 'Invalid value length'
        else:
            pieces.append(length_type.bytes_from(len(value)))

        for item in value:
            pieces.append(item_type.bytes_from(item, **item_kwargs))
        return ''.join(pieces)

    @classmethod
    def read_bytes(cls, reader, length_type, item_type, **item_kwargs):
        """Reads a sequence of item_type. The length of the sequence is
        determined by reading a number using length_type. (If length_type is a
        number, that number will be used.)

        The item_kwargs argument is a dictionary of keyword arguments to pass
        on to the read_bytes method of the item_type class.

        """
        if isinstance(length_type, (int, long)):
            length = length_type
        else:
            length = length_type.read_bytes(reader)

        value = []
        for i in xrange(length):
            value.append(item_type.read_bytes(reader, **item_kwargs))
        return value

    def bytes_for(self, packet):
        return self.bytes_from(self.value_for(packet), self.length_type,
                               self.item_type)

    def read_value(self, packet, reader):
        return self.read_bytes(reader, self.length_type, self.item_type)
