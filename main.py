#! /usr/bin/python3

"""Main caller of the application."""
from data_gathering import configuration
from data_processing import ndvi_calculator


CONFIG = configuration.SetupConfig()
PARSER = configuration.ReadConfig()

NDSI = ndvi_calculator.NDSI()
