import pathlib
import os
from util import strings
from data_gathering import configuration


class SceneMetadata:
    """Class which deals with the scene MTL metadata file."""
    def __init__(self):
        """Initialises the parser for the configuration file."""
        self.parser = configuration.ReadConfig()
        self.input_path = self.parser.get_input_path()
        self.metadata_file = self.get_metadata_file()

    def get_metadata_file(self) -> pathlib.Path:
        """Returns the full path to the metadata file."""
        endwith = strings.default_metadata_endwith()

        # search for metadata file in the input directory
        metadata = False
        for file in os.listdir(str(self.input_path)):
            if file.endswith(endwith):
                metadata = file
        if not metadata:
            raise SceneMetadataError("SceneMetadata file was not found.")

        # get the full metadata file path
        metadata = self.input_path.joinpath(metadata)

        return metadata

    def get_scene_set_attributes(self) -> dict:
        """Returns a dictionary with the set landsat scene attributes from the MTL file."""
        attributes = strings.get_scene_unset_attributes()

        with open(self.metadata_file, "r") as file:
            for line in file:
                attributes = set_dictionary(attributes, line, ' = ')

        return attributes

    def get_scene_set_coordinates(self) -> dict:
        """Returns a dictionary with the set landsat scene coordinates from the MTL file."""
        coordinates = strings.get_scene_unset_coordinates()

        with open(self.metadata_file, "r") as file:
            for line in file:
                coordinates = set_dictionary(coordinates, line, ' = ')

        return coordinates


def set_dictionary(dictionary, line, splitter) -> dict:
    """Sets the values of the dictionary given as parameter by splitting the given line
    on the given splitter."""
    for key, value in dictionary.items():
        if key in line:
            (set_key, set_val) = line.rstrip().split(splitter)
            dictionary[key] = set_val

    return dictionary


class SceneMetadataError(Exception):
    """Raise for the case when the metadata file doesn't exist in the input directory."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
