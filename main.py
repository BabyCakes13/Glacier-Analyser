"""Main caller of the application."""
from data_gathering import IO, configuration

# setup the configuration file
config = configuration.SetupConfig()

# setup Input Bands
io = IO.InputBands()
io.get_bands()
