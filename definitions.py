"""Module which holds definitions."""
import os
import datetime

# paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')
DEFAULT_INPUT_DIR = os.path.join(ROOT_DIR, 'input')
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')


# bands
GREEN_BAND_END = '_B3.TIF'
SWIR1_BAND_END = '_B6.TIF'
METADATA_END = "_MTL.txt"


# NDSI
THRESHOLD = 8000
OUT_TIFF_UINT8 = str(THRESHOLD) + "_NDSI_INT8.tif"
OUT_TIFF_UINT16 = str(THRESHOLD) + "_NDSI_INT16.tif"
OUT_TIFF_FLOAT32 = str(THRESHOLD) + "_NDSI_FLOAT32.tif"

# download
DEFAULT_START_DATE = '1990-01-01'
DEFAULT_END_DATE = datetime.datetime.now().strftime('%Y-%m-%d')
DEFAULT_CLOUD_COVERAGE = 5
DEFAULT_PATH = 204
DEFAULT_ROW = 33
DEFAULT_LIMIT = 999
