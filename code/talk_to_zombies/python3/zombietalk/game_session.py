import logging
import asyncio

class ZombieGameSession:
   def __init__(self,name,server):
       self.game_name = name
       self.players   = {}
       self.server    = server
       self.loop      = server.loop
       self.running   = True
       self.task      = asyncio.ensure_future(self.handle_game_loop(),loop=self.loop)
   async def handle_game_loop(self):
       while self.running:
          await asyncio.sleep(1.0)
          # here is where we run game logic
   def close_game(self):
       logging.info('Closing game %s', self.game_name)
       del self.server.current_games[self.game_name]
       self.running = False
       self.task.cancel()
   def leave_player(self,player):
       del self.players[player.username]
       logging.info('Player %s has left game %s',player.username, self.game_name)
       if len(self.players)==0:
          self.close_game()
       else:
          for k,v in self.players.items():
              v.send_line('LEAVE %s has left the game' % player.username)
   def join_player(self,player):
       self.players[player.username] = player
       logging.info('Player %s has joined game %s',player.username,self.game_name)
       for k,v in self.players.items():
           v.send_line('JOIN %s has joined the game' % player.username)
