# pyminecraft

A Python library for communicating with Minecraft clients and servers.

## Trying it out

### Minecraft wrapper

This project is an example of how to write a Minecraft wrapper. A wrapper sits
on top of the server, taking all client requests and forwarding them to the
server. The benefit of using a wrapper is that you get full control of
everything sent back and forth between the clients and the server. This can be
used for access control (for example: don't allow unknown users to place
blocks) or to allow new functionality (warping to locations, colored chat
messages, etc.)

Run this in the top directory to start the wrapper:

    python -m example.wrapper.main

This will start a wrapper on port 25564 that you can connect to by entering
`localhost:25564` as the server after selecting "Multiplayer" in the client.

The wrapper expects a Minecraft server to already be running locally on port
25565.

## MIT license

This project is licensed under an MIT license.  
<http://www.opensource.org/licenses/mit-license.php>

Copyright © 2010 Andreas Blixt <andreas@blixt.org>
