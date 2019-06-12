from colors import *
import os
import definitions
from data_gathering import scene_data as sd
from data_preparing import output_dir_handler as odh
from data_preparing import multiprocess_handler as mh
from data_processing import scene as sc
from data_processing import alignment_validator as av
from util import strings

DEBUG = False
VALID_TRANSFORMATIONS = 0
TOTAL_TRANSFORMATIONS = 0
MULTIPROCESSED = True


class Process:
    def __init__(self, glacier_dir, big_glacier_dir, output_dir, max_processes=definitions.MAX_PROCESSES):
        """
        The constructor of the Process class.
        :param glacier_dir: The glacier directory.
        :param big_glacier_dir: The directory which contains more glacier directories.
        :param output_dir: The directory assigned for processing writing.
        :param max_processes: Number of processes the application works with.
        """
        self.glacier_dir = glacier_dir
        self.big_glacier_dir = big_glacier_dir
        self.output_dir = output_dir

        self.max_processes = max_processes

        self.INTERRUPT_SIGNAL = False

        self.mh = mh.Multiprocess(max_processes=self.max_processes,
                                  handler=self.process_handler)

    def start(self) -> None:
        """
        Checks the type of the input directory and calls the process accordingly."
        :return: None
        """
        if self.big_glacier_dir:
            self.parse_directories()
        else:
            self.parse_directory(self.glacier_dir)

    def parse_directories(self) -> None:
        """
        Parses all the subdirectories of the big directory.
        :return: None
        """
        for root, dirs, files in os.walk(self.big_glacier_dir):
            for dir in dirs:
                dir_fullpath = os.path.join(root, dir)

                self.parse_directory(dir_fullpath)

                if self.INTERRUPT_SIGNAL:
                    break

            if self.INTERRUPT_SIGNAL:
                break

    def parse_directory(self, current_dir) -> int:
        """
        Parses each little directory, creates the necessary output directories based on its files and groups them in
        scenes, then calling processing on each scene.
        :param current_dir: The current glacier directory.
        :return: Return code of the function.
        """
        global VALID_TRANSFORMATIONS, TOTAL_TRANSFORMATIONS
        VALID_TRANSFORMATIONS = 0
        TOTAL_TRANSFORMATIONS = 0

        h = odh.OutputDirHandler(input_dir=current_dir, output_dir=self.output_dir)
        pr_dirs_map, pr_bands_map = h.prepare_path_row()

        for path_row, bands in pr_bands_map.items():
            green_band_list, swir1_band_list = self.separate_bands_on_type(bands)
            scenes = self.make_scenes(green_band_list=green_band_list,
                                      swir1_band_list=swir1_band_list)
            if len(scenes) == 0:
                print(blue("There are 0 scenes."))
                break

            # processing
            for scene in scenes:
                self.process_scene(scene=scene, reference_scene=scenes[0], pr_dirs_map=pr_dirs_map)

                if self.INTERRUPT_SIGNAL:
                    break

        if self.INTERRUPT_SIGNAL:
            return 2

        # print(blue("Alignment result for "), current_dir, blue(" is being written..."))
        # self.write_homography_result(glacier=glacier)

        return 0

    def process_scene(self, scene, reference_scene, pr_dirs_map):
        """
        Starts processing each scene with its reference filename by calling the parallel processing of alignment module.
        :param scene: The scene object representing the scene which will be aligned based on the reference.
        :param reference_scene: The reference scene to which the rest will be aligned.
        :param pr_dirs_map: The map which contains all the path and row pairs with their full path to the output dir for
        creating the output aligned image write path.
        :return:
        """
        output_dir = self.assign_path_row_directory(band=scene, pr_dirs_map=pr_dirs_map)
        aligned_scene = self.create_aligned_scene(scene=scene, output_dir=output_dir)

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

    @staticmethod
    def process_handler(task_name, return_code):
        return_codes = definitions.RETURN_CODES
        return_code = return_codes[return_code]
        print(return_code, " ", task_name)

    @staticmethod
    def create_aligned_scene(scene, output_dir) -> sc.Scene:
        """
        Creates the necessary attributes for creating the aligned image scene.
        :param scene: The scene object.
        :param output_dir: The directory in which the aligned image will be written.
        :return: Returns a Scene object.
        """
        aligned_green_filename = scene.get_scene_name() + definitions.GREEN_BAND_END
        aligned_swir1_filename = scene.get_scene_name() + definitions.SWIR1_BAND_END

        aligned_green_path = os.path.join(output_dir, aligned_green_filename)
        aligned_swir1_path = os.path.join(output_dir, aligned_swir1_filename)

        aligned_scene = sc.Scene(aligned_green_path, aligned_swir1_path)
        return aligned_scene

    def separate_bands_on_type(self, bands_list) -> tuple:
        """
        Separated the list composed of both green and swir1 files into two separate green and swir1 lists.
        :param bands_list: List composed of green and swir1 files.
        :return: Tuple formed of the separated green and swir1 files.
        """
        green_bands = self.get_bands_endwith(bands_list, definitions.GREEN_BAND_END)
        swir1_bands = self.get_bands_endwith(bands_list, definitions.SWIR1_BAND_END)

        return green_bands, swir1_bands

    @staticmethod
    def get_bands_endwith(together, endwith) -> list:
        """
        Creates a new list from the received one, choosing only the elements which end with the endwith parameter.
        :param together: List of band files.
        :param endwith: Comparison end of the file.
        :return: Returns the pruned list.
        """
        separated = []
        for band in together:
            if band.endswith(endwith):
                separated.append(band)

        return separated

    def write_homography_result(self, glacier) -> None:
        """
        Write the results of the process into the csv file
        :param glacier: The id of the glacier.
        :return: None
        """
        homography_csv = os.path.join(self.output_dir, definitions.HOMOGRAPHY_CSV)
        writer = av.HomographyCSV(glacier_id=glacier,
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
    def assign_path_row_directory(band, pr_dirs_map):
        """
        Assigns the scene to the correct path and row output directory.
        :param band: File which represents a Landsat 8 band.
        :param pr_dirs_map: The map which contains path_row as keys and full path to their corresponding dictionaries as
        values.
        :return: The correct output directory of the band, based on its path and row.
        """
        scene = band.get_scene_name()
        h = sd.SceneData(scene=scene)

        path = h.get_path()
        row = h.get_row()
        path_row = (path, row)
        
        output_directory = None

        for path_row_key, path_row_dir in pr_dirs_map.items():
            if path_row == path_row_key:
                output_directory = path_row_dir
                break

        return output_directory

