import click
from abc import abstractmethod
from hatch_adder import __version__
import subprocess
import pathlib
import argparse
import sys


def cli():
    parser = argparse.ArgumentParser(
        description="A tool for adding dependencies to Hatch projects.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(title="commands", dest="command")

    COMMANDS: dict[str, type[BaseCommand]] = {
        "add": AddCommand,
        "remove": RemoveCommand,
    }

    for name, handler in COMMANDS.items():
        parser = subparsers.add_parser(name, help=handler.help)
        handler.add_arguments(parser)

    args = parser.parse_args()

    if args.command:
        COMMANDS[args.command].handler(args=args)


class BaseCommand:
    help = ""

    @classmethod
    @abstractmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def handler(cls, args):
        raise NotImplementedError

class AddCommand(BaseCommand):
    help = "Add packages to the project."
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        parser.add_argument("--no-remove-lock", action="store_false", default=True, dest="remove_lock")
        parser.add_argument("--dev", action="store_true", default=False)
        parser.add_argument("packages", nargs="*", help="Packages to add.")

    @classmethod
    def handler(cls, args):
        if len(args.packages) == 0:
            print("must supply packages. See --help")
            sys.exit(1)
            return

        cmd = [
            "uv", "add", "--no-sync", "--active",
        ]
        if args.dev:
            cmd.extend(["--optional", "dev"])
        cmd.extend(args.packages)
        subprocess.check_call(cmd)
        if args.remove_lock:
            lockfile = pathlib.Path("uv.lock")
            if lockfile.exists():
                lockfile.unlink()


class RemoveCommand(AddCommand):
    pass


def _make_command(name, handler_class: type[BaseCommand]):
    def _command():
        parser = argparse.ArgumentParser(
            description=handler_class.help,
        )
        handler_class.add_arguments(parser)
        args = parser.parse_args()
        handler_class.handler(args=args)
    return _command

# Add base level entrypoint shortcuts
hatch_add = _make_command("add", AddCommand)
hatch_remove = _make_command("remove", RemoveCommand)

if __name__ == "__main__":
    cli()
