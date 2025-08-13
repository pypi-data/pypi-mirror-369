from pathlib import Path

import pytest


@pytest.fixture
def commandfile_path(tmp_path: Path):
    return tmp_path / "commandfile.yaml"
