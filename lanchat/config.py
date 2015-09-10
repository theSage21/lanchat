import os as _os

CMDS = ('QUIT', 'ASSUME', 'MSG')  # valid commands
BUF_SIZE = 2**10
ENCODING = 'utf-8'
SEPERATOR = ':/:/'
MSG_FORMAT = '{}' + SEPERATOR + '{}'

client_name = _os.environ.get('USER')
server_listen_port = 8888  # port on which server will listen
broadcast_addr = ('255.255.255.255', 9999)  # addr at which beacon will broadcast
prompt = 'LC:> '  # lanchat prompt
broadcast_msg = 'Stop doing naughty analysis. This chat server is not secured'  # what to broadcast
quit_key = 27  # ESC
server_search_timeout = 2


class Col:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
