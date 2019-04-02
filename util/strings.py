import os
from pathlib import Path
CONFIG_FILENAME = "config.ini"


def get_io_paths():
    """Returns the paths dictionary for the configuration file."""
    paths = {
        'input_path': 'D:\Programming\Facultate\Licenta\Input',
        'output_path': 'D:\Programming\Facultate\Licenta\Input\Output'
    }

    return paths


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_config_path() -> Path:
    """Returns the path to the configuration file."""
    return Path(os.path.join(get_project_root(), CONFIG_FILENAME))


