from . import config


def ask_to_identify(sock):
    cmd = '{}:/:/{}'.format(config.cmd['ident'], 'ident')
    sock.sendall(cmd.encode('utf-8'))


def reply_ident(sock, name):
    cmd = '{}:/:/{}'.format(config.cmd['ident'], name)
    sock.sendall(cmd.encode('utf-8'))


def pack_msg(msg):
    cmd = '{}:/:/{}'.format(config.cmd['msg'], msg)
    return cmd.encode('utf-8')
