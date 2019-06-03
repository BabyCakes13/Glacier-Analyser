import shutil
import os
import definitions
from data_gathering import scene_data


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
                    file_path = os.path.join(root, file)
                    path_row = self.determine_PR(file, file_path)

                    if (path_row not in total_PR_dirs.keys()) and (path_row is not None):
                        PR_dir = self.make_PR_directory(path_row)
                        total_PR_dirs[path_row] = PR_dir

        print(total_PR_dirs)
        return total_PR_dirs

    def determine_PR(self,file, file_path):
        """Determines the path and row of the scene."""
        scene = self.check_scene_exists(file, file_path)
        if scene is None:
            return None

        validator = scene_data.SceneData(scene)
        path = validator.get_path()
        row = validator.get_row()
        path_row = (path, row)

        return path_row

    def check_scene_exists(self, file, file_path):
        """Checks if the bands for the scene exists."""
        scene = None

        if file.endswith(definitions.GREEN_BAND_END):
            scene = self.get_scene_name(file_path, definitions.GREEN_BAND_END)
        if file.endswith(definitions.SWIR1_BAND_END):
            scene = self.get_scene_name(file_path, definitions.SWIR1_BAND_END)

        return scene

    def make_PR_directory(self, path_row):
        """Creates a directory with the path and row."""
        path_row_dir_filename = str(path_row[0]) + "_" + str(path_row[1])
        path_row_dir = os.path.join(self.output_dir, path_row_dir_filename)

        if os.path.exists(path_row_dir):
            shutil.rmtree(path_row_dir)
        os.mkdir(path_row_dir)

        return path_row_dir

    @staticmethod
    def get_scene_name(band_path, band_endwith):
        """Returns the scene name."""
        input_dir, band = os.path.split(band_path)
        split = band.split(band_endwith)
        scene = split[0]

        return str(scene)