import time as _time
import socket as _socket
from . import config as _config
from . import error as _err


def __command(txt, cmd):
    if cmd not in _config.CMDS:
        raise _err.InvalidCommand(cmd + ' not a Valid command')
    string = _config.MSG_FORMAT.format(cmd, txt)
    string = string.encode(_config.ENCODING)
    return string


def msg(txt, sock):
    "Send txt as message to sock"
    string = __command(txt, 'MSG')
    sock.sendall(string)


def quit(sock):
    "Tell the sock that I quit"
    string = __command('I quit', 'QUIT')
    sock.sendall(string)


def assume_server(sock):
    "Tell the socket to assume server role"
    string = __command('Assume server', 'ASSUME')
    sock.sendall(string)


def get_server_sock():
    "Get a server socket"
    s = _socket.socket()
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, True)
    s.setblocking(False)
    s.bind(('0.0.0.0', _config.server_listen_port))
    s.listen(5)
    return s


def get_client_sock(addr):
    "Get a client socket"
    s = _socket.create_connection(addr)
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, True)
    s.setblocking(False)
    return s


def get_beacon():
    "Get a beacon socket"
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, True)
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_BROADCAST, True)
    return s


def get_existing_server_addr():
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, True)
    while True:
        try:
            s.bind(('', _config.broadcast_addr[1]))
        except:
            _time.sleep(1)
        else:
            break
    s.settimeout(_config.server_search_timeout)
    try:
        data, addr = s.recvfrom(_config.BUF_SIZE)
    except OSError:
        return None
    else:
        return (addr[0], _config.server_listen_port)


def recv(sock):
    try:
        data = sock.recv(_config.BUF_SIZE)
    except OSError:
        return None, None
    else:
        data = data.decode().split(_config.SEPERATOR)
        try:
            cmd, msg = data[0], data[1]
        except IndexError:
            cmd, msg = None, None
        return cmd, msg
