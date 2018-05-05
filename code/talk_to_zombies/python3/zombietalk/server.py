import asyncio
import logging

import game_session

logging.basicConfig(level=logging.INFO)

# protocol states
LOBBY_MODE   = 0
INGAME_MODE  = 1
ENDGAME_MODE = 2

MOTD = "Welcome to the server!"

LOBBY_COMMANDS  = set(('START','NAME','JOIN','QUIT'))
INGAME_COMMANDS = set(('SHOOT','NAME','LEAVE','QUIT')) 

class ZombieGameClient:
   def __init__(self,server,name,reader,writer):
       self.server   = server
       self.reader   = reader
       self.writer   = writer
       self.name     = name
       self.username = name
       self.state    = LOBBY_MODE
       self.state_handler = self.lobby_handler
       self.cur_game = None
       self.send_motd()
       self.timeout = 30
       self.running = True
   def close(self,msg):
       if(self.state == INGAME_MODE):
          self.leave_game()
       self.send_line('DISCONNECTED %s' % msg)
       self.writer.write_eof()
       self.running = False
       self.server.delete_client(self)
   def handle_namecmd(self,name):
       self.username = name
       self.send_line('NAME Name changed')
       if self.state == INGAME_MODE:
          pass # here we'd broadcast the name change to other players
   def join_game(self, game):
       game.join_player(self)
       self.cur_game = game
       self.state = INGAME_MODE
       self.state_handler = self.ingame_handler
       self.timeout = 240 # increase the timeout
   def leave_game(self):
       self.cur_game.leave_player(self)
       self.state         = LOBBY_MODE
       self.state_handler = self.lobby_handler
       self.cur_game      = None
       self.send_motd()
   def handle_joincmd(self,game_name):
       if game_name not in self.server.current_games.keys():
          self.send_line('ERROR That game does not exist, did you mean "START %s"?' % game_name)
          return
       new_game = self.server.current_games[game_name]
       self.join_game(new_game)
   def handle_startcmd(self,game_name):
       if game_name in self.server.current_games.keys():
          self.send_line('ERROR A game already exists with that name, did you mean "JOIN %s"?', game_name)
          return
       new_game = game_session.ZombieGameSession(game_name,self.server)
       self.server.current_games[game_name] = new_game
       logging.info('Client %s started game %s with username %s',game_name,self.name,self.username)
       self.join_game(new_game)
   def ingame_handler(self,line):
       split_line = line.split(' ')
       if len(split_line)==0: return
       command = split_line[0]
       if not command in INGAME_COMMANDS:
          self.send_line('ERROR invalid command')
       elif command=='QUIT':
          self.close('User quit')
          return
       elif command=='LEAVE':
          self.leave_game()
   def lobby_handler(self,line):
       split_line = line.split(' ')
       if len(split_line)==0: return
       command = split_line[0]
       if not command in LOBBY_COMMANDS:
          self.send_line('ERROR invalid command')
       elif command=='QUIT':
          self.close('User quit')
          return
       if len(split_line) != 2:
          self.send_line('ERROR command takes 1 parameter')
          return
       # using a dict here is more efficient than a bunch of if/elif statements, or at least usually is
       {'NAME' :self.handle_namecmd,
        'JOIN' :self.handle_joincmd,
        'START':self.handle_startcmd}[command](*split_line[1:])
   def send_line(self,line):
       data = '%s\n' % line
       self.writer.write(data.encode())
   @asyncio.coroutine
   def read_line(self):
       data = yield from self.reader.readline()
       return data.decode().strip('\n')
   def send_motd(self):
       self.send_line('MOTD %s' % MOTD)
       self.send_line('MOTD Valid commands are: %s' % ' '.join(LOBBY_COMMANDS))
       for k,v in self.server.current_games.items():
           self.send_line('GAME %s is active with %s players' % (k,len(v.players)))
   @asyncio.coroutine
   def handle_loop(self):
       while self.running:
          try:
             in_line = yield from asyncio.wait_for(self.read_line(), self.timeout)
             self.state_handler(in_line)
          except asyncio.TimeoutError as e:
             self.close('Timed out')

class ZombieGameServer:
   def __init__(self):
       self.clients       = {} # maps by IP:port names
       self.current_games = {}
       self.loop          = asyncio.get_event_loop()
   @asyncio.coroutine
   def handle_connection(self, reader, writer):
       peername   = ':'.join(map (lambda x: str(x), writer.get_extra_info('peername')))
       new_client = ZombieGameClient(self,peername,reader,writer)
       self.clients[peername] = new_client
       logging.info('New connection %s', peername)
       try:
          yield from new_client.handle_loop()
       except BrokenPipeError as e:
          logging.info('Client %s disconnected', peername)
          self.delete_client(new_client)
   def delete_client(self,client):
       del self.clients[client.name]
       if client.state == INGAME_MODE:
          if client.cur_game != None:
             client.cur_game.leave_player(client)
       logging.info('Deleted client %s', client.name)
   def start_server(self):
       self.server = self.loop.run_until_complete(asyncio.start_server(self.handle_connection,'0.0.0.0',1337, loop=self.loop))
       logging.info('Serving on %s', self.server.sockets[0].getsockname())
       try:
          self.loop.run_forever()
       except Exception as e:
          logging.exception('Exception occurred')

if __name__=='__main__':
   game_server = ZombieGameServer()
   game_server.start_server()
