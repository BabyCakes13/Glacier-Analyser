"""Module which handles input and output data."""
import os
from data_gathering import configuration
import definitions
from util import strings

GREEN_BAND_END = '_B3.TIF'
SWIR1_BAND_END = '_B6.TIF'


class InputOutput:
    """Class which handles input output operations."""
    def __init__(self):
        """Setup the parser for reading the configuration file."""
        self.parser = configuration.ReadConfig()

    def get_selected_bands(self) -> list:
        """Return the list with the full band names, as strings for the selected bands from the configuration file.
        If the file does not exist, it will not be added to the list."""
        band_names = []
        band_numbers = self.parser.get_yes_bands()

        for file in os.listdir(definitions.INPUT_DIR):
            for number in band_numbers:
                if file.endswith(strings.default_band_endwith(number)):
                    band_names.append(str(file))

        return band_names

    def get_bands_path(self) -> list:
        """Returns a list with full paths to the geotiff images as strings."""
        band_paths = []
        bands = self.get_selected_bands()

        for band in bands:
            band_paths.append(os.path.join(definitions.INPUT_DIR, band))

        return band_paths

    def get_NDSI_band_paths(self) -> tuple:
        """Returns the full paths to the green and swir1 bands."""
        all_tif_bands_fullpath = self.get_bands_path()
        green_fullpath = None
        swir1_fullpath = None

        for band_fullpath in all_tif_bands_fullpath:
            if GREEN_BAND_END in band_fullpath:
                green_fullpath = band_fullpath
            elif SWIR1_BAND_END in band_fullpath:
                swir1_fullpath = band_fullpath

        return green_fullpath, swir1_fullpath

