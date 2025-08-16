import importlib
import importlib.metadata
from argparse import ArgumentParser, Namespace
from typing import Optional, Callable

SetupParserFunc = Callable[[ArgumentParser], None]
ExecCmdFunc = Callable[[Namespace, ArgumentParser], None]


def get_module_setup_parser(module: str) -> SetupParserFunc:
    module = importlib.import_module(f"{module}.__main__")
    return getattr(module, "setup_parser")


def get_module_exec_cmd(module: str) -> ExecCmdFunc:
    module = importlib.import_module(f"{module}.__main__")
    return getattr(module, "exec_cmd")


def get_version():
    try:
        return importlib.metadata.version('bagSy')
    except importlib.metadata.PackageNotFoundError:
        return "dev"


def parse_and_exec(module: str,
                   name: str, description: str,
                   cli_args: Optional[list[str]]):
    parser = ArgumentParser(
        prog=name,
        description=description,
        epilog=f"bagSy {get_version()}. To contribute see https://gitlab.ensta.fr/ssh/bagsy."
    )
    get_module_setup_parser(module)(parser)
    get_module_exec_cmd(module)(parser.parse_args(cli_args), parser)
