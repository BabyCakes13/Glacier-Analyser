"""Argument parser"""
import argparse
import definitions


class ArgsParser:
    """Class which handles the argument parser for the command line."""

    def __init__(self):
        """Sets up the argument parser."""
        self.parser = argparse.ArgumentParser(description="Provides necessary input/output information.",
                                              add_help=True)
        self.add_arguments()
        self.args = self.parser.parse_args()

    def add_arguments(self):
        """Adds arguments to the parser."""

        self.parser.add_argument('--input',
                                 help='Path to the input folder which contains the data set',
                                 default=definitions.DEFAULT_INPUT_DIR,
                                 type=str,
                                 nargs=1,
                                 dest='input')
        self.parser.add_argument('--output',
                                 help='Path to the output folder which will contain the results',
                                 default=definitions.DEFAULT_OUTPUT_DIR,
                                 type=str,
                                 nargs=1,
                                 dest='output')
        self.parser.add_argument('--download',
                                 help='Period for collecting (year-month-day), DD latitude/longitude'
                                      'which will be converted to WRS-2 path/row',
                                 nargs=4,
                                 type=str,
                                 dest='download')

    def get_input(self):
        """Returns the path to the input folder which contains the data set."""
        return self.args.input

    def get_output(self):
        """Returns the path to the output folder which will contain the results."""
        return self.args.output

    def get_download(self):
        """If provided, returns a list with beginning and end date, DD latitude/longitude for download."""
        if self.args.download is not None:
            return self.args.download
