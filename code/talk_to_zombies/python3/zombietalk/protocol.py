import traceback

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
   def close(self):
       """ Close the connection, this method should be called from other classes and NOT the method in the server
       """ 
       self.active = False
       self.state.on_close(proto_handler=self)

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

