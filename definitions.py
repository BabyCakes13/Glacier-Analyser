"""Module which holds definitions."""
import os

# paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')
INPUT_DIR = os.path.join(ROOT_DIR, 'input')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')


# bands
GREEN_BAND_END = '_B3.TIF'
SWIR1_BAND_END = '_B6.TIF'
METADATA_END = "_MTL.txt"


# NDSI
THRESHOLD = 8000
OUT_TIFF_UINT8 = str(THRESHOLD) + "_NDSI_INT8.tif"
OUT_TIFF_UINT16 = str(THRESHOLD) + "_NDSI_INT16.tif"
OUT_TIFF_FLOAT32 = str(THRESHOLD) + "_NDSI_FLOAT32.tif"
