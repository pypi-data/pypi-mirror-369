"""$run(project_name.in.py): Main module.

© $run(author.in.py) <$run(email.in.py)> $run(year.in.py).

Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import importlib.metadata
import logging
import os
import sys
import warnings

from .subcommand import commands
from .warnings_util import die, simple_warning


VERSION = importlib.metadata.version("$run(project_module.in.py)")


def main(argv: list[str] = sys.argv[1:]) -> None:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="$run(description.in.py)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"""%(prog)s {VERSION}
© $run(year.in.py) $run(author.in.py) <$run(email.in.py)>
$run(project_home_page.in.py)
Distributed under the GNU General Public License version 3, or (at
your option) any later version. There is no warranty.""",
    )
    parser.add_argument(
        "--greeting",
        help="specify the greeting to use",
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Locate and load sub-commands
    command_list = commands()
    if len(command_list) > 0:
        subparsers = parser.add_subparsers(
            title="subcommands", metavar="SUBCOMMAND"
        )
        for command in command_list:
            command.add_subparser(subparsers)

    args = parser.parse_args(argv)

    # Run command
    try:
        if "func" in args:
            args.func(args)
        else:
            print(f"{args.greeting or 'Hello'} from $run(project_name.in.py)!")
    except Exception as err:
        if "DEBUG" in os.environ:
            logging.error(err, exc_info=True)
        else:
            die(f"{err}")
        sys.exit(1)
