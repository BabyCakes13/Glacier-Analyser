import shutil
import os
import definitions
from collections import defaultdict
from data_gathering import scene_data
from data_preparing import path_row_grouping as prg
from data_processing import alignment_algorithm
from data_processing import alignment_validator
from data_gathering import test_alignment


class ProcessAlignment:
    def __init__(self, little_dir, big_input_dir, output_dir, months):
        self.little_dir = little_dir
        self.big_input_dir = big_input_dir
        self.output_dir = output_dir

        self.months = months
        self.homography_csv = os.path.join(self.output_dir, definitions.HOMOGRAPHY_CSV)
        self.path_row_handler = None

    def start(self):
        """Checks the type of the input directory and calls the aligner."""
        if self.big_input_dir != definitions.DEFAULT_BIG_DIR:
            self.parse_directories()
        else:
            self.parse_directory(self.little_dir)

    def parse_directories(self):
        """Parses all the subdirectories of one directory and applies the processing on found images."""
#        print("Parsing big directory: ", self.big_input_dir )

        for root, dirs, files in os.walk(self.big_input_dir):
            for dir in dirs:
                dir_fullpath = os.path.join(root, dir)
                self.parse_directory(dir_fullpath)

    def parse_directory(self, current_dir):
        """Applies the changes to the input_dir which contains the images."""
        # get glacier id to make glacier specific folder
        root, glacier = os.path.split(current_dir)
        glacier_dir = self.make_glacier_dir(glacier=glacier)
        bands, band_options = self.prepare_bands(current_dir)

        # group to path row directory
        path_row_handler = prg.PathRowGrouping(input_dir=current_dir, output_dir=glacier_dir)
        total_PR_dir = path_row_handler.determine_total_PR()

        alignment_algorithm.TOTAL_PROCESSED = 0
        alignment_algorithm.VALID_HOMOGRAPHIES = 0

        self.group_bands(current_dir=current_dir, total_PR_dir=total_PR_dir)
        # for B3 then B6
        """ for count, option in enumerate(band_options):
          # iterate over all band lists
          for band in bands[count]:
            scene = self.get_scene_name(band)
            scene_data_handler = scene_data.SceneData(scene)
            path = scene_data_handler.get_path()
            row = scene_data_handler.get_row()
            outpur_dir = self.assign_directory(path=path, row=row, total_PR_dir=total_PR_dir)

            self.align_to_reference(band=band,
                                      band_option=option,
                                      reference=references[count],
                                      aligned_dir=outpur_dir)

        self.write_homography_result(glacier=glacier) """

    def prepare_bands(self, current_dir):
        """Gathers all the B3 and B6 bands from the current directory in a list of band lists.
        Returns the list of lists of green and swir1 bands, and the band endwith options."""
        green_bands = self.get_bands(definitions.GREEN_BAND_END, current_dir)
        swir1_bands = self.get_bands(definitions.SWIR1_BAND_END, current_dir)

        band_options = (definitions.GREEN_BAND_END, definitions.SWIR1_BAND_END)
        bands = (green_bands, swir1_bands)

        return bands, band_options

    def group_bands(self, current_dir, total_PR_dir):
        """Groups all the bands into their path/row map."""
        total_PR_lists = defaultdict(list)

        for file in os.listdir(current_dir):
            if file.endswith((definitions.GREEN_BAND_END, definitions.SWIR1_BAND_END)):
                scene = self.get_scene_name(file)
                scene_data_handler = scene_data.SceneData(scene)

                path = scene_data_handler.get_path()
                row = scene_data_handler.get_row()
                path_row = (path, row)
                print("File's path and row: ", path_row)

                total_PR_lists[path_row].append(file)

            for key, value in total_PR_dir.items():
                print(key, ": ", value)

    def align_to_reference(self, band, band_option, reference, aligned_dir) -> bool:
        """Checks whether the scene is between the selected months, then aligns it to the directory reference."""
        scene = self.get_scene_name(band)

        if self.check_scene_in_months(scene) is False:
            return False
        aligned_filename = scene + band_option

        alignment_algorithm.setup_alignment(reference_filename=reference,
                                            tobe_aligned_filename=band,
                                            result_filename=aligned_filename,
                                            aligned_dir=aligned_dir)
        return True

    def make_glacier_dir(self, glacier):
        glacier_dir = os.path.join(self.output_dir, glacier)

        if os.path.exists(glacier_dir):
            shutil.rmtree(glacier_dir)
        os.mkdir(glacier_dir)

        return glacier_dir

    def check_scene_in_months(self, scene) -> bool:
        """Checks whether the scene is taken in a valid month or not."""
        validator = scene_data.SceneData(scene)
        month = validator.get_month()

        if month in self.months:
            return True
        return False

    def write_homography_result(self, glacier):
        """Write the alignment results of the input directory to the csv file."""
        writer = alignment_validator.HomographyCSV(glacier_id=glacier,
                                                   homography_csv=self.homography_csv)
        writer.start()

    @staticmethod
    def assign_directory(path, row, total_PR_dir):
        """Assigns the scene to the correct path and row output directory."""
        path_row = (path, row)
        output_directory = None

        for path_row_key, path_row_dir in total_PR_dir.items():
            if path_row == path_row_key:
                output_directory = path_row_dir
                break

        print(output_directory)
        return output_directory

    @staticmethod
    def get_bands(band_option, input_dir):
        """Parses through the files of the given directory and selects a list with the bands which was opted for."""
        bands = []

        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith(band_option):
                    bands.append(os.path.join(root, file))

        return bands

    @staticmethod
    def get_scene_name(band_path):
        """Returns the scene name."""
        input_dir, band = os.path.split(band_path)

        if band.endswith(definitions.GREEN_BAND_END):
            split = band.split(definitions.GREEN_BAND_END)
        else:
            split = band.split(definitions.SWIR1_BAND_END)
        scene = split[0]

        return str(scene)

# TODO scale down image 10x so that the aligner finds better matches, calculate homography and all transformations on that, then at the last step, apply the transformation on the big image


