import logging
from argparse import ArgumentParser, Namespace
from typing import Optional

from bagsy.logger import setup_logging
from bagsy.parser import get_module_exec_cmd, get_module_setup_parser, parse_and_exec

logger = logging.getLogger(__name__)

# SBUPARSERS defines the subparsers to register into the main "bagsy" argparser
# They need to be python module with a __main__.py defining the two following functions:
#   - setup_parser of type SetupParserFunc
#   - exec_cmd of type ExecCmdFunc
SUBPARSERS = ["info", "convert"]

def setup_parser(parser: ArgumentParser) -> None:
    sub_parsers = parser.add_subparsers(dest="cmd",
                                        metavar="cmd",
                                        help=f"Available commands: {' ,'.join(SUBPARSERS)}.")
    for cmd in SUBPARSERS:
        sub_parser = sub_parsers.add_parser(cmd)
        get_module_setup_parser(f"bagsy.{cmd}")(sub_parser)


def exec_cmd(args: Namespace, parser: ArgumentParser):
    if args.cmd is not None:
        get_module_exec_cmd(f"bagsy.{args.cmd}")(args, parser)
    else:
        parser.print_help()


def main(cli_args: Optional[list[str]] = None):
    setup_logging(logging.INFO)

    parse_and_exec("bagsy",
                   "bagsy",
                   "A python cli tool to help in the creation, conversion and sharing of rosbags.",
                   cli_args)


if __name__ == "__main__":
    main()