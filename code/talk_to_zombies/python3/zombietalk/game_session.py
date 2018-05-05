import logging
import asyncio
import random

class ZombieGameSession:
   def __init__(self,name,server):
       self.PRNG      = random.Random()
       self.game_name = name
       self.players   = {}
       self.server    = server
       self.loop      = server.loop
       self.running   = True
       self.game_over = False
       self.task      = asyncio.ensure_future(self.handle_game_loop(),loop=self.loop)
       self.zombie_x  = self.PRNG.randint(0,9)
       self.zombie_y  = 29
   async def handle_game_loop(self):
       while not self.game_over:
          await asyncio.sleep(1.0)
          self.zombie_x = (self.zombie_x + self.PRNG.randint(-1,1)) % 9
          self.zombie_y -= self.PRNG.randint(0,1)
          self.check_zombie()
          if not self.game_over:
             await asyncio.sleep(1.0)
             self.zombie_x = (self.zombie_x + self.PRNG.randint(-1,1)) % 9
             self.zombie_y -= self.PRNG.randint(0,1)
             self.check_zombie()
          if not self.game_over:
             self.send_update()
   def send_update(self):
       for k,v in self.players.items():
           v.send_line('WALK Zombie %d %d' % (self.zombie_x,self.zombie_y))
   def check_zombie(self):
       logging.info('Zombie in game %s at (%d,%d)', self.game_name,self.zombie_x,self.zombie_y)
       if self.zombie_y == 0:
          logging.info('Game %s over: zombie won', self.game_name)
          self.game_over = True
          for k,v in self.players.items():
              v.send_line('GAMEOVER Zombie won')
              v.game_over()

   def close_game(self):
       logging.info('Closing game %s', self.game_name)
       del self.server.current_games[self.game_name]
       self.running = False
       self.task.cancel()
   def player_shoot(self,player,x,y):
       for k,v in self.players.items():
           v.send_line('SHOOT %s %d %d' % (player.username, x, y))
       if (x==self.zombie_x) and (y==self.zombie_y):
          self.game_over = True
          self.task.cancel()
          for k,v in self.players.items():
              v.send_line('GAMEOVER %s won' % player.username)
              v.game_over()
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
