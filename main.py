#! /usr/bin/python3

"""Main caller of the application."""
from data_gathering import args
from data_processing import ndvi_calculator

arg = args.ArgsParser()

ndvi = ndvi_calculator.NDSI(arg.get_input(), arg.get_output())
