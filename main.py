"""Main caller of the application."""
from data_gathering import configuration, scene_metadata

# setup the configuration file
CONFIG = configuration.SetupConfig()
PARSER = configuration.ReadConfig()

# setup Input Bands
# io = IO.InputBands()
# io.get_attributes()

# metadata buggin'
METAL = scene_metadata.SceneMetadata()
print(METAL.get_scene_set_attributes())
print(METAL.get_scene_set_coordinates())
