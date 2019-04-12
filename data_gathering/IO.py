"""Class which gets the data from the input directory and outputs it in the right one."""
import os
from data_gathering import configuration
from util import strings

NDSI_BANDS = ["_B3.TIF", "_B6.TIF"]


class InputBands:

    def __init__(self):
        """Setup the parser for reading the configuration file."""
        self.parser = configuration.ReadConfig()
        self.input_path = self.parser.get_input_path()

    def get_selected_bands(self) -> list:
        """Return the list with the full band names, as strings for the selected bands from the configuration file.
        If the file does not exist, it will not be added to the list."""
        band_names = []
        band_numbers = self.parser.get_yes_bands()

        # search all the files in the input directory
        for file in os.listdir(str(self.input_path)):
            for number in band_numbers:
                if file.endswith(strings.default_band_endwith(number)):
                    band_names.append(str(file))

        return band_names

    def get_bands_fullpath(self) -> list:
        """Returns a list with full paths to the geotiff images as strings."""
        band_paths = []
        bands = self.get_selected_bands()

        # combine thg input path with the name of the geotiff band
        for band in bands:
            band_paths.append(str(self.input_path.joinpath(band)))

        return band_paths

    def get_NDSI_band_paths(self) -> list:
        """Returns the string full paths to the needed bands for calculating the NDSI."""
        NDSI_bands_fullpaths = []
        all_bands_fullpath = self.get_bands_fullpath()

        for band_fullpath in all_bands_fullpath:
            if any(band in band_fullpath for band in NDSI_BANDS):
                NDSI_bands_fullpaths.append(band_fullpath)

        return NDSI_bands_fullpaths

