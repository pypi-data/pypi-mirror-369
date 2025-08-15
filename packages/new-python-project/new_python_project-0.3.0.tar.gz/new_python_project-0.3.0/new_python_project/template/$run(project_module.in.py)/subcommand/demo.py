"""$run(project_module.in.py) 'demo' subcommand

© $run(author.in.py) <$run(email.in.py)> $run(year.in.py).

Released under the GPL version 3, or (at your option) any later version.
"""

import argparse


def run(args: argparse.Namespace) -> None:
    """'demo' command handler"""
    msg = args.message
    if args.upper:
        msg = msg.upper()
    print(f"demo says: {msg}")

def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "demo",
        help="a demo sub-command",
    )
    parser.add_argument(
        "--upper",
        help="up-case the text",
        action="store_true",
    )
    parser.add_argument("message", metavar="TEXT", help="text to print")
    parser.set_defaults(func=run)
