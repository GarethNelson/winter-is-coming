class GameExists(Exception):
   pass

class GameLobby:
   """ This class handles the game lobby, there should only be one instance per server (obviously)
   
       Essentially it just keeps track of a bunch of game sessions
   """ 
   def __init__(self):
       self.game_sessions = {}
   def add_game(self,game_name=None,game_session=None):
       """ Adds a game session with the specified name

       If that name is already taken, throws a GameExists exception, otherwise returns None

       Keyword args:
          game_name(str): The name of the game to add
          game_session:   The actual GameSession instance to add

       """
       if game_name in self.game_sessions:
          raise GameExists()
          return
       if (game_name is None) or (game_session is None):
          raise Exception('Invalid params to add_game()!')
       self.game_sessions[game_name] = game_session
   def close_game(self,game_name=None):
       """ Closes a game session, this does NOT cleanup the actual GameSession object, it only removes the game
           from the list of game sessions.

           The caller should ensure the game actually exists before calling.
       """ 
       del self.game_session[game_none]
   def get_player_counts(self):
       """ Returns a dictionary of currently active games and player counts
       """ 
       retval = {}
       for k,v in self.game_sessions.items():
           retval[k] = v.get_player_count()
       return retval
   def get_game(self, game_name):
       """ Returns the game session if it exists, otherwise returns None
       """
       if game_name in self.game_sessions.keys():
          return self.game_sessions[game_name]
       return None # not technically required, but makes it more clear
