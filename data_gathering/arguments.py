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
                                 help='Path to the input folder which contains the data set.',
                                 default=definitions.DEFAULT_INPUT_DIR,
                                 type=str,
                                 nargs=1,
                                 dest='input')
        self.parser.add_argument('--output',
                                 help='Path to the output folder which will contain the results.',
                                 default=definitions.DEFAULT_OUTPUT_DIR,
                                 type=str,
                                 nargs=1,
                                 dest='output')
        self.parser.add_argument('--start',
                                 help='Start date for image gathering.',
                                 default=definitions.DEFAULT_START_DATE,
                                 type=str,
                                 nargs=1,
                                 dest='start'
                                 )
        self.parser.add_argument('--end',
                                 help='End date for image gathering.',
                                 default=definitions.DEFAULT_END_DATE,
                                 type=str,
                                 nargs=1,
                                 dest='end'
                                 )
        self.parser.add_argument('--path',
                                 help='Path for image gathering.',
                                 default=definitions.DEFAULT_PATH,
                                 type=str,
                                 nargs=1,
                                 dest='path'
                                 )
        self.parser.add_argument('--row',
                                 help='Row for image gathering.',
                                 default=definitions.DEFAULT_ROW,
                                 type=str,
                                 nargs=1,
                                 dest='row'
                                 )
        self.parser.add_argument('--cloud',
                                 help='Maximum cloud coverage for image gathering.',
                                 default=definitions.DEFAULT_CLOUD_COVERAGE,
                                 type=str,
                                 nargs=1,
                                 dest='cloud'
                                 )
        self.parser.add_argument('--download',
                                 help='Specify whether to download images or not.',
                                 action='store_true',
                                 dest='download')

    def get_input(self):
        """Returns the path to the input folder which contains the data set."""
        return self.args.input

    def get_output(self):
        """Returns the path to the output folder which will contain the results."""
        return self.args.output

    def get_start(self):
        """Returns the start date of image gathering."""
        return self.args.start

    def get_end(self):
        """Returns the end date of image gathering."""
        return self.args.end

    def get_path(self):
        """RReturns the WRS2 path."""
        return self.args.path

    def get_row(self):
        """Returns the WRS2 row."""
        return self.args.row

    def get_cloud(self):
        """Returns the maximum cloud cloud coverage."""
        return self.args.cloud

    def get_download(self):
        """Returns True if the argument download was provided."""
        return self.args.download
