import pytest
import socket
from lanchat import utils, error


@pytest.fixture
def sock():
    "Return a dummy socket socket factory"
    class S:
        "Dummy socket"
        def __init__(self, err=None, tosend=None, sent=None):
            self.err = err
            self.sent = sent
            self.tosend = tosend

        def sendall(self, x):
            self.sent = x.decode()
            if self.err is not None:
                raise self.err()

        def recv(self, buff):
            if self.err is not None:
                raise self.err()
            if self.tosend is None:
                raise OSError()
            else:
                return self.tosend

    class Factory:
        def get(self, err=None, tosend=None, sent=None):
            return S(err, tosend, err)

    return Factory()


def test_command_generation():
    assert (b'hi' and b'MSG') in utils.__command('hi', 'MSG')
    assert (b'hi' and b'QUIT') in utils.__command('hi', 'QUIT')
    assert (b'hi' and b'ASSUME') in utils.__command('hi', 'ASSUME')
    assert isinstance(utils.__command('hi', 'MSG'), bytes)


def test_command_error_raise():
    with pytest.raises(error.InvalidCommand):
        utils.__command('hi', 'InvalidCmd')


def test_msg_function(sock):
    x = 'hi'
    s = sock.get()
    assert utils.msg(x, s) is None
    assert 'MSG' in s.sent
    assert 'hi' in s.sent


def test_quit_function(sock):
    s = sock.get()
    assert utils.quit(s) is None
    assert 'QUIT' in s.sent


def test_assume_server_command(sock):
    s = sock.get()
    assert utils.assume_server(s) is None
    assert 'ASSUME' in s.sent


def test_get_server_sock_command():
    s = utils.get_server_sock()
    assert s
    assert s.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
    assert s.gettimeout() == 0.0


def test_get_beacon():
    s = utils.get_beacon()
    assert s
    assert s.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
    assert s.getsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST)


def test_get_existing_server_without_server():
    e = utils.get_existing_server_addr()
    assert e is None


def test_recv_function_nothing_to_recieve(sock):
    s = sock.get()
    cmd, msg = utils.recv(s)
    assert cmd is None
    assert msg is None


def test_recv_function_something_to_recv(sock):
    msg = utils.__command('nothing', 'MSG')
    s = sock.get(tosend=msg)
    cmd, m = utils.recv(s)
    assert cmd == 'MSG'
    assert m == 'nothing'
