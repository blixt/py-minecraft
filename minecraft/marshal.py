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

__all__ = [
    'BlockOffset', 'Item', 'ItemList', 'NamedBinaryTagData',
    'RelativeBlockChange', 'RelativeBlockChangeList', 'ZlibData']

def _struct_repr(struct):
    kw = []
    for name in struct.__slots__:
        kw.append('%s=%r' % (name, getattr(struct, name)))

    cls = struct.__class__
    return '%s.%s(%s)' % (cls.__module__, cls.__name__, ', '.join(kw))

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
    __slots__ = ['id', 'count', 'uses']
    
    def __init__(self, id, count, uses):
        self.id = id
        self.count = count
        self.uses = uses

    def __repr__(self):
        return _struct_repr(self)

class ItemList(Marshaler):
    @classmethod
    def bytes_from(cls, value):
        pieces = []

        pieces.append(JavaShort.bytes_from(len(value)))
        for item in value:
            if item:
                pieces.append(JavaShort.bytes_from(item.id))
                pieces.append(JavaByte.bytes_from(item.count))
                pieces.append(JavaShort.bytes_from(item.uses))
            else:
                pieces.append(JavaShort.bytes_from(-1))

        return ''.join(pieces)

    @classmethod
    def read_bytes(cls, reader):
        count = JavaShort.read_bytes(reader)

        items = []
        for i in xrange(count):
            item_id = JavaShort.read_bytes(reader)
            if item_id != -1:
                count = JavaByte.read_bytes(reader)
                uses = JavaShort.read_bytes(reader)
                items.append(Item(item_id, count, uses))
            else:
                items.append(None)
        return items

class NamedBinaryTagData(Marshaler):
    @classmethod
    def bytes_from(cls, value):
        return ZlibData.bytes_from(value, length_type=JavaShort, use_gzip=True)

    @classmethod
    def read_bytes(cls, reader):
        data = ZlibData.read_bytes(reader, length_type=JavaShort,
            use_gzip=True)
        # TODO: Implement named binary tag format.
        #       http://www.minecraft.net/docs/NBT.txt
        return data

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
