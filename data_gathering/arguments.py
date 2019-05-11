"""Argument parser"""
import argparse
import gdal
import os
from data_gathering import download
from data_processing import ndsi_calculator
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
        process_parser.add_argument('--threshold',
                                    help='Threshold of the NDSI calculator.',
                                    default=definitions.THRESHOLD,
                                    type=int,
                                    dest='threshold')
        process_parser.set_defaults(func=set_process_function)


def activate_arguments():
    """Instantiates an argument parser object and activates parsing."""
    arguments = ArgsParser()
    args = arguments.parser.parse_args()
    args.func(args)


def set_download_function(args):
    """The default function for download sub parser."""
    downloader = download.Downloader(args.csv, args.dir, args.j)
    downloader.start()


def set_process_function(args):
    """The default function for process sub parser."""
    print("Setting up process...", args.input)

    green_bands_paths, green_bands_number = get_ndsi_bands_paths(args.input, definitions.GREEN_BAND_END)
    swir1_bands_paths, swir1_bands_number = get_ndsi_bands_paths(args.input, definitions.SWIR1_BAND_END)

    if green_bands_number == swir1_bands_number:
        for counter in range(0, green_bands_number):
            green_scene = get_scene_name(green_bands_paths[counter], definitions.GREEN_BAND_END)
            swir1_scene = get_scene_name(swir1_bands_paths[counter], definitions.SWIR1_BAND_END)

            if check_pairs(green_scene, swir1_scene):
                ndsi = ndsi_calculator.NDSI(green_path=green_bands_paths[counter],
                                            swir1_path=swir1_bands_paths[counter],
                                            output_dir=args.output,
                                            threshold=args.threshold)
                output_filename = green_scene + "_" + str(args.threshold) + "_NDSI_INT8.tif"
                ndsi.create_NDSI(output_filename, gdal.GDT_Byte)
    else:
        print("Some bands are missing.")


def get_scene_name(band_path, band_endwith):
    """Returns the scene name."""
    input_dir, band = os.path.split(band_path)
    split = band.split(band_endwith[0])
    scene = split[0]

    return str(scene)


def check_pairs(green, swir1):
    """Checks if the scene names of the two bands are the same."""
    if green == swir1:
        return True
    return False


def count_bands(input_dir, band_option):
    """Counts the number of bands from the input directory which end with the specified option."""
    count = 0
    for file in os.listdir(input_dir):
        if file.endswith(band_option):
            count += 1

    return count


def get_ndsi_bands_paths(input_dir, band_option) -> list:
    """Returns the path to the opted bands."""
    band_paths = []
    count = 0

    for file in os.listdir(input_dir):
        if file.endswith(band_option):
            band_paths.append(os.path.join(input_dir, str(file)))
            count += 1

    return sorted(band_paths), count
