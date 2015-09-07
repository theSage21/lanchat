import argparse
from . import client, server


def get_parser():
    parser = argparse.ArgumentParser(description='LAN chat')
    return parser


def add_args(parser):
    parser.add_argument('-v',
                        '--version',
                        help='Version')


def process_args(args):
    if args.version:
        from lanchat import __version__
        version = 'v ' + '.'.join(map(str, __version__))
        print(version)
        return None
