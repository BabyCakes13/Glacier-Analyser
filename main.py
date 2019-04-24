#! /usr/bin/python3

"""Main caller of the application."""
from data_gathering import IO, configuration, scene_metadata
import definitions
from data_processing import ndvi_calculator
from util import strings

CONFIG = configuration.SetupConfig()
PARSER = configuration.ReadConfig()

NDSI = ndvi_calculator.NDSI()
