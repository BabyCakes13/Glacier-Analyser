"""Module which handles scene metadata. Works with .MTL file."""
from util import strings


class SceneMetadata:
    """
    Class which handles the extraction of information from the metadata file found in the download directory of each
    scene. Based on working with .MTL file.
    """

    def __init__(self, metadata_path):
        """Sets up the metadata handler."""
        self.metadata = metadata_path

    def get_scene_set_attributes(self) -> dict:
        """
        Returns a dictionary with the set landsat scene attributes from the MTL file.
        :return: dict
        """
        attributes = strings.get_scene_unset_attributes()

        with open(self.metadata, "r") as file:
            for line in file:
                attributes = self.set_dictionary(attributes, line, ' = ')

        return attributes

    def get_scene_set_coordinates(self) -> dict:
        """
        Returns a dictionary with the set landsat scene coordinates from the MTL file.
        :return: dict
        """
        coordinates = strings.get_scene_unset_coordinates()

        with open(self.metadata, "r") as file:
            for line in file:
                coordinates = self.set_dictionary(coordinates, line, ' = ')

        return coordinates

    @staticmethod
    def set_dictionary(dictionary, line, splitter) -> dict:
        """
        Sets the values of the dictionary given as parameter by splitting the given line
        on the given splitter.
        :param dictionary: The dictionary to be split.
        :param line: The line containing key, value pairs.
        :param splitter: The splitter character used for splitting the lines and separate the key values.
        :return: dict
        """
        for key, value in dictionary.items():
            if key in line:
                (set_key, set_val) = line.rstrip().split(splitter)
                dictionary[key] = set_val

        return dictionary


class SceneMetadataError(Exception):
    """
    Class which raises an exception when there is no metadata file found.
    """
    def __init__(self, message):
        """
        Initializes a message to return when the exception is raised.
        :param message: The error message when the file is not found
        """
        self.message = message

    def __str__(self) -> repr:
        """
        Returns the repr string containing the error message..
        :return: repr
        """
        return repr(self.message)
