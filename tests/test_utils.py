from lanchat import utils


def test_command_generation():
    assert (b'hi' and b'MSG') in utils.__command('hi', 'MSG')
    assert (b'hi' and b'QUIT') in utils.__command('hi', 'QUIT')
    assert (b'hi' and b'ASSUME') in utils.__command('hi', 'ASSUME')
    assert isinstance(utils.__command('hi', 'MSG'), bytes)
