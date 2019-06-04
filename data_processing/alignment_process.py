import shutil
import os
import definitions
from collections import defaultdict
from data_gathering import scene_data
from data_preparing import path_row_grouping as prg
from data_processing import alignment_ORB, alignment_ECC
from data_processing import alignment_validator


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
        # get glacier id to make glacier output folder
        root, glacier = os.path.split(current_dir)
        glacier_dir = self.make_glacier_dir(glacier=glacier)

        processed_output_dir = os.path.join(self.output_dir, glacier)
        path_row_handler = prg.PathRowGrouping(input_dir=current_dir, output_dir=processed_output_dir)
        total_PR_output_dir = path_row_handler.determine_total_PR()
        path_row_dir_map = self.group_bands_to_path_row(current_dir=current_dir)

        # for each path_row option
        for path_row, path_row_files in path_row_dir_map.items():
            print("----------------------- ", path_row, "----------------------- ")
            B3_and_B6_lists = self.separate_bands_on_type(path_row_files)

            # for B3 then B6 lists
            for band_list in B3_and_B6_lists:
                # reference image to which the rest from the list will be aligned to
                """for band in band_list:
                    print(band, "\n")"""
                reference_image = band_list[0]
                rest_of_bands = band_list[1:]

                self.process_list(band_list=rest_of_bands,
                                  reference=reference_image,
                                  processed_output_dir=total_PR_output_dir)

        self.write_homography_result(glacier=glacier)

    def process_list(self, band_list, reference, processed_output_dir):
        """Applies the alignment process to the list of bands."""
        alignment_ORB.TOTAL_PROCESSED = 0
        alignment_ORB.VALID_HOMOGRAPHIES = 0

        # for each band except the reference
        for band in band_list:
            scene = self.get_scene_name(band)
            scene_data_handler = scene_data.SceneData(scene)

            path = scene_data_handler.get_path()
            row = scene_data_handler.get_row()
            outpur_dir = self.assign_directory(path=path, row=row, total_PR_dir=processed_output_dir)

            self.align_to_reference(scene=scene, reference=reference, image=band, processed_output_dir=outpur_dir)

    def align_to_reference(self, scene, reference, image, processed_output_dir) -> bool:
        """Checks whether the scene is between the selected months, then aligns it to the directory reference."""
        if self.check_scene_in_months(scene) is False:
            print("Scene not in months.")
            return False

        alignment_ECC.setup_alignment(reference_filename=reference,
                                      image_filename=image,
                                      result_filename=image,
                                      processed_output_dir=processed_output_dir)
        return True

    def separate_bands_on_type(self, bands_list):
        """Gathers all the B3 and B6 bands from the current directory in a list of band lists.
        Returns the list of lists of green and swir1 bands, and the band endwith options."""
        green_bands = self.get_bands_endwith(bands_list, definitions.GREEN_BAND_END)
        swir1_bands = self.get_bands_endwith(bands_list, definitions.SWIR1_BAND_END)

        bands = (green_bands, swir1_bands)

        return bands

    def get_bands_endwith(self, bands_list, endwith):
        """Gets a list of B3 and B6 bands and separates them in two lists of B3 and B6 bands."""
        band_endwith = []
        for band in bands_list:
            if band.endswith(endwith):
                band_endwith.append(band)

        return band_endwith

    def group_bands_to_path_row(self, current_dir):
        """Groups all the bands into their path/row map.
        Each path_row touple will contain a list with all the filepaths of the bands which are from that path_row."""
        # find all the path_rows to create the output directories
        total_PR_lists = defaultdict(list)

        for file in os.listdir(current_dir):
            if file.endswith((definitions.GREEN_BAND_END, definitions.SWIR1_BAND_END)):
                scene = self.get_scene_name(file)
                scene_data_handler = scene_data.SceneData(scene)

                path = scene_data_handler.get_path()
                row = scene_data_handler.get_row()
                path_row = (path, row)

                total_PR_lists[path_row].append(os.path.join(current_dir, file))

        return total_PR_lists

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

        return output_directory

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


