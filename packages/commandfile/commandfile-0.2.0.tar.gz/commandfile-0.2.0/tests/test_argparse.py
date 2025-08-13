import sys
from pathlib import Path
from unittest.mock import patch

from commandfile.argparse import CommandfileArgumentParser
from commandfile.io import write_cmdfile_yaml
from commandfile.model import Commandfile, Filelist, Parameter


def test_no_args():
    parser = CommandfileArgumentParser()
    parser.add_argument("value", type=int)
    parser.add_argument("--some-flag", action="store_true")
    with patch.object(sys, "argv", ["example.py", "42", "--some-flag"]):
        args = parser.parse_args()
        assert args.value == 42
        assert args.some_flag is True


def test_standard_arguments():
    parser = CommandfileArgumentParser()
    parser.add_argument("--some-arg", type=int)
    args = parser.parse_args(["--some-arg", "42"])
    assert args.some_arg == 42


def test_commandfile_parameter(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[Parameter(key="some-arg", value="42")],
        inputs=[],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser()
    parser.add_argument("--some-arg", type=int)
    args = parser.parse_args(["--commandfile", str(commandfile_path)])
    assert args.some_arg == 42


def test_commandfile_implicit_argument_rename(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[Parameter(key="some-arg", value="42")],
        inputs=[],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser(implicit_arg="--read-that")
    parser.add_argument("--some-arg", type=int)
    args = parser.parse_args(["--read-that", str(commandfile_path)])
    assert args.some_arg == 42


def test_commandfile_implicit_argument(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser()
    args = parser.parse_args(["--commandfile", str(commandfile_path)])
    assert args.commandfile == commandfile_path


def test_commandfile_parameter_override(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[Parameter(key="some-arg", value="42")],
        inputs=[],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser()
    parser.add_argument("--some-arg", type=int)
    args = parser.parse_args(
        ["--commandfile", str(commandfile_path), "--some-arg", "100"]
    )
    assert args.some_arg == 100


def test_commandfile_filelist(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[
            Filelist(
                key="some-file-input",
                files=["file1.txt", "file2.txt"],
            ),
        ],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser()
    parser.add_argument("--some-file-input", type=str, nargs="+")
    args = parser.parse_args(["--commandfile", str(commandfile_path)])
    assert args.some_file_input == ["file1.txt", "file2.txt"]


def test_commandfile_empty_filelist(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[
            Filelist(
                key="some-file-input",
                files=[],
            ),
        ],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser()
    parser.add_argument("--some-file-input", type=str, nargs="*")
    args = parser.parse_args(["--commandfile", str(commandfile_path)])
    assert args.some_file_input == []


def test_commandfile_single_input(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[
            Filelist(
                key="single-input",
                files=["single.txt"],
            ),
        ],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser()
    parser.add_argument("--single-input", type=Path)
    args = parser.parse_args(["--commandfile", str(commandfile_path)])
    assert args.single_input == Path("single.txt")


def test_commandfile_known_args(commandfile_path: Path):
    cmdfile = Commandfile(
        header={},
        parameters=[
            Parameter(key="known-arg", value="value"),
            Parameter(key="unknown-arg", value="ignored"),
        ],
        inputs=[],
        outputs=[],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    parser = CommandfileArgumentParser()
    parser.add_argument("--known-arg", type=str)
    args, remaining_argv = parser.parse_known_args(
        ["--commandfile", str(commandfile_path)]
    )
    assert args.known_arg == "value"
    assert remaining_argv == ["--unknown-arg", "ignored"]
