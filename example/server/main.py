# -*- coding: utf-8 -*-

import asyncore
import math
import socket

import autoproto.marshal.java
import autoproto.packet
from minecraft.marshal import *
from minecraft.packet import *

class Vector:
    """A 3D vector.

    """
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Entity(object):
    """An entity in the world. Entities are objects that can move around freely
    in the world.

    """
    id_counter = 0

    def __init__(self):
        Entity.id_counter += 1
        self.id = Entity.id_counter
        self.pos = Vector(128.0, 80.0, 128.0)
        self.vel = Vector()
        self.yaw = 0.0
        self.pitch = 0.0

class Player(Entity):
    def __init__(self, username):
        super(Player, self).__init__()
        self.username = username

class Error(Exception):
    pass

class NameInUseError(Error):
    pass

class MinecraftServer(asyncore.dispatcher):
    def __init__(self, host, port):
        self.clients = {}
        self.entities = {}
        
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(1)
        print 'Listening on %s:%d' % (host or '*', port)

    def add_entity(self, entity):
        self.entities[entity.id] = entity

    def add_player(self, client):
        if client.username in self.clients:
            raise NameInUseError('Username is already in use.')

        self.message(u'§e%s joined the game' % client.username)

        self.clients[client.username] = client

        player = Player(client.username)
        self.add_entity(player)
        return player

    def handle_accept(self):
        socket, address = self.accept()
        print address, 'connected'
        ClientHandler(socket, self)

    def message(self, message):
        print message
        packet = ChatMessage(message=message)
        for client in self.clients.values():
            client.out.append(packet)

    def remove_entity(self, entity):
        del self.entities[entity.id]

    def remove_player(self, client):
        if client.entity:
            self.remove_entity(client.entity)
        del self.clients[client.username]
        self.message(u'§e%s left the game' % client.username)

class ClientHandler(asyncore.dispatcher):
    def __init__(self, socket, server):
        self.entity = None

        self.server = server
        self.reader = autoproto.packet.PacketReader(
            autoproto.marshal.java.JavaUByte,
            autoproto.packet.TO_SERVER)
        self.handler = self.protocol()

        # Queue for packets that should be sent, but don't have to be sent
        # immediately, leaving room for other packets to be handled.
        self.deferred = []
        # List of packets that have been received by the client, but not
        # handled.
        self.incoming = []
        # List of packets that are to be sent to the client.
        self.out = []

        asyncore.dispatcher.__init__(self, socket)

    def get_packet(self, type=None):
        packet = self.incoming.pop(0)
        if type:
            assert isinstance(packet, type), 'Unexpected packet %s' % packet
        return packet

    def protocol(self):
        """A generator that handles the Minecraft protocol.

        """
        # Wait for packets available.
        while not self.incoming:
            yield None

        handshake = self.get_packet(Handshake)
        self.username = handshake.username 
        yield HandshakeResponse(hash='-')

        # Wait for packets available.
        while not self.incoming:
            yield None

        login = self.get_packet(LogIn)
        if login.protocol_version != 7:
            yield Disconnect(reason='Unsupported client version.')
            return

        try:
            entity = self.server.add_player(self)
            self.entity = entity
            yield LoggedIn(player_id=0, map_seed=0, dimension=0)
        except NameInUseError:
            yield Disconnect(reason='Name already in use.')
            return

        yield SpawnPosition(x=0, y=64, z=0)

        for x in xrange(20):
            for z in xrange(20):
                yield AllocateChunk(x=x, z=z, allocate=True)

        yield MoveAndLookCorrection(
            x=entity.pos.x, y=entity.pos.y, z=entity.pos.z,
            stance=entity.pos.y + 1.62, yaw=entity.yaw, pitch=entity.pitch,
            on_ground=False)

        # Give the player a golden pickaxe.
        pickaxe = Item(285, 1, 0)
        yield WindowItems(
            window=0,
            items=[None] * 36 + [pickaxe] + [None] * 8)
        yield SetSlot(window=0, slot=36, item=pickaxe)

        yield SetTime(time=725037)
        yield KeepAlive()

        yield SetHealth(health=20)

        # 64 blocks of gold, then 64 blocks of air, plus metadata and light
        # data, in a 16x128x16 area.
        data = ('\x29' * 64 + '\x00' * 64) * 256 + '\x00' * 16384 + \
                '\xff' * 32768
        chunks = []
        for x in xrange(20):
            for z in xrange(20):
                chunks.append(ChunkData(
                    x=x * 16, y=0, z=z * 16, ubound_x=15, ubound_y=127,
                    ubound_z=15, data=data))
        # Send chunks back in order of distance.
        chunks.sort(key=lambda c: math.sqrt((entity.pos.x - c.x - 8) ** 2 +
                                            (entity.pos.y - c.y - 8) ** 2))

        # Add ChunkData to a deferred queue, so client input can be processed
        # while chunk data is being sent.
        self.deferred += chunks

        # Remove unused variables.
        del chunks, data

        yield MoveAndLookCorrection(
            x=entity.pos.x, y=entity.pos.y, z=entity.pos.z,
            stance=entity.pos.y + 1.62, yaw=entity.yaw, pitch=entity.pitch,
            on_ground=False)

        yield ChatMessage(message=u'§eWelcome to Example Server!')

        while True:
            while not self.incoming:
                # Waiting for incoming packets.
                n = 0
                while self.deferred:
                    # Since there is nothing to do, use this opportunity to
                    # send deferred packets.
                    yield self.deferred.pop(0)
                    n += 1
                    if n >= 5:
                        # Only send up to 5 deferred packets at a time.
                        break
                yield None

            # Incoming packets available.
            packet = self.get_packet()

            # Handle packets.
            if isinstance(packet, (Move, MoveAndLook)):
                entity.pos.set(packet.x, packet.y, packet.z)
                entity.stance = packet.stance
            if isinstance(packet, (Look, MoveAndLook)):
                entity.yaw = packet.yaw
                entity.pitch = packet.pitch
            if isinstance(packet, ChatMessage):
                self.server.message('<%s> %s' % (self.username, packet.message))
            if isinstance(packet, Disconnect):
                print self.username, 'disconnecting:', packet.reason
                break

        self.handle_close()

    def handle_close(self):
        if self.entity:
            self.server.remove_player(self)
            self.entity = None
        self.server = None

        self.close()

    def handle_read(self):
        data = self.recv(8192)
        if not data:
            self.handle_close()

        self.incoming += self.reader.read(data)
        for response in self.handler:
            # Stop when there are no more packets to send.
            if not response:
                break
            self.out.append(response)

    def handle_write(self):
        data = []

        while len(self.out) > 0:
            packet = self.out.pop(0)
            data.append(packet.build())

        self.send(''.join(data))

    def writable(self):
        return len(self.out) > 0

def main():
    s = MinecraftServer('', 25565)
    asyncore.loop()

if __name__ == '__main__':
    main()
