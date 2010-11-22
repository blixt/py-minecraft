# -*- coding: utf-8 -*-

import re

import packets
from packets.minecraft import *
from wrapper import packet_handler

@packet_handler(ChatMessage, packets.TO_CLIENT)
def modify_chat(player, packet):
    """Modifies chat messages to be prefixed with "Name says" in a green
    color, instead of just "<Name>" in white.

    """
    packet.message = re.sub(r'^<([^>]+)>', u'§a\\1 says§f', packet.message)

@packet_handler(SetTime, packets.TO_CLIENT)
def force_day(player, packet):
    packet.time = 3600
