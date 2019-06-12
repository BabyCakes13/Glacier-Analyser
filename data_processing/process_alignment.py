from colors import *
import shutil
import os
import definitions
from collections import defaultdict
from data_gathering import scene_data
from data_preparing import path_row_grouping as prg
from data_preparing import multithread_handler
from data_processing import scene as sc
from data_processing import alignment_validator
from util import strings

DEBUG = False
VALID_TRANSFORMATIONS = 0
TOTAL_TRANSFORMATIONS = 0
MULTITHREADED = True


class ProcessAlignment:
    def __init__(self, little_dir, big_input_dir, output_dir, max_threads=definitions.MAX_THREADS):
        self.little_dir = little_dir
        self.big_input_dir = big_input_dir
        self.output_dir = output_dir

        self.path_row_handler = None
        self.max_threads = max_threads

        self.INTERRUPT_SIGNAL = False

        self.mh = multithread_handler.Multithread(max_threads=self.max_threads,
                                                  handler = self.process_handler)

    def start(self):
        """Checks the type of the input directory and calls the aligner."""
        if self.big_input_dir != definitions.DEFAULT_BIG_DIR:
            self.parse_directories()
        else:
            self.parse_directory(self.little_dir)

    def parse_directories(self):
        """Parses all the subdirectories of one directory and applies the processing on found images."""
        for root, dirs, files in os.walk(self.big_input_dir):
            for dir in dirs:
                dir_fullpath = os.path.join(root, dir)
                self.parse_directory(dir_fullpath)

                if self.INTERRUPT_SIGNAL:
                    break

            if self.INTERRUPT_SIGNAL:
                break

    def parse_directory(self, current_dir):
        """Applies the changes to the input_dir which contains the images."""
        global VALID_TRANSFORMATIONS, TOTAL_TRANSFORMATIONS
        VALID_TRANSFORMATIONS = 0
        TOTAL_TRANSFORMATIONS = 0

        # get glacier id to make glacier output folder
        glacier_dir = self.make_glacier_dir(current_dir)

        # prepare output paths
        processed_output_dir = os.path.join(self.output_dir, glacier)
        path_row_handler = prg.PathRowGrouping(input_dir=current_dir, output_dir=processed_output_dir)
        total_PR_output_dir = path_row_handler.determine_total_PR()
        path_row_dir_map = self.group_bands_to_path_row(current_dir=current_dir)

        # for each path/row
        for path_row, path_row_files in path_row_dir_map.items():
            print(blue(path_row))

            green_band_list, swir1_band_list = self.separate_bands_on_type(path_row_files)
            scenes = self.make_scenes(green_band_list=green_band_list,
                                      swir1_band_list=swir1_band_list)
            if len(scenes) == 0:
                print("Not enough scenes.")
                break

            for scene in scenes:

                self.process_scene(scene=scene, reference_scene=scenes[0], path_rows_directories=total_PR_output_dir)

                if self.INTERRUPT_SIGNAL:
                    break

        if self.INTERRUPT_SIGNAL:
            return 3

        print(blue("Alignment result for " , current_dir, " is being written..."))
        self.write_homography_result(glacier=glacier)

    #TODO: refactor below with map for each returncode
    def process_handler(self, task_name, return_code):
        if return_code == 0:
            print(green("SUCCESS " + task_name))
        elif return_code == 3:
            print(yellow("INTERRRUPTED " + task_name))
        elif return_code == 1:
            print(red("FAILURE " + task_name))
        else:
            print(magenta("SOME OTHER ERROR " + task_name))

    def process_scene(self, scene, reference_scene, path_rows_directories):
        output_dir = self.assign_path_row_directory(scene=scene, total_PR_dir=path_rows_directories)
        aligned_green_filename = scene.get_scene_name() + definitions.GREEN_BAND_END
        aligned_swir1_filename = scene.get_scene_name() + definitions.SWIR1_BAND_END
        aligned_green_path = os.path.join(output_dir, aligned_green_filename)
        aligned_swir1_path = os.path.join(output_dir, aligned_swir1_filename)
        aligned_scene = sc.Scene(aligned_green_path, aligned_swir1_path)

        try:
            task = ["python3", "data_processing/alignment_ORB.py",
                    scene.green_band, scene.swir1_band,
                    reference_scene.green_band, reference_scene.swir1_band,
                    aligned_scene.green_band, aligned_scene.swir1_band,]

            self.mh.start_processing(task=task, task_name=scene.get_scene_name())

        except KeyboardInterrupt:
            print("Keyboard interrupt.")
            self.INTERRUPT_SIGNAL = True
            self.mh.kill_all_humans()
            self.mh.wait_all_process_done()

    def separate_bands_on_type(self, bands_list):
        """Gathers all the B3 and B6 bands from the current directory in a list of band lists.
        Returns the list of lists of green and swir1 bands, and the band endwith options."""
        green_bands = self.get_bands_endwith(bands_list, definitions.GREEN_BAND_END)
        swir1_bands = self.get_bands_endwith(bands_list, definitions.SWIR1_BAND_END)

        return green_bands, swir1_bands

    @staticmethod
    def get_bands_endwith(bands_list, endwith):
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
        path_row_litst = defaultdict(list)

        for file in os.listdir(current_dir):
            if file.endswith((definitions.GREEN_BAND_END, definitions.SWIR1_BAND_END)):
                print("\n")
                scene = strings.get_scene_name(file)
                scene_data_handler = scene_data.SceneData(scene)

                path = scene_data_handler.get_path()
                row = scene_data_handler.get_row()
                path_row = (path, row)

                path_row_litst[path_row].append(os.path.join(current_dir, file))

            if self.INTERRUPT_SIGNAL:
                break

        return path_row_litst

    def make_glacier_dir(self, current_dir):
        """
        Creates and returns the path to the directory with the current glacier name.
        :param current_dir: The dictionary the application is currently in.
        :return: The path to the new glacier id directory.
        """
        root, glacier = os.path.split(current_dir)
        glacier_dir = os.path.join(self.output_dir, glacier)

        if os.path.exists(glacier_dir):
            shutil.rmtree(glacier_dir)
        os.mkdir(glacier_dir)

        return glacier_dir

    def write_homography_result(self, glacier):
        """Write the alignment results of the input directory to the csv file."""
        homography_csv = os.path.join(self.output_dir, definitions.HOMOGRAPHY_CSV)
        writer = alignment_validator.HomographyCSV(glacier_id=glacier,
                                                   homography_csv=homography_csv)
        writer.start()

    @staticmethod
    def make_scenes(green_band_list, swir1_band_list) -> list:
        """
        Go through the green list and swir1 list of bands and pair them up to create the scene object.
        :param green_band_list: List of all green bands from the path row directory.
        :param swir1_band_list: List of all swir1 bands from the path row directory.
        :return: A list with Scene objects.
        """
        scenes = []
        for green in green_band_list:
            # check to see if the scene name is the same
            green_scene = strings.get_scene_name(green)

            for swir1 in swir1_band_list:
                swir1_scene = strings.get_scene_name(swir1)

                if green_scene == swir1_scene:
                    scene = sc.Scene(green, swir1)
                    scenes.append(scene)

        return scenes

    @staticmethod
    def assign_path_row_directory(scene, total_PR_dir):
        """Assigns the scene to the correct path and row output directory."""
        scene_data_handler = scene_data.SceneData(scene.get_scene_name())

        path = scene_data_handler.get_path()
        row = scene_data_handler.get_row()
        path_row = (path, row)
        output_directory = None

        for path_row_key, path_row_dir in total_PR_dir.items():
            if path_row == path_row_key:
                output_directory = path_row_dir
                break

        return output_directory


