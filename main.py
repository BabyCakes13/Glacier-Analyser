#! /usr/bin/python3

"""Main caller of the application."""
from data_gathering import IO, configuration, scene_metadata
from data_processing import ndvi_calculator

# setup the configuration file
CONFIG = configuration.SetupConfig()
PARSER = configuration.ReadConfig()

# Calculate the NDSI!!! Hugging works!
NDSI = ndvi_calculator.NDSI()