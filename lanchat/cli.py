import argparse
from . import client, server, error


def get_parser():
    parser = argparse.ArgumentParser(description='LAN chat')
    return parser


def add_args(parser):
    parser.add_argument('-v',
                        '--version',
                        help='Version')
    parser.add_argument('-s',
                        '--server',
                        help='Run server')
    return parser


def process_args(args):
    if args.version:
        from lanchat import __version__
        version = 'v ' + '.'.join(map(str, __version__))
        print(version)
        return None
    elif args.server:
        s = server.Server()
        return s
    else:
        try:
            c = client.Client()
        except error.ServerNotFound:
            s = server.Server()
            import threading
            t = threading.Thread(target=s.run, daemon=True)
            t._start()
            c = client.Client()
            return c


def main():
    p = get_parser()
    p = add_args(p)
    a = p.parse_args()
    ret = process_args(a)
    if ret is not None:
        ret.run()
