import socket
import time
from . import utils
from . import config


class Beacon:
    addr = ('255.255.255.255', 33333)

    def __init__(self, data_to_broadcast):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.__data = data_to_broadcast.encode('utf-8')

    def flash(self):
        self.__s.sendto(self.__data, Beacon.addr)

    def close(self):
        self.__s.close()


class Server:
    def __init__(self):
        self.__sock = socket.socket()
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.__sock.setblocking(False)
        self.__sock.bind(config.server_addr)
        self.__sock.listen(5)
        self.__beacon = Beacon(str(self.__sock.getsockname()))

        self.__users = {}
        self.__recieved = []
        self.__to_send = []

    def run(self):
        try:
            while True:
                try:
                    com, addr = self.__sock.accept()
                except OSError:
                    pass
                else:
                    com.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                    com.setblocking(False)
                    no = len(self.__users)
                    self.__users[str(no)] = com
                    utils.ask_to_identify(com)
                finally:
                    self.__beacon.flash()
                    msgs = self.__recieve()
                    msgs = self.__categorize(msgs)
                    self.__retransmit(msgs)
        except KeyboardInterrupt:
            print('Shutting down server')
            self.__shutdown()

    def __shutdown(self):
        self.__sock.close()
        for u, com in self.__users.items():
            com.close()

    def __recieve(self):
        msgs = []
        for user, com in self.__users.items():
            try:
                data = com.recv(512)
            except OSError:
                pass
            else:
                data = data.decode()
                try:
                    cmd, msg = data.split(':/:/')
                except ValueError:
                    pass
                else:
                    msgs.append((user, cmd, msg))
        return msgs

    def __categorize(self, messages):
        to_transmit = []
        for user, cmd, msg in messages:
            if cmd == config.cmd['ident']:
                com = self.__users.pop(user)
                self.__users[msg] = com
                print(user, ' identified as ', msg)
            elif cmd == config.cmd['msg']:
                stamp = time.time()
                to_transmit.append((stamp, user, msg))
        to_transmit.sort(key=lambda x: x[0])
        return to_transmit

    def __retransmit(self, messages):
        for stamp, sender, msg in messages:
            for reciever, com in self.__users.items():
                if sender == reciever:
                    continue
                msg = utils.pack_msg(msg)
                com.sendall(msg)
