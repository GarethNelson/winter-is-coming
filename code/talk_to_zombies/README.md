# Protocol description

The game is split into 3 states: lobby, ingame and endgame.

When first connecting, you are in the lobby state, this state accepts the following commands:

* JOIN <game>
  Attempts to join an existing game, game names are single words, e.g:
  GarethsGame instead of "Gareth's Game"

* NAME <username>
  Change your username, if you don't do this, your username defaults to your IP address and port number, e.g 1.2.3.4:1337

* QUIT
  Disconnect from the server

* START <game>
  Starts a new game with the specified name, it must not already exist

Once ingame you can use NAME and QUIT and additionally the following 2 commands:

* LEAVE
  Leaves the game and returns to the lobby

* SHOOT <x> <y>
  Try to shoot the zombie at co-ordinates (x,y)

If anyone wins (including the zombie), the server enters endgame mode, from where you can only do LEAVE or QUIT
