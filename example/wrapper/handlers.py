# -*- coding: utf-8 -*-

import re

from autoproto.packet import TO_CLIENT, TO_SERVER
from example.wrapper import packet_handler
from minecraft.packet import *

@packet_handler(ChatMessage, TO_CLIENT)
def modify_chat(player, packet):
    """Modifies chat messages to be prefixed with "Name says" in a green
    color, instead of just "<Name>" in white.

    """
    packet.message = re.sub(r'^<([^>]+)>', u'§a\\1 says§f', packet.message)
