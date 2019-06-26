"""Module which handles the argument parsing for the application."""
import argparse

import definitions
from data_displaying import csv_reader
from data_displaying import gui
from data_gathering import download
from data_processing import process


class ArgsParser:
    """
    Class which handles argument parsing for the command line interface.
    """

    def __init__(self):
        """
        Sets up the argument parser for the command line interface, creating subparsers for process, download and
        display.
        """
        self.parser = argparse.ArgumentParser(add_help=True)
        self.subparsers = self.parser.add_subparsers()

        self.add_download_arguments()
        self.add_process_arguments()
        self.add_display_arguments()

    def add_download_arguments(self) -> None:
        """
        Adds arguments to the download sub parser.
        :return: None
        """
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

    def add_process_arguments(self) -> None:
        """
        Adds arguments to the process sub parser.
        :return: None
        """
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

    def add_display_arguments(self) -> None:
        """
        Adds display arguments to the parser.
        :return: None
        """
        process_parser = self.subparsers.add_parser('display',
                                                    add_help=True)
        process_parser.add_argument('--csv',
                                    help='Path to the csv containing path row data for one glacier.',
                                    default=None,
                                    type=str,
                                    dest='csv')
        process_parser.set_defaults(func=set_display_function)


def activate_arguments() -> None:
    """
    Instantiates an argument parser object and activates parsing.
    :return: None
    """
    arguments = ArgsParser()
    args = arguments.parser.parse_args()

    # start gui mode
    if check_no_arguments_passed(args):
        gui.start()
        return

    # start cmd mode
    args.func(args)


def check_no_arguments_passed(args) -> bool:
    """
    Checks if no arguments have been passed to the application.
    :param args: Arguments form the command line.
    :return: True if there were to arguments found, aka all have values of none, False if at least one has a value which
    is not None. Used for determining whether to start the application in GUI mode or not.
    """
    for arg in vars(args):
        if getattr(args, arg) is not None:
            return False
    return True


def set_download_function(args) -> None:
    """
    The default function for download sub parser.
    :param args:
    :return:
    """
    print("Setting up download...", args.csv)

    downloader = download.Downloader(args.csv, args.dir, args.j)
    downloader.start()

    print("Finished download.")


def set_process_function(args) -> None:
    """
    The default function for process sub parser.
    :param args: Arguments taken from the command line.
    :return: None
    """
    print("Setting up process...")

    process_align = process.Process(args.input, args.bigdir, args.output, args.j)
    process_align.start()

    print("Finished process.")


def set_display_function(args) -> None:
    """
       The default function for display sub parser.
       :param args: Arguments taken from the command line.
       :return: None
       """
    print("Setting up display...")

    process_align = csv_reader.CSVReader(csv=args.csv)
    process_align.start()

    print("Finished display.")
