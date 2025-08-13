from pathlib import Path
from textwrap import dedent

from commandfile.io import read_cmdfile_yaml, write_cmdfile_yaml
from commandfile.model import Commandfile, Filelist, Parameter


def test_io_roundtrip_empty(commandfile_path: Path):
    cmdfile = Commandfile(header={}, parameters=[], inputs=[], outputs=[])
    write_cmdfile_yaml(cmdfile, commandfile_path)
    loaded_cmdfile = read_cmdfile_yaml(commandfile_path)
    assert loaded_cmdfile == cmdfile


def test_io_roundtrip(commandfile_path: Path):
    cmdfile = Commandfile(
        header={
            "some-header-key": "some-header-value",
        },
        parameters=[
            Parameter(key="some-arg", value=42),
        ],
        inputs=[
            Filelist(key="input-files", files=["input1.txt", "input2.txt"]),
        ],
        outputs=[
            Filelist(key="output-files", files=["output1.txt", "output2.txt"]),
        ],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    loaded_cmdfile = read_cmdfile_yaml(commandfile_path)
    assert loaded_cmdfile == cmdfile


def test_io_contents(commandfile_path: Path):
    cmdfile = Commandfile(
        header={"some-header-key": "some-header-value"},
        parameters=[Parameter(key="some-arg", value=42)],
        inputs=[
            Filelist(key="input-files", files=["input1.txt", "input2.txt"]),
            Filelist(key="other-input-files", files=["inputA.txt", "inputB.txt"]),
        ],
        outputs=[Filelist(key="output-files", files=["output1.txt", "output2.txt"])],
    )
    write_cmdfile_yaml(cmdfile, commandfile_path)
    contents = commandfile_path.read_text()
    print(contents)
    assert (
        contents
        == dedent("""
        header:
          some-header-key: some-header-value
        parameters:
        - key: some-arg
          value: 42.0
        inputs:
        - key: input-files
          files:
          - input1.txt
          - input2.txt
        - key: other-input-files
          files:
          - inputA.txt
          - inputB.txt
        outputs:
        - key: output-files
          files:
          - output1.txt
          - output2.txt
    """).lstrip()
    )
