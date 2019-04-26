import configparser
import os
from pathlib import Path
from util import strings
import definitions


class SetupConfig:
    """Class which sets up the configuration file."""

    def __init__(self):
        """Initialises the parser for the configuration file."""
        self.parser = configparser.ConfigParser()
        self.validate_config()

    def set_config(self):
        """Sets up the config.ini file."""
        self.parser['PATHS'] = strings.get_default_io_paths()
        self.parser['BANDS'] = strings.get_default_bands()
        self.parser['SPECIFICATIONS'] = strings.get_default_period()

        with open(definitions.CONFIG_PATH, 'w') as file:
            self.parser.write(file)

    def validate_config(self):
        """Checks if the configuration file is valid."""
        if os.path.isfile(definitions.CONFIG_PATH) is False:
            self.set_config()


class ReadConfig:
    """Class used for reading data from the configuration file."""

    def __init__(self):
        """Initialises the parser for the configuration file."""
        self.parser = configparser.ConfigParser()
        self.parser.read(definitions.CONFIG_PATH)

    def get_paths_dict(self) -> dict:
        """Returns the PATHS dictionary from configuration file."""
        return dict((self.parser.items('PATHS')))

    def get_bands_dict(self) -> dict:
        """Returns the BANDS dictionary from configuration file."""
        return dict((self.parser.items('BANDS')))

    def get_attributes_dict(self) -> dict:
        """Returns the ATTRIBUTES dictionary from configuration file."""
        return dict((self.parser.items('ATTRIBUTES')))

    def get_input_path(self) -> Path:
        """Returns the path to the input directory."""
        return Path(self.get_paths_dict().get('INPUT_DIR'))

    def get_output_path(self) -> Path:
        """Returns the path to the output directory."""
        return Path(self.get_paths_dict().get('OUTPUT_DIR'))

    def get_yes_bands(self) -> list:
        """Returns a list with the selected bands for usage
        (the ones opted with YES in the config.ini file)."""
        yes_bands = []
        for band, band_option in self.get_bands_dict().items():
            if band_option == 'YES':
                yes_bands.append(band)

        return yes_bands


class ValidateConfig:
    pass
    # TODO validate the data from the configuration file.


