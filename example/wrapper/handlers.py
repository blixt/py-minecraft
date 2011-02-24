# -*- coding: utf-8 -*-

from datetime import datetime
import re

from autoproto.packet import TO_CLIENT, TO_SERVER
from example.wrapper import config, packet_handler
from minecraft.packet import *

@packet_handler(Disconnect, TO_CLIENT)
def player_disconnected(player, packet):
    print '%s disconnected (%s)' % (player.username, packet.reason)

@packet_handler(LoggedIn)
def player_logged_in(player, packet):
    print '%s logged in' % player.username

    config.set('players', player.username, 'last-login',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@packet_handler(ChatMessage, TO_SERVER)
def player_sent_message(player, packet):
    print '<%s> %s' % (player.username, packet.message)
