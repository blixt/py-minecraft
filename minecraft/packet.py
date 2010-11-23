# -*- coding: utf-8 -*-

"""Module which defines the Minecraft packet types.

"""

from autoproto.marshal.java import *
from autoproto.packet import Packet, PacketToClient, PacketToServer
from minecraft.marshal import *

# TODO: Make it simpler to make the id type local to a set of packet types
#       without having to inherit from yet another class.
Packet.id_type = JavaUByte

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__all__ = [
    'AddItem', 'AllocateChunk', 'AnimateArm', 'AttachEntity', 'BlockChange',
    'ChatMessage', 'ChunkData', 'CollectItem', 'ComplexEntity',
    'CreateVehicle', 'DestroyEntity', 'Dig', 'Disconnect', 'DropItem',
    'Entity', 'EntityVelocity', 'Handshake', 'HandshakeResponse', 'KeepAlive',
    'LogIn', 'LoggedIn', 'Look', 'Move', 'MoveAndLook',
    'MoveAndLookCorrection', 'MoveAndPointEntity', 'MoveEntity',
    'MultiBlockChange', 'PlaceItem', 'PlayerInventory', 'PlayerState',
    'PointEntity', 'RelativeBlockChange', 'RelativeBlockChangeList',
    'SetHeldItem', 'SetTime', 'SpawnMob', 'SpawnNamedEntity', 'SpawnPosition',
    'TeleportEntity', 'UseEntity']

class KeepAlive(PacketToClient, PacketToServer):
    id = 0x00

class LoggedIn(PacketToClient):
    id = 0x01
    player_id = JavaInt()
    unknown_1 = JavaString()
    unknown_2 = JavaString()
    map_seed = JavaLong()
    dimension = JavaByte()

class LogIn(PacketToServer):
    id = 0x01
    protocol_version = JavaInt()
    username = JavaString()
    password = JavaString()
    map_seed = JavaLong()
    dimension = JavaByte()

class HandshakeResponse(PacketToClient):
    id = 0x02
    hash = JavaString()

class Handshake(PacketToServer):
    id = 0x02
    username = JavaString()

class ChatMessage(PacketToClient, PacketToServer):
    id = 0x03
    message = JavaString()

class SetTime(PacketToClient):
    id = 0x04
    time = JavaLong()

class PlayerInventory(PacketToClient, PacketToServer):
    id = 0x05
    type = JavaInt()
    count = JavaShort()
    items = ItemList()

    MAIN = -1
    EQUIPPED = -2
    CRAFTING = -3

class SpawnPosition(PacketToClient):
    id = 0x06
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()

class UseEntity(PacketToServer):
    id = 0x07
    player_id = JavaInt()
    entity_id = JavaInt()

class PlayerState(PacketToServer):
    id = 0x0A
    on_ground = JavaBool()

class Move(PacketToServer):
    id = 0x0B
    x = JavaDouble()
    y = JavaDouble()
    stance = JavaDouble()
    z = JavaDouble()
    on_ground = JavaBool()

class Look(PacketToServer):
    id = 0x0C
    yaw = JavaFloat()
    pitch = JavaFloat()
    on_ground = JavaBool()

class MoveAndLookCorrection(PacketToClient):
    id = 0x0D
    x = JavaDouble()
    stance = JavaDouble()
    y = JavaDouble()
    z = JavaDouble()
    yaw = JavaFloat()
    pitch = JavaFloat()
    on_ground = JavaBool()

class MoveAndLook(PacketToServer):
    id = 0x0D
    x = JavaDouble()
    y = JavaDouble()
    stance = JavaDouble()
    z = JavaDouble()
    yaw = JavaFloat()
    pitch = JavaFloat()
    on_ground = JavaBool()

class Dig(PacketToServer):
    id = 0x0E
    status = JavaByte()
    x = JavaInt()
    y = JavaByte()
    z = JavaInt()
    face = JavaByte()

    STARTED_DIGGING = 0
    DIGGING = 1
    STOPPED_DIGGING = 2
    BLOCK_BROKEN = 3

