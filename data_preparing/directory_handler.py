"""
Module which creates the processing output directories hierarchy.
"""
import os
import re
import shutil
from collections import defaultdict

import definitions
from data_gathering import scene_information
from util import strings


class OutputDirHandler:
    """
    Class which creates the output folder hierarchy, as: glacier_dir/path_row1, glacier_dir/path_row2 and so on. The
    path_row directories contain the processed images.
    """

    def __init__(self, input_dir, output_dir):
        """
        Initializes the variables needed for folder hierarchy creation.
        :param input_dir: Input directory which contains the files needed to be processed.
        :param output_dir: Output directory which contains the files which will be processed.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.clearmeup = False

    def get_path_row_dir_map(self) -> map:
        """
        Create a map of all the found paths and rows pairs as keys,
        and the full path to their directory location as values.
        :return: Directory with path_row as key and full path to their directory as value.
        """
        pr_dir = {}

        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith('.TIF'):
                    file = os.path.join(root, file)
                    path_row = self.get_scene_path_row(file)

                    if (path_row not in pr_dir.keys()) and (path_row is not None):
                        print("Made directory ", path_row)
                        path_row_dir = self.make_path_row_directory(path_row)
                        pr_dir[path_row] = path_row_dir

        return pr_dir

    def get_path_row_bands_map(self) -> dict:
        """
        Groups all the bands into their path/row map.
        Each path_row touple will contain a list with all the filepaths of the bands which are from that path_row.
        :return: dict
        """
        all_pr = defaultdict(list)

        for file in os.listdir(self.input_dir):
            if file.endswith((definitions.GREEN_BAND_END, definitions.SWIR1_BAND_END)):
                scene = strings.get_scene_name(file)
                if self.validate_scene_name(scene) is False:
                    continue
                h = scene_information.SceneInformation(scene)

                path = h.get_path()
                row = h.get_row()
                path_row = (path, row)

                all_pr[path_row].append(os.path.join(self.input_dir, file))

        return all_pr

    def get_scene_path_row(self, file) -> tuple:
        """
        Determines the path and row of one scene based on the Landsat naming convention.
        :param file: The path to a Landsat image, which will have its scene extracted for path row find.
        :return: None if the scene is not found, a tuple containing the path and the row else.
        """
        path_row = None
        scene = strings.get_scene_name(file)

        h = scene_information.SceneInformation(scene)
        if self.validate_scene_name(scene=scene):
            path = h.get_path()
            row = h.get_row()
            path_row = (path, row)

        return path_row

    def prepare_path_row_maps(self) -> tuple:
        """
        Creates the two needed maps for dividing the files based on their paths and rows.
        pr_bands_map: map which has path_row as keys and a list with all the band from that directory which have the
        same paths and rows
        pr_dirs_map: map which has path_row as keys and a full path to their created directory as glacier_id/path_row
        :return: A tuple formed of the two maps.
        """
        pr_dirs_map = self.get_path_row_dir_map()
        pr_bands_map = self.get_path_row_bands_map()

        return pr_dirs_map, pr_bands_map

    def make_glacier_dir(self) -> str:
        """
        Creates and returns the path to the directory with the current glacier name.
        :return: None
        """
        glacier = self.get_glacier()
        glacier_dir = os.path.join(self.output_dir, glacier)

        if os.path.exists(glacier_dir) and self.clearmeup is False:
            shutil.rmtree(glacier_dir)
            self.clearmeup = True
        try:
            os.mkdir(glacier_dir)
        except OSError:
            pass

        return glacier_dir

    def make_path_row_directory(self, path_row) -> str:
        """
        Creates a directory of the form glacier_id/path_row which will keep the results. If the directory exists, it
        will be overwritten.
        :param path_row: Path and row of the scene, as tuple.
        :return: String containing the path to the created path_row dir.
        """
        glacier_dir = self.make_glacier_dir()
        path_row_dir_filename = str(path_row[0]) + "_" + str(path_row[1])
        path_row_dir = os.path.join(glacier_dir, path_row_dir_filename)

        try:
            os.mkdir(path_row_dir)
        except OSError:
            pass

        return path_row_dir

    def get_glacier(self) -> str:
        """
        Finds the glacier id from the input path.
        :return: A string containing the glacier id.
        """
        root, glacier = os.path.split(self.input_dir)
        return glacier

    @staticmethod
    def validate_scene_name(scene) -> bool:
        """
        Validates with a regex the Landsat scene name convention.
        :param scene: The name of the scene.
        :return: True if valid, False otherwise.
        """
        patterns = [
            re.compile(r'LC8\d{3}\d{3}\d{4}\d{3}\w{3}\d{2}'),
            re.compile(r'LC8\d{3}\d{3}\d{4}\d{3}')
        ]

        for pattern in patterns:
            if bool(re.match(pattern, scene)):
                return True
        return False
