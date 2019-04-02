import configparser
from pathlib import Path
from util import strings


class SetupConfig:
    """Class which sets up the configuration file."""

    def __init__(self):
        """Initialises the parser for the configuration file."""
        self.parser = configparser.ConfigParser()
        self.validate_config()

    def set_config(self):
        """Sets up the config.ini file."""
        self.parser['PATHS'] = strings.get_io_paths()

        with open(strings.get_config_path(), 'w') as file:
            self.parser.write(file)

    def validate_config(self):
        """Checks if the configuration file is valid."""
        if strings.get_config_path().exists() is False:
            self.set_config()


class ReadConfig:
    """Class used for reading and getting data from the configuration file using a parser."""

    def __init__(self):
        """Initialises the parser for the configuration file."""
        self.parser = configparser.ConfigParser()
        self.parser.read(strings.get_config_path())

    def get_io_dict(self) -> dict:
        """Returns the PATHS dictionary from configuration file."""
        return dict((self.parser.items('PATHS')))

    def get_input_path(self) -> Path:
        """Returns the path to the input directory."""
        return Path(self.get_io_dict().get('input_path'))

    def get_output_path(self) -> Path:
        """Returns the path to the output directory."""
        return Path(self.get_io_dict().get('output_path'))


class ValidateConfig:
    pass
    # TODO validate the data from the configuration file.


