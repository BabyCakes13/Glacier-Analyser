#! /usr/bin/python3

"""Main caller of the application."""
from data_gathering import download
import argparse
import os
import definitions

# sub-command functions
def fDownload(args):
    if args.input:
        inputCsv = args.input
    else:
        inputCsv = os.path.join(definitions.FILES_DIR, definitions.GLACIER_COORDINATES_FILENAME + '.csv')

    if args.output:
        outputDir = args.output
    else:
        outputDir = os.path.join(definitions.FILES_DIR)

    csvhandler = download.CSVHandler(inputCsv, outputDir, args.first, args.last)
    csvhandler.open_csv()

def process(args):
    print ('((%s))' % args.z)

# create the top-level parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# create the parser for the "download" command
parser_download = subparsers.add_parser('download')
parser_download.add_argument('--input')
parser_download.add_argument('--output')
parser_download.add_argument('--first', type=int, default=0)
parser_download.add_argument('--last', type=int, default=99999999)
parser_download.set_defaults(func=fDownload)

# create the parser for the "process" command
parser_process = subparsers.add_parser('process')
parser_process.add_argument('z')
parser_process.set_defaults(func=process)

args = parser.parse_args()
args.func(args)
