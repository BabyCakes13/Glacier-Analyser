"""Class which gets the data from the input directory and outputs it in the right one."""
import os
from data_gathering import configuration
from util import strings


class InputBands:

    def __init__(self):
        """Setup the parser for reading the configuration file."""
        self.parser = configuration.ReadConfig()

    def get_bands(self) -> list:
        """Return the list with the full band names for the selected bands from the configuration file.
        If the file does not exist, it will not be added to the list."""
        band_names = []
        band_numbers = self.parser.get_yes_bands()
        input_path = self.parser.get_input_path()

        # search all the files in the input directory
        for file in os.listdir(str(input_path)):
            for number in band_numbers:
                if file.endswith(strings.default_endwith(number)):
                    band_names.append(file)

        return band_names
