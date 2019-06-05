import shutil
import os
from data_gathering import scene_data
from util import strings


class PathRowGrouping:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

        self.total_PR_dirs = self.determine_total_PR()

    def determine_total_PR(self):
        """Create a map of total path and rows, with the path to the created directory for each glacier directory."""
        total_PR_dirs = {}

        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith('.TIF'):
                    file = os.path.join(root, file)
                    path_row = self.determine_path_row(file)

                    if (path_row not in total_PR_dirs.keys()) and (path_row is not None):
                        PR_dir = self.make_PR_directory(path_row)
                        total_PR_dirs[path_row] = PR_dir

        return total_PR_dirs

    def determine_path_row(self, file):
        """Determines the path and row of the scene."""
        scene = strings.get_scene_name(file)
        if scene is None:
            return None

        validator = scene_data.SceneData(scene)
        path = validator.get_path()
        row = validator.get_row()
        path_row = (path, row)

        return path_row

    def make_PR_directory(self, path_row):
        """Creates a directory with the path and row."""
        path_row_dir_filename = str(path_row[0]) + "_" + str(path_row[1])
        path_row_dir = os.path.join(self.output_dir, path_row_dir_filename)

        if os.path.exists(path_row_dir):
            shutil.rmtree(path_row_dir)
        os.mkdir(path_row_dir)

        return path_row_dir
