import logging
import sys
from argparse import ArgumentParser, Namespace
from itertools import chain
from pathlib import Path

from commandfile.io import read_cmdfile_yaml
from commandfile.model import Commandfile

logger = logging.getLogger(__name__)


class CommandfileArgumentParser(ArgumentParser):
    def __init__(self, *, implicit_arg: str = "--commandfile", **kwargs):
        super().__init__(**kwargs)
        self.implicit_arg = implicit_arg
        self.implicit_dest = implicit_arg.lstrip(self.prefix_chars).replace("-", "_")
        # Add implicit argument to the parser so that the commandfile can be accessed
        # by client code.
        self.add_argument(self.implicit_arg, type=Path, help="Path to a commandfile.")

    def parse_args(self, args=None, namespace=None) -> Namespace:
        remaining_argv = self._parse_commandfile_arg(args)
        return super().parse_args(remaining_argv, namespace)

    def parse_known_args(
        self, args=None, namespace=None
    ) -> tuple[Namespace, list[str]]:
        remaining_argv = self._parse_commandfile_arg(args)
        return super().parse_known_args(remaining_argv, namespace)

    def _parse_commandfile_arg(self, args=None):
        if args is None:
            args = sys.argv[1:]

        # Create a minimal parser to find the implicit argument without raising errors
        # for other unknown arguments, and without consuming the implicit argument in
        # the original parser.
        pre_parser = ArgumentParser(add_help=False)
        pre_parser.add_argument(self.implicit_arg, type=Path)
        pre_args, remaining_argv = pre_parser.parse_known_args(args)

        commandfile_path = getattr(pre_args, self.implicit_dest)
        if commandfile_path:
            commandfile = self._load_commandfile(commandfile_path)
            logger.debug("Loaded commandfile %s: %s", commandfile_path, commandfile)
            remaining_argv = [
                # Prepend commandfile args to the remaining command-line args.
                # This ensures that command-line args can override file-based args.
                *self._commandfile_to_argv(commandfile),
                *remaining_argv,
                # Append the implicit argument to the end of the list.
                *(self.implicit_arg, str(commandfile_path)),
            ]
        return remaining_argv

    def _load_commandfile(self, path: Path) -> Commandfile:
        """Load a Commandfile from a YAML file."""
        return read_cmdfile_yaml(path)

    def _commandfile_to_argv(self, commandfile: Commandfile) -> list[str]:
        """Convert a Commandfile to a list of command-line arguments."""
        argv = []
        for item in commandfile.parameters:
            argv.extend([f"--{item.key}", str(item.value)])

        for filelist in chain(commandfile.inputs, commandfile.outputs):
            argv.append(f"--{filelist.key}")
            argv.extend(map(str, filelist.files))

        return argv
