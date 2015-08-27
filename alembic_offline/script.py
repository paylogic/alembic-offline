"""alembic-offline command line script."""
import argparse

from . import commands


def main():
    """Entry point to migration data commands."""
    parser = argparse.ArgumentParser(prog="alembic-offline")
    subparsers = parser.add_subparsers(help="sub-command help", dest='command')
    subparsers.required = True
    add_subparser_graph(subparsers)
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)



def add_subparser_graph(subparsers):
    """Add a graph subparser to main subparser collection."""
    parser_graph = subparsers.add_parser("graph", help="Graph the migrations")
    parser_graph.add_argument(
        '--filename',
        dest="filename",
        metavar="FILENAME",
        help="The filename to store the dotfile too.",
        required=True,
    )
    parser_graph.add_argument(
        "--alembic-config",
        dest="alembic_config",
        metavar="PATH",
        help="alembic config path",
        required=True,
    )
    parser_graph.add_argument(
        '--quiet',
        dest='verbose',
        action='store_false',
        help="Should it print output?",
        required=False
    )

    parser_graph.set_defaults(func=lambda args: commands.graph(
        alembic_config=args.alembic_config,
        filename=args.filename,
        verbose=args.verbose)
    )
