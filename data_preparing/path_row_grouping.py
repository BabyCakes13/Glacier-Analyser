import os
import definitions
from data_gathering import scene_data


class PRGroup:
    def __init__(self, directory):
        self.directory = directory

    def determine_total_PR(self):
        """Determine the total paths and rows of the directory."""
        total_PR = []

        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.TIF'):
                    file_path = os.path.join(root, file)
                    path_row = self.determine_PR(file, file_path)

                    if path_row not in total_PR and path_row is not None:
                        total_PR.append(path_row)

        print(total_PR)

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

    @staticmethod
    def get_scene_name(band_path, band_endwith):
        """Returns the scene name."""
        input_dir, band = os.path.split(band_path)
        split = band.split(band_endwith)
        scene = split[0]

        return str(scene)