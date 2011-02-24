#!/usr/bin/python
# -*- coding: utf-8 -*-

from example.wrapper import config
from example.wrapper import MinecraftWrapper

def main():
    w = MinecraftWrapper(('localhost', 25565), ('', config.get('port')))
    w.load_command_module('example.wrapper.commands')
    w.load_handler_module('example.wrapper.handlers')
    w.start()

if __name__ == '__main__':
    main()
