import time as __time
from threading import Thread as __Thread
from threading import Lock as __Lock
from queue import deque as __deque
from . import utils as __utils
from . import config as __config


def __notice(txt):
    "print notice"
    txt = __config.Col.WARNING + txt + __config.Col.ENDC
    print(txt)


def __stats(txt):
    "Print stats"
    txt = __config.Col.OKBLUE + txt + __config.Col.ENDC
    print(txt)


class Node:
    def __init__(self):
        self.__client_list_lock = __Lock()
        self.alive = True
        addr = __utils.get_existing_server_addr()
        if addr is None:
            self.__make_server()
        else:
            self.__make_client()

        self.name = __config.client_name

    def run(self):
        """Run self on provided screen"""
        __notice('Starting output thread')
        o = __Thread(target=self.__output_thread, name='output')
        o.start()
        self.threads.append(o)
        try:
            __notice('Starting input thread')
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
                    with self.__client_list_lock:
                        # prevent list form mutating
                        # while another thread is iterating
                        self.clients.append(com)
                        __stats('User count: {}'.format(len(self.clients)))

    def __shutdown(self):
        self.alive = False
        # wait for threads to exit
        __notice('\nWaiting for threads to stop.')
        while any((i.isAlive() for i in self.threads)):
            __time.sleep(1)
        # send close to everyone
        if self.mode == 'c':
            __notice('Telling server that im leaving')
            __utils.quit(self.__s)
        else:  # server
            try:
                with self.__client_list_lock:
                    new_server = self.clients.pop()
            except:  # nobody was left
                pass
            else:
                # tell the new server to assume
                __notice('Assigning new server for network')
                __utils.assume_server(new_server)
                # tell others to quit
                __notice('Telling everyone Im leaving')
                with self.__client_list_lock:
                    for com in self.clients:
                        __utils.quit(com)
        __notice('LanChat is closing. Use again')
        self.__s.close()

    def __get_instructions(self):
        "Get info from sockets"
        if self.mode == 'c':
            c, m = __utils.recv(self.__s)
            inst = [(c, m, self.__s)]
        else:
            inst = []
            with self.__client_list_lock:
                for com in self.clients:
                    c, m = __utils.recv(com)
                    if c is not None:
                        inst.append((c, m, com))
        return inst

    def __process_instructions(self, inst):
        "Act on instructions recieved"
        to_send = []
        for cmd, msg, com in inst:
            if cmd not in __config.CMDS:  # ignore if it is not legal
                continue
            if cmd == 'MSG':
                if self.mode == 's':
                    to_send.append((msg, com))
                print(msg)
            elif cmd == 'QUIT':
                if self.mode == 's':  # client quit
                    com.close()
                    with self.__client_list_lock:
                        self.clients.remove(com)
                else:  # server quit
                    self.__s.close()
                    self.__make_client()  # wait for new server
            elif cmd == 'ASSUME':
                if self.mode == 'c':  # assume a server role if client
                    self.__s.close()
                    self.__make_server()
        for msg, sender in to_send:
            if self.mode == 'c':
                __utils.msg(msg, self.__s)
            else:
                with self.__client_list_lock:
                    for com in self.clients:
                        if com == sender:
                            continue
                        __utils.msg(msg, com)

    def __beacon_thread(self):
        b = __utils.get_beacon()
        while self.alive:
            msg = __config.broadcast_msg.encode(__config.ENCODING)
            b.sendto(msg, __config.broadcast_addr)
            __time.sleep(0.1)
        b.close()

    def __output_thread(self):
        "Output thread"
        while self.alive:
            instructions = self.__get_instructions()
            self.__process_instructions(instructions)

    def __input_thread(self):
        "Input thread"
        while self.alive:
            x = input(__config.prompt)
            msg = self.name + ': ' + x
            if self.mode == 'c':  # client
                __utils.msg(msg, self.__s)
            else:  # server
                with self.__client_list_lock:
                    for com in self.clients:
                        __utils.msg(msg, com)

    def __make_server(self):
        "Make this node a server"
        __notice('Making server, getting listening socket')
        self.mode = 's'
        sock = __utils.get_server_sock()
        self.__s = sock
        with self.__client_list_lock:
            self.clients = __deque()
        self.threads = __deque()
        __notice('Making beacon')
        b = __Thread(target=self.__beacon_thread, name='beacon')
        b.start()
        self.threads.append(b)
        l = __Thread(target=self.__listen_thread, name='listen')
        __notice('Starting listen thread')
        l.start()
        self.threads.append(l)

    def __make_client(self):
        "Make this node a client"
        __notice('Making client, getting server connection')
        self.mode = 'c'
        addr = __utils.get_existing_server_addr()
        sock = __utils.get_client_sock(addr)
        self.__s = sock
        with self.__client_list_lock:
            self.clients = __deque()
        self.threads = __deque()
