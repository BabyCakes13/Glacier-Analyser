"""Class which gets the data from the input directory and outputs it in the right one."""
import os
from data_gathering import configuration
from util import strings

GREEN_BAND_END = '_B3.TIF'
SWIR1_BAND_END = '_B6.TIF'


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

    def get_NDSI_band_paths(self) -> tuple:
        """Returns the full paths to the green and swir1 bands."""
        all_tif_bands_fullpath = self.get_bands_fullpath()
        green_fullpath = None
        swir1_fullpath = None

        for band_fullpath in all_tif_bands_fullpath:
            if GREEN_BAND_END in band_fullpath:
                green_fullpath = band_fullpath
            elif SWIR1_BAND_END in band_fullpath:
                swir1_fullpath = band_fullpath

        return green_fullpath, swir1_fullpath

