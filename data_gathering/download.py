import csv
from colors import *
import os
import shutil
import subprocess
import definitions
from data_preparing import multiprocess as mh


class Downloader:
    """Class which handles searching and downloading landsat files."""

    def __init__(self, input_csv=definitions.GLACIER_DATASET_PATH,
                 download_dir=definitions.DEFAULT_DOWNLOAD_DIR,
                 max_processes=definitions.MAX_PROCESSES):
        """Initialises variables needed for the processes."""
        self.glacier_csv = input_csv
        self.download_dir = download_dir
        self.max_processes = max_processes

        self.mh = mh.Multiprocess(max_processes=self.max_processes,
                                  handler=self.process_handler)

        self.INTERRUPT_SIGNAL = False

        print(blue("Download csv file: ") + str(input_csv))

    def start(self):
        """Opens the csv file and starts the searching and downloading process."""
        with open(self.glacier_csv, 'r', newline='', encoding='ISO-8859-1') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            self.parse_rows(csv_reader)

    @staticmethod
    def create_search_arglist(row, json_query_filename):
        """Creates the sat-search argument list."""
        search_arglist = ["sat-search", "search", "--bbox",
                          str(float(row['lon']) - definitions.BBOX_SIZE),
                          str(float(row['lat']) - definitions.BBOX_SIZE),
                          str(float(row['lon']) + definitions.BBOX_SIZE),
                          str(float(row['lat']) + definitions.BBOX_SIZE),
                          "-p", "eo:cloud_cover<" + definitions.DEFAULT_CLOUD_COVERAGE,
                          "--save", json_query_filename]

        return search_arglist

    @staticmethod
    def create_download_arglist(json_query_filename, dirname):
        """Creates the sat-load argument list."""
        download_arglist = ["sat-search", "load", json_query_filename,
                            "--download", "B3", "B6", "MTL", "thumbnail",
                            "--datadir", dirname]

        return download_arglist

    @staticmethod
    def process_handler(task_name, return_code):
        return_codes = definitions.RETURN_CODES
        return_code = return_codes[return_code]
        print(return_code, " ", task_name)

    def parse_rows(self, csv_reader):
        """Parses and processes each row in the CSV file."""
        for row in csv_reader:

            directory_id = row['wgi_glacier_id'] + "_" + row['lon'] + "_" + row['lat']
            directory_name = os.path.join(self.download_dir, directory_id)
            json_query_filename = os.path.join(directory_name, definitions.JSON_QUERY)

            try:
                if os.path.exists(directory_name):
                    shutil.rmtree(directory_name)
                os.mkdir(directory_name)
            except FileNotFoundError:
                print("Cannot create download directory. The path has a directory which does not exist.")

            try:
                search_task = self.create_search_arglist(row, json_query_filename)
                print(yellow(search_task))
                # sync, will wait to finish
                search = subprocess.call(search_task)

                # async, will not wait to finish
                download_task = self.create_download_arglist(json_query_filename, directory_name)
                print(blue(download_task))

                self.mh.start_processing(task=download_task, task_name=json_query_filename)

            except KeyboardInterrupt:
                print("Keyboard interrupt.")
                self.INTERRUPT_SIGNAL = True
                self.mh.kill_all_processes()
                self.mh.wait_all_process_done()
                break


