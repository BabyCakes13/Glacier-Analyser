"""Module which holds definitions."""
from colors import *
import os
import datetime

# directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(ROOT_DIR, 'util')
FILES_DIR = os.path.join(UTIL_DIR, 'files')
DEFAULT_INPUT_DIR = os.path.join(FILES_DIR, 'input')
DEFAULT_OUTPUT_DIR = os.path.join(FILES_DIR, 'output')
DEFAULT_DOWNLOAD_DIR = os.path.join(FILES_DIR, 'download')

# files
GLACIER_DATASET_FILENAME = 'wgi_feb2012'
GLACIER_DATASET_PATH = os.path.join(FILES_DIR, GLACIER_DATASET_FILENAME + '.csv')
JSON_QUERY = 'query.json'
DEFAULT_SCENE_NAME = None
DEFAULT_BIG_DIR = None

# bands
GREEN_BAND_END = '_B3.TIF'
SWIR1_BAND_END = '_B6.TIF'
METADATA_END = "_MTL.txt"
BAND_OPTIONS = (GREEN_BAND_END, SWIR1_BAND_END)

# ndsi
THRESHOLD = 12000
OUT_TIFF_UINT8 = str(THRESHOLD) + "_NDSI_INT8.tif"
OUT_TIFF_UINT16 = str(THRESHOLD) + "_NDSI_INT16.tif"
OUT_TIFF_FLOAT32 = str(THRESHOLD) + "_NDSI_FLOAT32.tif"


# align
MAX_FEATURES = 1500
GOOD_MATCH_PERCENT = 0.10
ALLOWED_ERROR = 0.05
ALLOWED_INTEGRAL = 100

# download
DEFAULT_START_DATE = '1990-01-01'
DEFAULT_END_DATE = datetime.datetime.now().strftime('%Y-%m-%d')

# download parameters
DEFAULT_CLOUD_COVERAGE = "5"
BBOX_SIZE = 0.000001

# processing
MAX_PROCESSES = 4
RETURN_CODES = {
    0: (green("SUCCESS. ")),
    1: (red("FAILURE. ")),
    2: (yellow("INTERRUPTED. ")),
    4: (red("OTHER ERROR. "))
}

# print codes
PRINT_CODES = [
    yellow("[INFO] "),
    red("[ERROR] "),
    blue("[DONE] ")
]
