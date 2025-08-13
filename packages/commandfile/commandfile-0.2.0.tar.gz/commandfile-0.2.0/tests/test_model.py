import pytest

from commandfile.model import Commandfile, Filelist, Parameter


def test_find_parameter():
    cmdfile = Commandfile(
        header={},
        parameters=[Parameter(key=f"param-{i}", value=i) for i in range(10)],
        inputs=[],
        outputs=[],
    )
    param = cmdfile.find_parameter("param-7")
    assert param.key == "param-7"
    assert param.value == 7


def test_find_parameter_not_found():
    cmdfile = Commandfile(
        header={},
        parameters=[Parameter(key=f"param-{i}", value=i) for i in range(10)],
        inputs=[],
        outputs=[],
    )
    with pytest.raises(KeyError, match="Parameter 'param-20' not found"):
        cmdfile.find_parameter("param-20")


def test_find_input():
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[
            Filelist(key=f"input-{i}", files=[f"file-{i}-{j}.txt" for j in range(3)])
            for i in range(5)
        ],
        outputs=[],
    )
    input_filelist = cmdfile.find_input("input-3")
    assert input_filelist.key == "input-3"
    assert input_filelist.files == ["file-3-0.txt", "file-3-1.txt", "file-3-2.txt"]


def test_find_input_not_found():
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[],
        outputs=[],
    )
    with pytest.raises(KeyError, match="Input filelist 'anything' not found"):
        cmdfile.find_input("anything")


def test_find_output():
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[],
        outputs=[
            Filelist(key=f"output-{i}", files=[f"file-{i}-{j}.txt" for j in range(3)])
            for i in range(5)
        ],
    )
    output_filelist = cmdfile.find_output("output-1")
    assert output_filelist.key == "output-1"
    assert output_filelist.files == ["file-1-0.txt", "file-1-1.txt", "file-1-2.txt"]


def test_find_output_not_found():
    cmdfile = Commandfile(
        header={},
        parameters=[],
        inputs=[],
        outputs=[],
    )
    with pytest.raises(KeyError, match="Output filelist 'anything' not found"):
        cmdfile.find_output("anything")
