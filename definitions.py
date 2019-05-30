"""Module which holds definitions."""
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
DEFAULT_SCENE_NAME = "UNSET"
HOMOGRAPHY_CSV = 'homography_result.csv'

# bands
GREEN_BAND_END = '_B3.TIF'
SWIR1_BAND_END = '_B6.TIF'
METADATA_END = "_MTL.txt"

# ndsi
THRESHOLD = 12000
OUT_TIFF_UINT8 = str(THRESHOLD) + "_NDSI_INT8.tif"
OUT_TIFF_UINT16 = str(THRESHOLD) + "_NDSI_INT16.tif"
OUT_TIFF_FLOAT32 = str(THRESHOLD) + "_NDSI_FLOAT32.tif"

# download
DEFAULT_START_DATE = '1990-01-01'
DEFAULT_END_DATE = datetime.datetime.now().strftime('%Y-%m-%d')

# download parameters
DEFAULT_CLOUD_COVERAGE = "5"
BBOX_SIZE = 0.0000001
MAX_THREADS = 4
MONTHS = [6, 7, 8]
