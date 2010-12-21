# -*- coding: utf-8 -*-

"""Module which defines the Minecraft packet types.

"""

from autoproto.marshal import Array
from autoproto.marshal.java import *
from autoproto.packet import Packet, PacketToClient, PacketToServer
from minecraft.marshal import *

# TODO: Make it simpler to make the id type local to a set of packet types
#       without having to inherit from yet another class.
Packet.id_type = JavaUByte

__author__ = 'andreas@blixt.org (Andreas Blixt)'

__locals = set(locals())
__locals.add('__locals')

class KeepAlive(PacketToClient, PacketToServer):
    id = 0x00

class LoggedIn(PacketToClient):
    id = 0x01
    player_id = JavaInt()
    unused_1 = JavaString(default='')
    unused_2 = JavaString(default='')
    map_seed = JavaLong()
    dimension = JavaByte()

class LogIn(PacketToServer):
    id = 0x01
    protocol_version = JavaInt()
    username = JavaString()
    password = JavaString()
    unused_1 = JavaLong(default=0)
    unused_2 = JavaByte(default=0)

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

class Unknown(PacketToClient, PacketToServer):
    """Was previously the PlayerInventory packet."""
    id = 0x05
    unknown_1 = JavaInt()
    unknown_2 = JavaShort()
    unknown_3 = JavaShort()

class SpawnPosition(PacketToClient):
    id = 0x06
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()

class UseEntity(PacketToServer):
    """This packet is sent when an entity is within a certain range, the player
    points at it and then left- or right-clicks. The punching flag is True when
    left-clicking (punching).

    """
    id = 0x07
    actor_id = JavaInt()
    entity_id = JavaInt()
    punching = JavaBool()

class SetHealth(PacketToClient):
    id = 0x08
    health = JavaShort()

class Respawn(PacketToClient, PacketToServer):
    id = 0x09

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

class UseItem(PacketToServer):
    """This packet is sent when the currently held item is used. The x, y, z
    and face values will be -1 if the player was pointing in the air, otherwise
    they will be the coordinates and face of the block the player was pointing
    at.

    """
    id = 0x0F
    x = JavaInt()
    y = JavaByte()
    z = JavaInt()
    face = JavaByte()
    item = ItemData()

class SetHeldItem(PacketToClient, PacketToServer):
    id = 0x10
    slot = JavaShort()

class Animate(PacketToClient, PacketToServer):
    id = 0x12
    entity_id = JavaInt()
    animation = JavaByte()

    SWING = 1
    CROUCH = 104
    STAND = 105

class SpawnPlayer(PacketToClient):
    id = 0x14
    entity_id = JavaInt()
    username = JavaString()
    x = JavaInt()
    y = JavaInt()
    z = JavaInt()
    rotation = JavaByte()
    pitch = JavaByte()
    item_id = JavaShort()

class SpawnItem(PacketToClient, PacketToServer):
    id = 0x15
    entity_id = JavaInt()
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
    actor_id = JavaInt()

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

    CREEPER = 50
    SKELETON = 51
    ZOMBIE = 54
    PIG = 90
    SHEEP = 91
    COW = 92
    CHICKEN = 93

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

class DamageEntity(PacketToClient):
    """Notifies the client of an update to the health state of an entity. The
    state can be that the entity took damage, that it died or that it's about
    to explode.

    """
    id = 0x26
    entity_id = JavaInt()
    state = JavaByte()

    DAMAGE = 2
    DEATH = 3
    EXPLODING = 4

class AttachEntity(PacketToClient):
    id = 0x27
    actor_id = JavaInt()
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

class Explode(PacketToClient):
    id = 0x3C
    x = JavaDouble()
    y = JavaDouble()
    z = JavaDouble()
    unknown = JavaFloat()
    blocks = Array(JavaInt, BlockOffset)

class InitializeWindow(PacketToClient):
    id = 0x64
    window = JavaByte()
    type = JavaByte()
    title = JavaString()
    slot_count = JavaByte()

    # Window types.
    CHEST = 0
    WORKBENCH = 1
    FURNACE = 2

class CloseWindow(PacketToServer):
    id = 0x65
    window = JavaByte()

class RequestSetSlot(PacketToServer):
    id = 0x66
    window = JavaByte()
    slot = JavaShort()
    unknown = JavaByte() # related to right-click or splitting stacks
    transaction = JavaShort()
    item = ItemData()

    # Slot value for dropping items.
    DROP_ITEM_SLOT = -999

class SetSlot(PacketToClient):
    id = 0x67
    window = JavaByte()
    slot = JavaShort()
    item = ItemData()

    # Constant window ids.
    UNKNOWN = -1 # Sent when initializing a window for unknown reason.
    INVENTORY = 0

class WindowItems(PacketToClient):
    id = 0x68
    window = JavaByte()
    items = Array(JavaShort, WindowItemData)

class SetProgressBar(PacketToClient):
    id = 0x69
    window = JavaByte()
    bar = JavaShort()
    progress = JavaShort()

class Transaction(PacketToClient):
    id = 0x6A
    window = JavaByte()
    transaction = JavaShort()
    accepted = JavaBool() # Not completely verified.

class SpawnSign(PacketToClient):
    id = 0x82
    x = JavaInt()
    y = JavaShort()
    z = JavaInt()
    lines = Array(4, JavaString)

class Disconnect(PacketToClient, PacketToServer):
    id = 0xFF
    reason = JavaString()

__all__ = list(set(locals()) - __locals)
