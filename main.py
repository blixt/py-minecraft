#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

import packets
from packets.minecraft import *
from wrapper import MinecraftWrapper, packet_handler

class SimpleMinecraftWrapper(MinecraftWrapper):
    @packet_handler(ChatMessage, packets.TO_CLIENT)
    def modify_chat(self, player, packet):
        """Modifies chat messages to be prefixed with "Name says" in a green
        color, instead of just "<Name>" in white.

        """
        packet.message = re.sub(r'^<([^>]+)>', u'§a\\1 says§f', packet.message)

    @packet_handler(ChatMessage, packets.TO_SERVER)
    def player_said(self, player, packet):
        """Prints chat messages sent by players.

        """
        print player.username, 'said "%s"' % packet.message

def main():
    wrapper = SimpleMinecraftWrapper()
    wrapper.start()

if __name__ == '__main__':
    main()
