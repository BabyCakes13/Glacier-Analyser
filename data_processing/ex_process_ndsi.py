"""Module for the NDSI caller."""
import os
import definitions
from data_processing import alignment_validator
from data_processing import ndsi_calculator as nc


class ProcessCaller:
    """Class for NDSI calculation over a given input directory."""

    def __init__(self, input_dir, output_dir, threshold, scene):
        """Initialises the input directory, output directory and threshold for calculating the NDSI."""
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.threshold = threshold
        self.scene = scene
        self.homography_csv = os.path.join(self.output_dir, definitions.HOMOGRAPHY_CSV)

    def start_gathering(self):
        """Parses the files of the input directory, calculating the NDSI for the paired green and swir1 bands.
        Outputs the result in the specified output directory."""
        print("NDSI started...", self.input_dir)
        green_bands_paths, green_bands_number = self.get_dir_bands_paths(definitions.GREEN_BAND_END)
        swir1_bands_paths, swir1_bands_number = self.get_dir_bands_paths(definitions.SWIR1_BAND_END)

        for counter in range(0, green_bands_number):
            green_scene = self.get_scene_name(green_bands_paths[counter], definitions.GREEN_BAND_END)
            swir1_scene = self.get_scene_name(swir1_bands_paths[counter], definitions.SWIR1_BAND_END)
            if self.check_pairs(green_scene, swir1_scene):
                self.scene = green_scene
                self.process_images(green_path=green_bands_paths[counter],
                                    swir1_path=swir1_bands_paths[counter])

    def process_images(self, green_path, swir1_path):

        ndsi = nc.NDSI(green_path=green_path,
                       swir1_path=swir1_path,
                       output_dir=self.output_dir,
                       threshold=self.threshold)
        output_filename = green_scene + "_" + str(self.threshold) + "_NDSI_INT8.tif"
        ndsi.create_NDSI(output_filename, gdal.GDT_Byte)

    def count_bands(self, band_option):
        """Counts the number of bands from the input directory which end with the specified option."""
        count = 0
        for file in os.listdir(self.input_dir):
            if file.endswith(band_option):
                count += 1

        return count

    def get_dir_bands_paths(self, band_option) -> tuple:
        """Returns the path to the opted bands."""
        band_paths = []
        count = 0

        for file in os.listdir(self.input_dir):
            if file.endswith(band_option):
                band_paths.append(os.path.join(self.input_dir, str(file)))
                count += 1

        return sorted(band_paths), count

    def get_glacier_id(self):
        input_dir, glacier = os.path.split(self.input_dir)
        print(type(glacier))
        return glacier

    @staticmethod
    def check_pairs(green, swir1):
        """Checks if the scene names of the two bands are the same."""
        if green == swir1:
            return True
        return False



