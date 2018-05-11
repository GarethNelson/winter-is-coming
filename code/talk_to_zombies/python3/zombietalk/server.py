import asyncio
import logging
import game_lobby
import protocol

logging.basicConfig(level=logging.INFO)


class ZombieGameServer:
   def __init__(self):
       self.clients       = {}
       self.loop          = asyncio.get_event_loop()
       self.lobby         = game_lobby.GameLobby()
       self.start_state   = protocol.LobbyState(game_lobby = self.lobby)
   async def handle_connection(self, reader, writer):
       endpoint               = ':'.join(map (lambda x: str(x), writer.get_extra_info('peername')))
       proto_handler          = protocol.ProtocolHandler(server=self, endpoint=endpoint, start_state=self.start_state)
       self.clients[endpoint] = proto_handler
       logging.info('New connection %s', endpoint)
       while proto_handler.active:
          try:
             input_line  = await reader.readline()
             input_line  = input_line.decode()
             if len(input_line)>1:
                output_line = proto_handler.handle_line(input_line) + '\n'
                writer.write(output_line.encode())
          except BrokenPipeError as e:
             logging.info('Client %s disconnected', peername)
             proto_handler.active = False

       self.delete_client(endpoint)
       writer.close()
   def delete_client(self,endpoint):
       del self.clients[endpoint]
       logging.info('Deleted client %s', endpoint)
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