class PlaceItem(PacketToServer):
    id = 0x0F
    item_id = JavaShort()
    x = JavaInt()
    y = JavaByte()
    z = JavaInt()
    face = JavaByte()

class SetHeldItem(PacketToClient, PacketToServer):
    id = 0x10
    player_id = JavaInt()
    item_id = JavaShort()

class AddItem(PacketToClient):
    id = 0x11
    item_id = JavaShort()
    count = JavaByte()
    health = JavaShort()

class AnimateArm(PacketToClient, PacketToServer):
    id = 0x12
    player_id = JavaInt()
    animate = JavaBool()

class SpawnNamedEntity(PacketToClient):
    id = 0x14
    player_id = JavaInt()
    username = JavaString()
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()
    rotation = JavaByte()
    pitch = JavaByte()
    item_id = JavaShort()

class DropItem(PacketToClient, PacketToServer):
    id = 0x15
    player_id = JavaInt()
    item_id = JavaShort()
    count = JavaByte()
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()
    rotation = JavaByte()
    pitch = JavaByte()
    roll = JavaByte()

class CollectItem(PacketToClient):
    id = 0x16
    entity_id = JavaInt()
    player_id = JavaInt()

class CreateVehicle(PacketToClient):
    id = 0x17
    entity_id = JavaInt()
    type = JavaByte()
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()

    BOAT = 1
    MINE_CART = 10
    MINE_CART_CHEST = 11
    MINE_CART_FURNACE = 12

class SpawnMob(PacketToClient):
    id = 0x18
    entity_id = JavaInt()
    type = JavaByte()
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()
    yaw = JavaByte()
    pitch = JavaByte()

class EntityVelocity(PacketToClient):
    id = 0x1C
    entity_id = JavaInt()
    x = JavaShort()
    y = JavaShort()
    z = JavaShort()

class DestroyEntity(PacketToClient):
    id = 0x1D
    entity_id = JavaInt()

class Entity(PacketToClient):
    id = 0x1E
    entity_id = JavaInt()

class MoveEntity(PacketToClient):
    id = 0x1F
    entity_id = JavaInt()
    x = JavaByte()
    y = JavaByte()
    z = JavaByte()

class PointEntity(PacketToClient):
    id = 0x20
    entity_id = JavaInt()
    yaw = JavaByte()
    pitch = JavaByte()

class MoveAndPointEntity(PacketToClient):
    id = 0x21
    entity_id = JavaInt()
    x = JavaByte()
    y = JavaByte()
    z = JavaByte()
    yaw = JavaByte()
    pitch = JavaByte()

class TeleportEntity(PacketToClient):
    id = 0x22
    entity_id = JavaInt()
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()
    yaw = JavaByte()
    pitch = JavaByte()

class AttachEntity(PacketToClient):
    id = 0x27
    player_id = JavaInt()
    entity_id = JavaInt()

    DETACH = -1

class AllocateChunk(PacketToClient):
    id = 0x32
    x = JavaInt()
    z = JavaInt()
    # False to deallocate
    allocate = JavaBool()

class ChunkData(PacketToClient):
    id = 0x33
    x = JavaInt()
    y = JavaShort()
    z = JavaInt()
    ubound_x = JavaByte()
    ubound_y = JavaByte()
    ubound_z = JavaByte()
    data = ZlibData()

class MultiBlockChange(PacketToClient):
    id = 0x34
    x = JavaInt()
    z = JavaInt()
    changes = RelativeBlockChangeList()

class BlockChange(PacketToClient):
    id = 0x35
    x = JavaInt()
    y = JavaByte()
    z = JavaInt()
    type = JavaByte()
    meta = JavaByte()

class ComplexEntity(PacketToClient):
    id = 0x3B
    x = JavaInt()
    y = JavaShort()
    z = JavaInt()
    data = NamedBinaryTagData()

class Disconnect(PacketToClient, PacketToServer):
    id = 0xFF
    reason = JavaString()
