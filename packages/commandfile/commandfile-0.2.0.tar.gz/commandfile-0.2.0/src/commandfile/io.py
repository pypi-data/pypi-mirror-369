from pathlib import Path

import yaml

from commandfile.model import Commandfile


def write_cmdfile_yaml(cmdfile: Commandfile, path: Path):
    """Write a Commandfile object to a YAML file."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(cmdfile.model_dump(), f, sort_keys=False)


def read_cmdfile_yaml(path: Path) -> Commandfile:
    """Read a Commandfile object from a YAML file."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Commandfile(**raw)
