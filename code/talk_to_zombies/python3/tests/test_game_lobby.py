from zombietalk import game_lobby

class MockPlayer:
   pass

class MockGameSession:
   def __init__(self,n=1):
       self.n = n
   def get_player_count(self):
       return self.n

def test_player_count():
    test_lobby = game_lobby.GameLobby()
    test_session_a = MockGameSession(1)
    test_session_b = MockGameSession(2)
    test_session_c = MockGameSession(3)
    test_lobby.add_game('TestA', test_session_a)
    test_lobby.add_game('TestB', test_session_b)
    test_lobby.add_game('TestC', test_session_c)
    player_counts = test_lobby.get_player_counts()
    assert player_counts == {'TestA':1, 'TestB':2, 'TestC':3}


           
