# -*- coding: utf-8 -*-

"""Minecraft-specific Marshaler types.

"""

import gzip
import zlib

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from autoproto.marshal import Array, Marshaler
from autoproto.marshal.java import *

__author__ = 'andreas@blixt.org (Andreas Blixt)'

def _struct_repr(struct):
    kw = []
    for name in struct.__slots__:
        kw.append('%s=%r' % (name, getattr(struct, name)))

    cls = struct.__class__
    return '%s.%s(%s)' % (cls.__module__, cls.__name__, ', '.join(kw))

__locals = set(locals())
__locals.add('__locals')

class BlockOffset(Marshaler):
    """A tuple of X, Y, Z offsets. The offsets are whole numbers (bytes) since
    they're intended for blocks.

    """
    @classmethod
    def bytes_from(cls, value):
        return ''.join(JavaByte.bytes_from(v) for v in value)

    @classmethod
    def read_bytes(cls, reader):
        return tuple(JavaByte.read_bytes(reader) for i in xrange(3))

class Item(object):
    __slots__ = ['id', 'count', 'damage']

    def __init__(self, id, count, damage):
        self.id = id
        self.count = count
        self.damage = damage

    def __repr__(self):
        return _struct_repr(self)

class ItemData(Marshaler):
    @classmethod
    def bytes_from(cls, value):
        if value:
            return JavaShort.bytes_from(value.id) + \
                   JavaByte.bytes_from(value.count) + \
                   JavaShort.bytes_from(value.damage)
        else:
            return JavaShort.bytes_from(-1)

    @classmethod
    def read_bytes(cls, reader):
        id = JavaShort.read_bytes(reader)
        if id >= 0:
            count = JavaByte.read_bytes(reader)
            damage = JavaShort.read_bytes(reader)
            return Item(id, count, damage)
        else:
            return None

class DynamicField(object):
    __slots__ = ['type', 'unknown', 'value']

    def __init__(self, type, unknown, value):
        self.type = type
        self.unknown = unknown
        self.value = value

    def __repr__(self):
        return _struct_repr(self)

class DynamicData(Marshaler):
    @staticmethod
    def get_marshaler(field_type):
        if field_type == 0:
            return JavaByte
        elif field_type == 1:
            return JavaShort
        elif field_type == 2:
            return JavaInt
        elif field_type == 3:
            return JavaFloat
        elif field_type == 4:
            return JavaString
        elif field_type == 5:
            return ItemData
        else:
            raise ValueError('Unexpected DynamicData field type.')

    @classmethod
    def read_bytes(cls, reader):
        value = []

        x = JavaByte.read_bytes(reader)
        while x != 127:
            field_type = x >> 5
            unknown = x & 0x1F

            data = DynamicData.get_marshaler(field_type).read_bytes(reader)
            field = DynamicField(field_type, unknown, data)
            value.append(field)

            x = JavaByte.read_bytes(reader)

        return value

    @classmethod
    def bytes_from(cls, value):
        pieces = []

        for field in value:
            x = field.type << 5 | field.unknown
            pieces.append(JavaByte.bytes_from(x))
            marshaler = DynamicData.get_marshaler(field.type)
            pieces.append(marshaler.bytes_from(field.value))

        return ''.join(pieces + [JavaByte.bytes_from(127)])

class RelativeBlockChange(object):
    __slots__ = ['x', 'y', 'z', 'type', 'meta']

    def __init__(self, x, y, z, type, meta):
        self.x = x
        self.y = y
        self.z = z
        self.type = type
        self.meta = meta

    def __repr__(self):
        return _struct_repr(self)

class RelativeBlockChangeList(Marshaler):
    @classmethod
    def bytes_from(cls, value):
        length = len(value)

        # Pre-allocate list so it can be filled non-sequentially.
        pieces = [None] * (1 + length * 3)
        pieces[0] = JavaShort.bytes_from(len(value))

        i = 0
        for change in value:
            s = change.x << 12 | change.z << 8 | change.y
            pieces[1 + i] = JavaShort.bytes_from(s)
            pieces[1 + i + length] = JavaByte.bytes_from(change.type)
            pieces[1 + i + length + length] = JavaByte.bytes_from(change.meta)
            i += 1

        return ''.join(pieces)

    @classmethod
    def read_bytes(cls, reader):
        length = JavaShort.read_bytes(reader)
        coords = Array.read_bytes(reader, length, JavaShort)
        types = Array.read_bytes(reader, length, JavaByte)
        meta = Array.read_bytes(reader, length, JavaByte)

        value = []
        for i in xrange(length):
            s = coords[i]
            x, z, y = (s >> 12, s >> 8 & 0xF, s & 0xFF)
            value.append(RelativeBlockChange(x, y, z, types[i], meta[i]))
        return value

class ZlibData(Marshaler):
    def __init__(self, length_type=JavaInt, use_gzip=False, **kwargs):
        super(ZlibData, self).__init__(**kwargs)
        self.length_type = length_type
        self.gzip = use_gzip

    @classmethod
    def bytes_from(cls, value, length_type=JavaInt, use_gzip=False):
        if use_gzip:
            buffer = StringIO()
            gz = gzip.GzipFile(None, mode='wb', fileobj=buffer)
            gz.write(value)
            gz.close()
            data = length_type.bytes_from(buffer.tell()) + buffer.getvalue()
            buffer.close()
            return data
        else:
            deflated = zlib.compress(value)
            return length_type.bytes_from(len(deflated)) + deflated

    @classmethod
    def read_bytes(cls, reader, length_type=JavaInt, use_gzip=False):
        length = length_type.read_bytes(reader)
        if use_gzip:
            return zlib.decompress(reader.get(length), zlib.MAX_WBITS + 16)
        else:
            return zlib.decompress(reader.get(length))

    def bytes_for(self, packet):
        return self.bytes_from(self.value_for(packet), self.length_type,
            self.gzip)

    def read_value(self, packet, reader):
        return self.read_bytes(reader, self.length_type, self.gzip)

__all__ = list(set(locals()) - __locals)
