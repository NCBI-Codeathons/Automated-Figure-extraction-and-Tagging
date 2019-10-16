from abc import ABC, abstractmethod
from typing import Any, Iterable, Type, cast
import sys
import argparse
import importlib
import pkgutil
import os


class Cog(ABC):  # pragma: no cover
    """
    Base class for application.
    """

    @staticmethod
    @abstractmethod
    def initialize(arg_parse: Any) -> None:
        """
        Will be called by manager to place app into registry.
        """
        pass


def get_all_commands() -> Iterable[Type[Cog]]:
    """
    List all applications.
    """
    loader = pkgutil.get_loader('figtag.apps')
    filename = cast(Any, loader).get_filename()
    pkg_dir = os.path.dirname(filename)
    for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):
        importlib.import_module('.apps.' + name, __package__)

    return Cog.__subclasses__()


def main() -> None:  # pragma: no cover
    """
    Forward call to application passed as first argument.

    Used by pex as module entry point and allow to call scripts in bin folder.
    """

    parser = argparse.ArgumentParser(
        prog="manage.py",
        description='Common entry point to figtag')

    subparsers = parser.add_subparsers(
        title="Commands (pass -h to a command to get its details)",
        metavar="command")

    for m in get_all_commands():
        m.initialize(subparsers)

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))
