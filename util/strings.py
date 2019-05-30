import datetime
import definitions


def get_default_io_paths() -> dict:
    """Returns the paths dictionary for the configuration file.
    :rtype dict"""

    paths = {
        'DEFAULT_INPUT_DIR': definitions.DEFAULT_INPUT_DIR,
        'DEFAULT_OUTPUT_DIR': definitions.DEFAULT_OUTPUT_DIR
    }

    return paths


def get_default_period() -> dict:
    """Return the default date for the configuration file, calculated as today - 100 years today.
    :rtype dict"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    past = '1900-01-01'

    today = today.strftime('%Y-%m-%d')
    past = past.strftime('%Y-%m-%d')

    specifications = {
        'from': today,
        'to': past
    }

    return specifications


def get_default_bands() -> dict:
    """Returns the band options directory for the configuration file.
    :rtype dict"""
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


def default_band_endwith(number) -> str:
    """Returns the default Landsat band name termination with the correct band number,
    opted for in the configuration file.
    :rtype str"""
    return "_B" + number.upper() + ".TIF"


def get_scene_unset_attributes() -> dict:
    """Returns a dictionary containing some of the attributes of the landsat scene,
     unset, from the MTL file.
     :rtype: dict"""
    attributes = {
        'LANDSAT_SCENE_ID': '',
        'LANDSAT_PRODUCT_ID': '',
        'SPACECRAFT_ID ': '',
        'WRS_PATH': '',
        'WRS_ROW': '',
        'DATE_ACQUIRED': '',
        'SCENE_CENTER_TIME': '',
        'CLOUD_COVER': '',
        'IMAGE_QUALITY_OLI': '',
        'SUN_ELEVATION': ''
    }

    return attributes


def get_scene_unset_coordinates() -> dict:
    """Returns a dictionary which contains the corner coordinates of the landsat scene,
    unset, from the MTL file."""
    coordinates = {
        'CORNER_UL_LAT_PRODUCT': '',
        'CORNER_UL_LON_PRODUCT': '',
        'CORNER_UR_LAT_PRODUCT': '',
        'CORNER_UR_LON_PRODUCT': '',
        'CORNER_LL_LAT_PRODUCT': '',
        'CORNER_LL_LON_PRODUCT': '',
        'CORNER_LR_LAT_PRODUCT': '',
        'CORNER_LR_LON_PRODUCT': '',
    }

    return coordinates


def get_default_homography_csv():
    attributes = ['GLACIER_ID',
                  'MAX_FEATURES',
                  'GOOD_MATCH_PERCENT',
                  'ALLOWED_ERROR',
                  'ALLOWED_INTEGRAL',
                  'VALID_HOMOGRAPHIES',
                  'PROCESSED_HOMOGRAPHIES',
                  'RATIO']
    return attributes


def get_system_messages():

    messages = [
        'starting VRT creation...',
        'ended VRT creation.'
    ]

    return messages


def error_messages():

    errors = [
        'Invalid data type for output NDSI.'
    ]

    return errors
