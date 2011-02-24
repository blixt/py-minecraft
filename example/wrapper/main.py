#!/usr/bin/python
# -*- coding: utf-8 -*-

from example.wrapper import config
from example.wrapper import MinecraftWrapper

def main():
    wrapper = MinecraftWrapper(
        (config.get('server', 'host'), config.get('server', 'port')),
        ('', config.get('port')))
    wrapper.load_command_module('example.wrapper.commands')
    wrapper.load_handler_module('example.wrapper.handlers')
    wrapper.start()

if __name__ == '__main__':
    main()
