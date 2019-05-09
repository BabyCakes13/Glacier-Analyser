"""Argument parser"""
import argparse
from data_gathering import download
import definitions


class ArgsParser:
    """Class which handles the argument parser for the command line."""

    def __init__(self):
        """Sets up the argument parser."""
        self.parser = argparse.ArgumentParser(add_help=True)
        self.subparsers = self.parser.add_subparsers()

        self.add_download_arguments()
        self.add_process_arguments()

    def add_download_arguments(self):
        """Adds arguments to the download sub parser."""
        download_parser = self.subparsers.add_parser('download',
                                                     add_help=True)
        download_parser.add_argument('--csv',
                                     help='Path to the csv file.',
                                     default=definitions.GLACIER_DATASET_PATH,
                                     type=str,
                                     dest='csv')
        download_parser.add_argument('--output',
                                     help='Path to the output folder which will contain the data set results.',
                                     default=definitions.FILES_DIR,
                                     type=str,
                                     dest='output')
        download_parser.add_argument('-j',
                                     help='Number of threads which will search and download.',
                                     default=definitions.MAX_THREADS,
                                     type=int,
                                     dest='j')
        download_parser.set_defaults(func=set_download_function)

    def add_process_arguments(self):
        """Adds arguments to the process sub parser."""
        process_parser = self.subparsers.add_parser('process',
                                                    add_help=True)
        process_parser.add_argument('--input',
                                    help='Path to the input folder which contains the data set of TIF images.',
                                    default=definitions.DEFAULT_INPUT_DIR,
                                    type=str,
                                    dest='input')
        process_parser.add_argument('--output',
                                    help='Path to the output folder which will contain the data set of TIF images.',
                                    default=definitions.DEFAULT_OUTPUT_DIR,
                                    type=str,
                                    dest='output')
        process_parser.set_defaults(func=set_process_function)


def activate_arguments():
    """Instantiates an argument parser object and activates parsing."""
    arguments = ArgsParser()
    args = arguments.parser.parse_args()
    args.func(args)


def set_download_function(args):
    """The default function for download sub parser."""
    downloader = download.Downloader(args.csv, args.output, args.j)
    downloader.start()


def set_process_function(args):
    """The default function for process sub parser."""
    print("PATIENCE, will be done!")
    print("Arguments: " + args.input + args.output)
