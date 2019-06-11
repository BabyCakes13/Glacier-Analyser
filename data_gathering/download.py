import csv
from colors import *
import json
import os
import shutil
import time
import subprocess
import definitions
from data_preparing import multithread_handler


class Downloader:
    """Class which handles searching and downloading landsat files."""

    def __init__(self, input_csv=definitions.GLACIER_DATASET_PATH,
                 download_dir=definitions.DEFAULT_DOWNLOAD_DIR,
                 max_threads=definitions.MAX_THREADS,
                 months=definitions.VALID_MONTHS):
        """Initialises variables needed for the processes."""
        self.glacier_csv = input_csv
        self.download_dir = download_dir
        self.months = months
        self.max_threads = max_threads
        self.process_queue = []

        self.INTERRUPT_SIGNAL = False

        print("Input: " + str(input_csv))

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

    def check_months(self, json_query_path, scene_number):
        """Checks if the month of the scene from the query is valid with the opted month list."""
        print("JSON: ", json_query_path)

        with open(json_query_path, "r") as json_query:
            data = json.load(json_query)

        datetime = data["features"][scene_number]['properties']["datetime"]
        month = int(datetime[5:7])

        if month in self.months:
            return True
        return False

    @staticmethod
    def create_download_arglist(json_query_filename, dirname):
        """Creates the sat-load argument list."""
        download_arglist = ["sat-search", "load", json_query_filename,
                            "--download", "B3", "B6", "MTL", "thumbnail",
                            "--datadir", dirname]

        return download_arglist

    def parse_rows(self, csv_reader):
        """Parses and processes each row in the CSV file."""
        process_queue_download = []
        for row in csv_reader:

            directory_id = row['wgi_glacier_id'] + "_" + row['lon'] + "_" + row['lat']
            directory_name = os.path.join(self.download_dir, directory_id)
            json_query_filename = os.path.join(directory_name, definitions.JSON_QUERY)

            start_multithreaded_process_download = None
            try:
                if os.path.exists(directory_name):
                    shutil.rmtree(directory_name)
                os.mkdir(directory_name)
            except FileNotFoundError:
                print("Cannot create download directory. The path has a directory which does not exist.")

            try:
                search_task = self.create_search_arglist(row, json_query_filename)
                print(blue(search_task))

                search = subprocess.call(search_task)

                download_task = self.create_download_arglist(json_query_filename, directory_name)
                print(yellow(download_task))
                start_multithreaded_process_download = \
                    multithread_handler.Multithread(task=download_task,
                                                    target_file=json_query_filename,
                                                    process_queue=process_queue_download,
                                                    max_threads=self.max_threads)
                process_queue_download = start_multithreaded_process_download.start_processing()

            except KeyboardInterrupt:
                print("Keyboard interrupt.")
                self.INTERRUPT_SIGNAL = True
                start_multithreaded_process_download.wait_all_process_done()
                break

