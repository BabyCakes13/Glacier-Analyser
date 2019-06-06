import gdal
from data_processing import ndsi_calculator
from util import strings
import definitions


class ProcessNDSI:
    def __init__(self, green_list, swir1_list, output_dir):
        """Green list contains full path to all B3 bands from the directory."""
        """Swir1 list contains full path to all B6 bands from the directory."""
        self.green_list = green_list
        self.swir1_list = swir1_list
        self.output_dir = output_dir

        self.pairs = self.make_pairs()

    def start_ndsi(self):
        """Start the NDSI process. Parses each pair and creates the NDSI from it."""
        # process each pair of B3 and B6
        for pair in self.pairs:
            ndsi = ndsi_calculator.NDSI(green_path=pair(0),
                                        swir1_path=pair(1),
                                        output_dir=self.output_dir,
                                        threshold=definitions.THRESHOLD)
            scene = strings.get_scene_name(pair(0))
            result_filename = scene + "_" +  definitions.THRESHOLD + ".TIF"
            ndsi.create_NDSI(result_filename, gdal.GDT_Byte)

    def make_pairs(self) -> list:
        """Go through the green list and swir1 list of bands and pair them up."""
        pairs = []
        for green in self.green_list:
            green_scene = strings.get_scene_name(green)

            for swir1 in self.swir1_list:
                swir1_scene = strings.get_scene_name(swir1)

                if green_scene == swir1_scene:
                    pair = (green, swir1)
                    pairs.append(pair)

        return pairs
