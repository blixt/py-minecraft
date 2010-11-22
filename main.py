#!/usr/bin/python
# -*- coding: utf-8 -*-

from wrapper import MinecraftWrapper

def main():
    w = MinecraftWrapper()
    w.load_command_module('simple.commands')
    w.load_handler_module('simple.handlers')
    w.start()

if __name__ == '__main__':
    main()
