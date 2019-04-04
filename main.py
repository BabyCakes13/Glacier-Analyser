"""Main caller of the application."""
from data_gathering import IO, configuration
from util import strings

# setup the configuration file
config = configuration.SetupConfig()
parser = configuration.ReadConfig()

print(parser.get_attributes_dict())