"""Module which holds definitions."""
import os
import datetime

# paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(ROOT_DIR, 'util')
DEFAULT_INPUT_DIR = os.path.join(ROOT_DIR, 'input')
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')
FILES_DIR = os.path.join(UTIL_DIR, 'files')


# bands
GREEN_BAND_END = '_B3.TIF'
SWIR1_BAND_END = '_B6.TIF'
METADATA_END = "_MTL.txt"


# NDSI
THRESHOLD = 6000
OUT_TIFF_UINT8 = str(THRESHOLD) + "_NDSI_INT8.tif"
OUT_TIFF_UINT16 = str(THRESHOLD) + "_NDSI_INT16.tif"
OUT_TIFF_FLOAT32 = str(THRESHOLD) + "_NDSI_FLOAT32.tif"

# download
DEFAULT_START_DATE = '1990-01-01'
DEFAULT_END_DATE = datetime.datetime.now().strftime('%Y-%m-%d')
DEFAULT_CLOUD_COVERAGE = "5"
# TODO find the number of rows in the csv file for accurate MAX_ROW possible number.
MAX_ROW = 150000
BBOX_SIZE = 0.0000001

# files
GLACIER_COORDINATES_FILENAME = 'wgi_feb2012'
JSON_QUERY = 'query.json'

