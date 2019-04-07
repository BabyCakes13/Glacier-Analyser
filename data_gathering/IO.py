"""Class which gets the data from the input directory and outputs it in the right one."""
import os
from data_gathering import configuration
from util import strings


class InputBands:

    def __init__(self):
        """Setup the parser for reading the configuration file."""
        self.parser = configuration.ReadConfig()
        self.input_path = self.parser.get_input_path()

    def get_selected_bands(self) -> list:
        """Return the list with the full band names for the selected bands from the configuration file.
        If the file does not exist, it will not be added to the list."""
        band_names = []
        band_numbers = self.parser.get_yes_bands()

        # search all the files in the input directory
        for file in os.listdir(str(self.input_path)):
            for number in band_numbers:
                if file.endswith(strings.default_band_endwith(number)):
                    band_names.append(file)

        return band_names

    def get_attributes(self) -> dict:
        """For now, nothing."""

        attributes = {}
        band_paths = self.get_bands_fullpath()

        for band in band_paths:
            pass
            # TODO extract band attributes from each band with gdal

        return attributes

    def get_bands_fullpath(self) -> list:
        """Returns a list with full paths to the geotiff images as Paths."""
        band_paths = []
        bands = self.get_selected_bands()

        # combine thg input path with the name of the geotiff band
        for band in bands:
            band_paths.append(self.input_path.joinpath(band))

        return band_paths
