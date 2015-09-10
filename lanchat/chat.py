import time
from threading import Thread
from queue import deque
from . import utils
from . import config


class Node:
    def __init__(self):
        self.alive = True
        addr = utils.get_existing_server_addr()
        if addr is None:
            self.__make_server()
        else:
            self.__make_client()

        self.name = config.client_name

    def run(self):
        """Run self on provided screen"""
        print('Starting output thread')
        o = Thread(target=self.__output_thread, name='output')
        o.start()
        self.threads.append(o)
        try:
            self.__input_thread()
        except KeyboardInterrupt:
            self.__shutdown()

    def __listen_thread(self):
        if self.mode == 's':
            while self.alive:
                try:
                    com, addr = self.__s.accept()
                except OSError:
                    pass
                else:
                    com.setblocking(False)
                    self.clients.append(com)

    def __shutdown(self):
        self.alive = False
        # wait for threads to exit
        print('\nWaiting for threads to stop.')
        while any((i.isAlive() for i in self.threads)):
            time.sleep(1)
        # send close to everyone
        if self.mode == 'c':
            print('Telling server that im leaving')
            utils.quit(self.__s)
        else:  # server
            try:
                new_server = self.clients.pop()
            except:  # nobody was left
                pass
            else:
                # tell the new server to assume
                print('Assigning new server for network')
                utils.assume_server(new_server)
                # tell others to quit
                print('Telling everyone Im leaving')
                for com in self.clients:
                    utils.quit(com)

        self.__s.close()

    def __get_instructions(self):
        "Get info from sockets"
        if self.mode == 'c':
            c, m = utils.recv(self.__s)
            inst = [(c, m, self.__s)]
        else:
            inst = []
            for com in self.clients:
                c, m = utils.recv(com)
                if c is not None:
                    inst.append((c, m, com))
        return inst

    def __process_instructions(self, inst):
        "Act on instructions recieved"
        to_send = []
        for cmd, msg, com in inst:
            if cmd not in config.CMDS:  # ignore if it is not legal
                continue
            if cmd == 'MSG':
                if self.mode == 's':
                    to_send.append(msg)
                print(msg)
            elif cmd == 'QUIT':
                if self.mode == 's':  # client quit
                    com.close()
                    self.clients.remove(com)
                else:  # server quit
                    self.__s.close()
                    self.__make_client()  # wait for new server
            elif cmd == 'ASSUME':
                if self.mode == 'c':  # assume a server role if client
                    self.__s.close()
                    self.__make_server()

    def __beacon_thread(self):
        b = utils.get_beacon()
        while self.alive:
            msg = config.broadcast_msg.encode(config.ENCODING)
            b.sendto(msg, config.broadcast_addr)
            time.sleep(1)
        b.close()

    def __output_thread(self):
        "Output thread"
        while self.alive:
            instructions = self.__get_instructions()
            self.__process_instructions(instructions)

    def __input_thread(self):
        "Input thread"
        while self.alive:
            x = input(config.prompt)
            msg = self.name + ': ' + x
            if self.mode == 'c':  # client
                utils.msg(msg, self.__s)
            else:  # server
                for com in self.clients:
                    utils.msg(msg, com)

    def __make_server(self):
        "Make this node a server"
        print('Making server, getting listening socket')
        sock = utils.get_server_sock()
        self.__s = sock
        self.clients = deque()
        self.mode = 's'
        self.threads = deque()
        print('Making beacon')
        b = Thread(target=self.__beacon_thread, name='beacon')
        b.start()
        self.threads.append(b)
        l = Thread(target=self.__listen_thread, name='listen')
        print('Starting listen thread')
        l.start()
        self.threads.append(l)

    def __make_client(self):
        "Make this node a client"
        print('Making client, getting server connection')
        addr = utils.get_existing_server_addr()
        sock = utils.get_client_sock(addr)
        self.__s = sock
        self.mode = 'c'
        self.clients = deque()
        self.threads = deque()
