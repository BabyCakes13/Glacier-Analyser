import os
import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
CONFIG_FILENAME = "config.ini"


def get_default_io_paths() -> dict:
    """Returns the paths dictionary for the configuration file."""
    paths = {
        'input_path': 'D:\Programming\Facultate\Licenta\Input',
        'output_path': 'D:\Programming\Facultate\Licenta\Input\Output'
    }

    return paths


def get_default_specifications() -> dict:
    """Return the default date for the configuration file."""
    today = datetime.datetime.now()
    past = today - relativedelta(years=100)

    today = today.strftime('%Y-%m-%d')
    past = past.strftime('%Y-%m-%d')

    specifications = {
        'from': today,
        'to': past
    }

    return specifications


def get_default_bands() -> dict:
    """Returns the band options directory for the configuration file."""
    paths = {
        '1': 'YES',
        '2': 'YES',
        '3': 'YES',
        '4': 'YES',
        '5': 'YES',
        '6': 'YES',
        '7': 'YES',
        '8': 'YES',
        '9': 'YES',
        '10': 'YES',
        '11': 'YES',
        'QA': 'YES',
    }

    return paths


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_config_path() -> Path:
    """Returns the path to the configuration file."""
    return Path(os.path.join(get_project_root(), CONFIG_FILENAME))


def default_endwith(number):
    """Returns the default Landsat band name termination with the correct band number,
    opted for in the configuration file."""
    return "_B" + number.upper() + ".TIF"


