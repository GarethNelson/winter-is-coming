class BaseProtocolState:
   """ The protocol handler is essentially a FSM, this class is the base class for all states
   """
   def on_close(self,proto_handler=None):
       """ Invoked from ProtocolHandler.close(), used for cleaning up stuff

       Note:
          This method should NOT try to close the actual socket etc, the sole responsibility is to cleanup state-specific data

       Keyword args:
          proto_handler: The ProtocolHandler instance

       """ 
       pass
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
  pass

class ProtocolHandler:
   """ Implements the protocol as described in documentation
   """
   def __init__(self,server=None,endpoint=None,start_state=LobbyState()):
       """ Keyword args:
           server:   The server this protocol handler is being run by
           endpoint: The endpoint associated with this protocol handler, usually an IP address and port, or a socket
       """
       self.server   = server
       self.endpoint = endpoint
       self.state    = start_state
   def close(self):
       """ Close the connection, this method should be called from other classes and NOT the method in the server
       """ 
       self.state.on_close(proto_handler=self)
   def handle_line(self,line):
       """ Handle a line sent from the client
       
       Essentially this method just parses the line of input into a command and params, then passes off to that command
   
       Args:
           line(str): The line of input to process
       """
       line       = line.strip('\n')
       split_line = line.split()
       cmd_name   = split_line[0].lower()
       cmd_args   = split_line[1:]
       try:
          response = getattr(self.state, 'cmd_%s' % cmd_name)(*cmd_args,proto_handler=self)
          return response
       except AttributeError as e:
          return 'ERROR: No such command %s' % cmd_name

