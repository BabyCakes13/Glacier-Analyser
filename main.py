"""Main caller of the application."""
from data_gathering import IO, configuration, scene_metadata
from data_processing import raster_setup

# setup the configuration file
CONFIG = configuration.SetupConfig()
PARSER = configuration.ReadConfig()

# setup Input Bands
io = IO.InputBands()

# metadata buggin'
# METAL = scene_metadata.SceneMetadata()
# print(METAL.get_scene_set_attributes())
# print(METAL.get_scene_set_coordinates())

BANDS = raster_setup.RasterHandler(io.get_bands_fullpath())
