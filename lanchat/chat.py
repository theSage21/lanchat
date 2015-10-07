import time
from threading import Thread, Lock
from queue import deque
from . import utils
from . import config


def notice(txt, color=False):
    "print notice"
    if color:
        txt = config.Col.WARNING + txt + config.Col.ENDC
    print(txt)


def stats(txt, color=False):
    "Print stats"
    if color:
        txt = config.Col.OKBLUE + txt + config.Col.ENDC
    print(txt)


class Node:
    def __init__(self, color=False):
        self.__client_list_lock = Lock()
        self.alive = True
        self.color = color
        addr = utils.get_existing_server_addr()
        if self.color:
            config.prompt = config.Col.OKGREEN + config.prompt + config.Col.ENDC  # lanchat prompt
        if addr is None:
            self.__make_server()
        else:
            self.__make_client()

        self.name = config.client_name

    def run(self):
        """Run self on provided screen"""
        notice('Starting output thread', self.color)
        o = Thread(target=self.__output_thread, name='output')
        o.start()
        self.threads.append(o)
        try:
            notice('Starting input thread', self.color)
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
                        stats('User count: {}'.format(len(self.clients)), self.color)

    def __shutdown(self):
        self.alive = False
        # wait for threads to exit
        notice('\nWaiting for threads to stop.', self.color)
        while any((i.isAlive() for i in self.threads)):
            time.sleep(1)
        # send close to everyone
        if self.mode == 'c':
            notice('Telling server that im leaving', self.color)
            utils.quit(self.__s)
        else:  # server
            try:
                with self.__client_list_lock:
                    new_server = self.clients.pop()
            except:  # nobody was left
                pass
            else:
                # tell the new server to assume
                notice('Assigning new server for network', self.color)
                utils.assume_server(new_server)
                # tell others to quit
                notice('Telling everyone Im leaving', self.color)
                with self.__client_list_lock:
                    for com in self.clients:
                        utils.quit(com)
        notice('LanChat is closing. Use again', self.color)
        self.__s.close()

    def __get_instructions(self):
        "Get info from sockets"
        if self.mode == 'c':
            c, m = utils.recv(self.__s)
            inst = [(c, m, self.__s)]
        else:
            inst = []
            with self.__client_list_lock:
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
                    to_send.append((msg, com))
                if self.color:
                    txt = config.Col.BOLD + msg + config.Col.ENDC
                else:
                    txt = msg
                print(txt)
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
                utils.msg(msg, self.__s)
            else:
                with self.__client_list_lock:
                    for com in self.clients:
                        if com == sender:
                            continue
                        utils.msg(msg, com)

    def __beacon_thread(self):
        b = utils.get_beacon()
        while self.alive:
            msg = config.broadcast_msg.encode(config.ENCODING)
            b.sendto(msg, config.broadcast_addr)
            time.sleep(config.beacon_delay)
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
                with self.__client_list_lock:
                    for com in self.clients:
                        utils.msg(msg, com)

    def __make_server(self):
        "Make this node a server"
        notice('Making server, getting listening socket', self.color)
        self.mode = 's'
        sock = utils.get_server_sock()
        self.__s = sock
        with self.__client_list_lock:
            self.clients = deque()
        self.threads = deque()
        notice('Making beacon', self.color)
        b = Thread(target=self.__beacon_thread, name='beacon')
        b.start()
        self.threads.append(b)
        l = Thread(target=self.__listen_thread, name='listen')
        notice('Starting listen thread', self.color)
        l.start()
        self.threads.append(l)

    def __make_client(self):
        "Make this node a client"
        notice('Making client, getting server connection', self.color)
        self.mode = 'c'
        addr = utils.get_existing_server_addr()
        sock = utils.get_client_sock(addr)
        self.__s = sock
        with self.__client_list_lock:
            self.clients = deque()
        self.threads = deque()
