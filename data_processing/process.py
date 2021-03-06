"""
Module which handles the processing part of the application: ndsi, alignment, difference and movement, arima.
"""
import os
import pathlib
import signal
import sys

sys.path.append(sys.path[0] + '/..')
import definitions
from data_preparing import directory_handler as odh, csv_writer
from data_processing import scenes as sc, multiprocess as mh
from util import strings

from colors import *


def interrupt_handler(signum, frame):
    """
    Method which handles the interrupt for application stop.
    :param signum: The signal name.
    :param frame: The frame in which to stop it.
    :return: raises KeyboardInterrupt.
    """
    print(definitions.PRINT_CODES[0] + "Exiting.")
    INTERRUPT_SIGNAL = True
    sys.exit(2)


DEBUG = False
MULTIPROCESSED = True
INTERRUPT_SIGNAL = False


class Process:
    """
    Class which handles processing of the input directories.
    """

    def __init__(self, big_glacier_dir, glacier_dir, output_dir, max_processes=definitions.MAX_PROCESSES):
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

        self.mh = mh.Multiprocess(max_processes=self.max_processes,
                                  handler=self.process_handler)
        self.VALID_ALIGNED = 0
        self.TOTAL_PROCESSED = 0

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

                if INTERRUPT_SIGNAL:
                    break

            if INTERRUPT_SIGNAL:
                break

    def parse_directory(self, current_dir) -> int:
        """
        Parses each little directory, creates the necessary output directories based on its files and groups them in
        scenes, then calling processing on each scene.
        :param current_dir: The current glacier directory.
        :return: Return code of the function.
        """
        h = odh.OutputDirHandler(input_dir=current_dir, output_dir=self.output_dir)
        pr_dirs_map, pr_bands_map = h.prepare_path_row_maps()

        for path_row, bands in pr_bands_map.items():
            print_string = "Processing for" + " " + str(path_row[0]) + "-" + str(path_row[1])
            print(definitions.PRINT_CODES[0] + yellow(print_string))
            green_band_list, swir1_band_list = self.separate_and_sort_bands_on_type(bands)
            scenes = self.make_scenes(green_band_list=green_band_list,
                                      swir1_band_list=swir1_band_list)
            output_dir = self.assign_path_row_directory(path_row=path_row, pr_dirs_map=pr_dirs_map)

            if len(scenes) == 0:
                print(definitions.PRINT_CODES[1] + red("There are 0 scenes."))
                break

            # processing
            for scene in scenes:
                aligned_scene = self.create_aligned_scene(scene=scene, output_dir=output_dir)

                self.process_scene(scene=scene, reference_scene=scenes[0], aligned_scene=aligned_scene)
                self.TOTAL_PROCESSED += 1

                if INTERRUPT_SIGNAL:
                    break

            if INTERRUPT_SIGNAL:
                break

            self.mh.wait_all_process_done()
            # don't write alignment csv until the ndsi work is tested.
            self.write_align_csv(path_row=path_row, output=output_dir)

        if INTERRUPT_SIGNAL:
            return 2
        else:
            return 0

    def process_scene(self, scene, reference_scene, aligned_scene) -> None:
        """
        Starts processing each scene with its reference filename by calling the parallel processing of alignment module.
        :param aligned_scene: The scene to be aligned.
        :param scene: The scene object representing the scene which will be aligned based on the reference.
        :param reference_scene: The reference scene to which the rest will be aligned.
        creating the output aligned image create path.
        :return:
        """

        try:
            task = ["python3", "data_processing/alignment_ORB.py",
                    scene.green_path, scene.swir1_path,
                    reference_scene.green_path, reference_scene.swir1_path,
                    aligned_scene.green_path, aligned_scene.swir1_path]

            self.mh.start_processing(task=task, task_name=scene.get_scene_name(), ignore_SIGINT=True)

        except KeyboardInterrupt:
            print(definitions.PRINT_CODES[1] + yellow("Keyboard interrupt."))
            INTERRUPT_SIGNAL = True
            self.mh.kill_all_processes(signal.SIGTERM)
            self.mh.wait_all_process_done()

    def process_handler(self, task_name, return_code) -> None:
        """
        Method which handles output of subprocesses.
        :param task_name: The name of the finished task.
        :param return_code: The return code of the finished task.
        :return: None
        """
        if return_code == 0:
            self.VALID_ALIGNED += 1

        return_codes = definitions.RETURN_CODES
        try:
            return_str = return_codes[return_code]
        except KeyError:
            return_str = "IDK"

        print(definitions.PRINT_CODES[0] + "Return code of ", task_name, " is ", return_code, " meaning ", return_str)
        print(definitions.PRINT_CODES[0] + "Valid: ", self.VALID_ALIGNED, " from: ", self.TOTAL_PROCESSED)

    @staticmethod
    def create_aligned_scene(scene, output_dir) -> sc.PathScene:
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

        aligned_scene = sc.PathScene(aligned_green_path, aligned_swir1_path)
        return aligned_scene

    def separate_and_sort_bands_on_type(self, bands_list) -> tuple:
        """
        Cut the list composed of both green and swir1 files into two separate green and swir1 lists. Sorts then based on
        their time of the scene, for time analysis.
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
                    scene = sc.PathScene(green, swir1)
                    scenes.append(scene)

        return scenes

    @staticmethod
    def assign_path_row_directory(path_row=None, pr_dirs_map=None) -> str:
        """
        Assigns the scene to the correct path and row output directory.
        :param path_row: The current path and row directory.
        :param pr_dirs_map: The map which contains path_row as keys and full path to their corresponding dictionaries as
        values.
        :return: The correct output directory of the band, based on its path and row.
        """
        output_directory = None

        for path_row_key, path_row_dir in pr_dirs_map.items():
            if path_row == path_row_key:
                output_directory = path_row_dir
                break

        return output_directory

    def write_align_csv(self, path_row, output) -> None:
        """
        Method which writes an alignment object to the alignment CSV.
        :param path_row: Path and row of file.
        :param output: Output path.
        :return: None
        """
        glacier_dir = pathlib.Path(output).parents[0]
        parent_dir, glacier_id = os.path.split(glacier_dir)
        path = path_row[0]
        row = path_row[1]

        if self.TOTAL_PROCESSED == 0:
            ratio = 0
        else:
            ratio = self.VALID_ALIGNED / self.TOTAL_PROCESSED
        arguments = [
            glacier_id,
            path,
            row,
            self.TOTAL_PROCESSED,
            self.VALID_ALIGNED,
            ratio
        ]

        h = csv_writer.CSVWriter(output_dir=glacier_dir,
                                 arguments=arguments)
        h.start()

        # reset for next run
        self.VALID_ALIGNED = 0
        self.TOTAL_PROCESSED = 0


if __name__ == "__main__":
    """
    Handle called from GUI.
    """

    big_glacier_dir = sys.argv[1]
    glacier_dir = sys.argv[2]
    output_dir = sys.argv[3]
    max_processes = int(sys.argv[4])

    signal.signal(signal.SIGINT, interrupt_handler)

    process_align = Process(big_glacier_dir=big_glacier_dir,
                            glacier_dir=glacier_dir,
                            output_dir=output_dir,
                            max_processes=max_processes)
    process_align.start()
