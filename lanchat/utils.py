import time
import socket
from . import config, error


def __command(txt, cmd):
    if cmd not in config.CMDS:
        raise error.InvalidCommand
    string = config.MSG_FORMAT.format(cmd, txt)
    string = string.encode(config.ENCODING)
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
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.setblocking(False)
    s.bind(('0.0.0.0', config.server_listen_port))
    s.listen(5)
    return s


def get_client_sock(addr):
    "Get a client socket"
    s = socket.create_connection(addr)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.setblocking(False)
    return s


def get_beacon():
    "Get a beacon socket"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    return s


def get_existing_server_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    while True:
        try:
            s.bind(('', config.broadcast_addr[1]))
        except:
            time.sleep(1)
        else:
            break
    s.settimeout(config.server_search_timeout)
    try:
        data, addr = s.recvfrom(config.BUF_SIZE)
    except OSError:
        return None
    else:
        return (addr[0], config.server_listen_port)


def recv(sock):
    try:
        data = sock.recv(config.BUF_SIZE)
    except OSError:
        return None, None
    else:
        data = data.decode().split(config.SEPERATOR)
        try:
            cmd, msg = data[0], data[1]
        except IndexError:
            cmd, msg = None, None
        return cmd, msg
