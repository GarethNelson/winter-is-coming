
class BaseProtocolState:
   """ The protocol handler is essentially a FSM, this class is the base class for all states
   """
   def on_open(self, proto_handler=None):
       """Invoked when the ProtocolHandler opens this state

       Keyword args:
          proto_handler: The ProtocolHandler instance
       """
       pass
   def on_close(self,proto_handler=None):
       """ Invoked from ProtocolHandler.close() or when switching to this state from another one, used for cleaning up stuff

       Note:
          This method should NOT try to close the actual socket etc, the sole responsibility is to cleanup state-specific data

       Keyword args:
          proto_handler: The ProtocolHandler instance

       """ 
       pass
   def cmd_quit(self,*args,proto_handler=None):
       """Disconnect from the server"""
       proto_handler.close()
       return 'Goodbye!'
   def cmd_usage(self,*args,proto_handler=None):
       """Get usage information for a command, if no argument is given, all commands are summarised""" 
       if len(args)==1:
          if not hasattr(self,'cmd_%s' % (args[0].lower())):
             return 'ERROR: Sorry, no such command, send USAGE to get usage information for all commands'
          else:
             return getattr(self,'cmd_%s' % args[0].lower()).__doc__
       retval = ''
       for item in dir(self):
           if item.startswith('cmd_'):
              retval += '%s: %s\n' % (item.replace('cmd_',''),getattr(self,item).__doc__)
       return retval

class LobbyState(BaseProtocolState):
   """ This is the default state that all clients enter upon first connecting to the server
   """
   def __init__(self,game_lobby=None):
       self.game_lobby = game_lobby
   def cmd_list(self,*args,proto_handler=None):
       """List games on this server"""
       game_counts = self.game_lobby.get_player_counts().items()
       if len(game_counts)==0: return 'No games currently active on this server'
       retval = ''
       for k,v in game_counts:
           retval += 'GAME %s, %d players\n' % (k,v)
   def cmd_join(self,*args,proto_handler=None):
       """Join a game"""
       session = self.game_lobby.get_game(args[0]) 
       if session is None:
          return 'ERROR: No such game session, perhaps you meant to use START?'
       new_state = InGameState(game_session=game_session)
       proto_handler.enter_state(new_state)
   def cmd_name(self,*args,proto_handler=None):
       """Change username"""
       proto_handler.username=args[0]
   def cmd_start(self,*args,proto_handler=None):
       """Start a game"""
       session = self.game_lobby.get_game(args[0])
       if session is not None:
          return 'ERROR: Game already exists, perhaps you meant to use JOIN?'

class InGameState(BaseProtocolState):
   """ This is the state used when a client is currently connected to an active game
   """
   def __init__(self,game_session=None):
       self.session = game_session
   def on_open(self,proto_handler=None):
       self.session.send_join_player(self)

class ProtocolHandler:
   """ Implements the protocol as described in documentation
   """
   def __init__(self,server=None,endpoint=None,start_state=None):
       """ Keyword args:
           server:   The server this protocol handler is being run by
           endpoint: The endpoint associated with this protocol handler, usually an IP address and port, or a socket
       """
       self.server   = server
       self.endpoint = endpoint
       self.state    = start_state
       self.active   = True
       self.username = endpoint
   def close(self):
       """ Close the connection, this method should be called from other classes and NOT the method in the server
       """ 
       self.active = False
       self.state.on_close(proto_handler=self)
   def enter_State(self,new_state):
       """ Switch to a new state
       """
       self.state.on_close(proto_handler=self)
       self.state = new_state
       self.state.on_open(proto_handler=self)
   def send_line(self,line):
       """ Send a line immediately to the client

       Args:
           line(str): The line to send to the client, this will be sent via the server
       """
       self.server.sendto_client(self.endpoint,line+'\n')
   def handle_line(self,line):
       """ Handle a line sent from the client
       
       Essentially this method just parses the line of input into a command and params, then passes off to that command
   
       Args:
           line(str): The line of input to process
       """
       line       = line.strip('\n')
       split_line = line.split()
       print(split_line)
       cmd_name   = split_line[0].lower()
       if len(split_line)>1:
          cmd_args = split_line[1:]
       else:
          cmd_args = []
       try:
          response = getattr(self.state, 'cmd_%s' % cmd_name)(*cmd_args,proto_handler=self)
          return response
       except AttributeError as e:
           traceback.print_exc()
           return 'ERROR: No such command %s' % cmd_name

