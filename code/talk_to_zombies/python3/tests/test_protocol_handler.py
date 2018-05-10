from zombietalk import protocol

def test_usage():
    """ Test we can send a USAGE command and get a response that isn't an error
    """
    handler = protocol.ProtocolHandler()
    retval  = handler.handle_line('USAGE\n')
    assert not retval.startswith('ERROR')

def test_invalid_cmd():
    """ Test sending an invalid command and make sure we get a response that IS an error
    """
    handler = protocol.ProtocolHandler()
    retval  = handler.handle_line('NOSUCHCMD\n')
    assert retval.startswith('ERROR')
