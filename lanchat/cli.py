import argparse
from . import chat


def get_parser():
    """
    Return a parser for the package
    """
    parser = argparse.ArgumentParser(description='''
    Distributed LAN chat
    ''')
    return parser


def add_arguments(parser):
    parser.add_argument('-v',
                        '--version',
                        action='store_true',
                        help='Display version info')
    return parser


def process_args_and_get_node(args):
    if args.version:
        from lanchat import __version__
        version = 'v ' + '.'.join(map(str, __version__))
        print(version)
        return None
    return chat.Node()


def main():
    p = get_parser()
    p = add_arguments(p)
    args = p.parse_args()
    n = process_args_and_get_node(args)
    if n is not None:
        n.run()
