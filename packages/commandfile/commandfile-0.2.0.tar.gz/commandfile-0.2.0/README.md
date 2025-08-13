# Commandfile

[![PyPI version](https://img.shields.io/pypi/v/commandfile.svg)](https://pypi.org/project/commandfile/)
[![Build status](https://img.shields.io/github/actions/workflow/status/lisa-sgs/commandfile/ci.yml?branch=develop)](https://github.com/lisa-sgs/commandfile/actions)
[![Coverage Status](https://coveralls.io/repos/github/lisa-sgs/commandfile/badge.svg?branch=develop)](https://coveralls.io/github/lisa-sgs/commandfile?branch=develop)
[![License](https://img.shields.io/pypi/l/commandfile)](https://opensource.org/license/apache-2-0)

## Purpose and scope

Commandfile defines a file format to pass arguments and runtime metadata to executables.
Its intended use case is to simplify and harmonize the calling convention of scientific modules in the [LISA](https://www.lisamission.org/) Scientific Ground Segment.

## Usage

This project provides a drop-in replacement for the `ArgumentParser` provided by [`argparse`](https://docs.python.org/3/library/argparse).

```python
# example.py
from commandfile.argparse import CommandfileArgumentParser as ArgumentParser

parser = ArgumentParser()
parser.add_argument("--some-value", type=int, required=True)
args = parser.parse_args()
print(args.some_value)
```

When using this parser, your program can either be executed by passing arguments on the command-line, or by providing a single `--commandfile` argument compliant with the [file format specification](src/commandfile/data/schema.json).
When developing locally, both approaches can be combined, the command-line arguments overriding the arguments specified in the commandfile.

```console
$ cat example-cmdfile.yaml
header:
  version: 1.21.4
parameters:
  - key: some-value
    value: '42'
inputs: []
outputs: []
$ example.py --commandfile example-cmdfile.yaml
42
$ example.py --commandfile example-cmdfile.yaml --some-value 24
24
```
