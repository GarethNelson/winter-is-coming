import asyncio
import logging

logging.basicConfig(level=logging.INFO)

# protocol states
LOBBY_MODE   = 0
INGAME_MODE  = 1
ENDGAME_MODE = 2

MOTD = "Welcome to the server!"

LOBBY_COMMANDS = set(('START','JOIN','QUIT'))

class ZombieGameClient:
   def __init__(self,server,name,reader,writer):
       self.server = server
       self.reader = reader
       self.writer = writer
       self.name   = name
       self.state  = LOBBY_MODE
       self.state_handler = self.lobby_handler
       self.send_motd()
       self.timeout = 30
       self.running = True
   def close(self,msg):
       self.send_line('DISCONNECTED %s' % msg)
       self.writer.write_eof()
       self.running = False
       self.server.delete_client(self)
   def lobby_handler(self,line):
       split_line = line.split(' ')
       if len(split_line)==0: return
       command = split_line[0]
       if not command in LOBBY_COMMANDS:
          self.send_line('ERROR invalid command')
       if command=='QUIT':
          self.close('User quit')
   def send_line(self,line):
       data = '%s\n' % line
       self.writer.write(data.encode())
   @asyncio.coroutine
   def read_line(self):
       data = yield from self.reader.readline()
       return data.decode().strip('\n')
   def send_motd(self):
       self.send_line('MOTD %s' % MOTD)
       if self.state == LOBBY_MODE:
          self.send_line('MOTD Valid commands are: %s' % ' '.join(LOBBY_COMMANDS))
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
       self.clients = {}
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
       logging.info('Deleted client %s', client.name)
   def start_server(self):
       self.loop   = asyncio.get_event_loop()
       self.server = self.loop.run_until_complete(asyncio.start_server(self.handle_connection,'0.0.0.0',1337, loop=self.loop))
       logging.info('Serving on %s', self.server.sockets[0].getsockname())
       try:
          self.loop.run_forever()
       except Exception as e:
          logging.exception('Exception occurred')

if __name__=='__main__':
   game_server = ZombieGameServer()
   game_server.start_server()
