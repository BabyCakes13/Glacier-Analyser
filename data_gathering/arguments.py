"""Argument parser"""
import argparse
from data_gathering import download
from data_processing import process
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
        download_parser.add_argument('--dir',
                                     help='Path to the output folder which will contain the data set results.',
                                     default=definitions.FILES_DIR,
                                     type=str,
                                     dest='dir')
        download_parser.add_argument('-j',
                                     help='Number of threads which will search and download.',
                                     default=definitions.MAX_PROCESSES,
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
        process_parser.add_argument('--threshold',
                                    help='Threshold of the NDSI calculator.',
                                    default=definitions.THRESHOLD,
                                    type=int,
                                    dest='threshold')
        process_parser.add_argument('--scene',
                                    help='Scene for processing. If set, will process only this scene,',
                                    default=definitions.DEFAULT_SCENE_NAME,
                                    type=str,
                                    dest='scene')
        process_parser.add_argument('--bigdir',
                                    help='Directory which contains all the glacier directories.',
                                    default=None,
                                    type=str,
                                    dest='bigdir')
        process_parser.add_argument('-j',
                                    help='Number of processes which will handle the processing.',
                                    default=definitions.MAX_PROCESSES,
                                    type=int,
                                    dest='j')
        process_parser.set_defaults(func=set_process_function)


def activate_arguments():
    """Instantiates an argument parser object and activates parsing."""
    arguments = ArgsParser()
    args = arguments.parser.parse_args()
    args.func(args)


def set_download_function(args):
    """The default function for download sub parser."""
    print("Setting up download...", args.csv)

    downloader = download.Downloader(args.csv, args.dir, args.j)
    downloader.start()

    print("Finished download.")


def set_process_function(args):
    """The default function for process sub parser."""
    print("Setting up process...")

    process_align = process.Process(args.input, args.bigdir, args.output, args.j)
    process_align.start()

    print("Finished process.")
