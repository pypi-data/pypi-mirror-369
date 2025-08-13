from commandfile.model_generated import (
    Commandfile as BaseCommandfile,
)
from commandfile.model_generated import (
    Filelist,
    Parameter,
)


class Commandfile(BaseCommandfile):
    """Extended Commandfile model with helper methods."""

    def find_parameter(self, key: str) -> Parameter:
        """Find a parameter by its key."""
        for param in self.parameters:
            if param.key == key:
                return param
        raise KeyError(f"Parameter {key!r} not found")

    def find_input(self, key: str) -> Filelist:
        """Find an input filelist by its key."""
        for file_inputs in self.inputs:
            if file_inputs.key == key:
                return file_inputs
        raise KeyError(f"Input filelist {key!r} not found")

    def find_output(self, key: str) -> Filelist:
        """Find an output filelist by its key."""
        for file_outputs in self.outputs:
            if file_outputs.key == key:
                return file_outputs
        raise KeyError(f"Output filelist {key!r} not found")
