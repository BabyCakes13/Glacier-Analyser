"""Module which handles input and output data."""
import os
import definitions


class InputOutput:
    """Class which handles input output operations."""
    def __init__(self, input_path):
        """Setup the parser for reading the configuration file."""
        self.input = input_path

    def get_ndsi_bands_paths(self) -> tuple:
        """Returns the path to the green and swir1 images."""
        green_path = None
        swir1_path = None

        for file in os.listdir(self.input):
            if file.endswith(definitions.GREEN_BAND_END):
                green_path = os.path.join(self.input, str(file))
            if file.endswith(definitions.SWIR1_BAND_END):
                swir1_path = os.path.join(self.input, str(file))

        return green_path, swir1_path
