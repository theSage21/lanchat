import socket
from . import config
from . import utils
from . import error

# Set the socket parameters


class Client:
    broadcast_addr = ('', 33333)

    def __init__(self, server_address=None):
        if server_address is None:
            sk = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            sk.settimeout(3)
            sk.bind(Client.broadcast_addr)
            try:
                data, addr = sk.recvfrom(1024)
            except socket.timeout:
                raise error.ServerNotFound()
            data = data.decode()[1:-1]
            ip, port = data.split(',')
            ip = ip[1:-1]
            server_address = (ip, int(port))
        self.name = config.default_client_name
        self.__server = server_address
        print('Connected to ', self.__server)
        self.__sock = socket.socket()
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.__sock.connect(self.__server)

    def run(self):
        while True:
            try:
                self.__recv()
                self.__send()
            except KeyboardInterrupt:
                print('Thanks for using lanchat')
                self.__shutdown()
                break

    def __shutdown(self):
        self.__sock.close()

    def __recv(self):
        try:
            data = self.__sock.recv(1024)
        except OSError:
            pass
        else:
            data = data.decode()
            cmd, msg = data.split(':/:/')
            if cmd == config.cmd['ident']:
                utils.reply_ident(self.__sock, self.name)
            elif cmd == config.cmd['msg']:
                print(msg)

    def __send(self):
        x = input()
        msg = utils.pack_msg(x)
        self.__sock.sendall(msg)
