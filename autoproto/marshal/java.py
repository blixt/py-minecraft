# -*- coding: utf-8 -*-

"""Java-specific Marshaler types.

"""

import struct

from autoproto.marshal import Marshaler

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = [
    'JavaBool', 'JavaByte', 'JavaDouble', 'JavaFloat', 'JavaInt', 'JavaLong',
    'JavaShort', 'JavaUByte', 'JavaUShort', 'JavaString']

class JavaBool(Marshaler):
    format = '>b'

    def read_value(self, packet, reader):
        return bool(self.read_bytes(reader))

class JavaByte(Marshaler):
    format = '>b'

class JavaUByte(Marshaler):
    format = '>B'

class JavaDouble(Marshaler):
    format = '>d'

class JavaFloat(Marshaler):
    format = '>f'

class JavaInt(Marshaler):
    format = '>i'

class JavaLong(Marshaler):
    format = '>q'

class JavaShort(Marshaler):
    format = '>h'

class JavaUShort(Marshaler):
    format = '>H'

class JavaString(Marshaler):
    @classmethod
    def bytes_from(self, value):
        value = value.encode('utf-8')
        strlen = len(value)
        return struct.pack('>h%ds' % strlen, strlen, value)

    @classmethod
    def read_bytes(self, reader):
        strlen = JavaShort.read_bytes(reader)
        return reader.get(strlen).decode('utf-8')
