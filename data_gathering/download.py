import csv
import os
import shutil
import subprocess
import signal

from colors import *

import sys
sys.path.append(sys.path[0] + '/..')

import definitions
from data_processing import multiprocess as mh

def interrupt_handler(signum, frame):
    print ("exiting now")
    raise KeyboardInterrupt

class Downloader:
    """
    Class which handles bulk searching and downloading of Landsat 8 scenes, multiprocessed.
    """

    def __init__(self, input_csv_path=definitions.GLACIER_DATASET_PATH,
                 download_dir=definitions.DEFAULT_DOWNLOAD_DIR,
                 max_processes=definitions.MAX_PROCESSES):
        """
        Initializes the variables needed for download processing.
        :param input_csv_path: The csv which contains information about the glaciers to be downloaded.
        :param download_dir: The path to the download directory in which the downloaded paths will be stored.
        :param max_processes: The number of maximum processes which can be turned on for the multiprocessing.
        """
        self.glacier_csv_path = input_csv_path
        self.download_dir = download_dir
        self.max_processes = max_processes
        self.search_process = None

        self.mh = mh.Multiprocess(max_processes=self.max_processes,
                                  handler=self.process_handler)

        print(blue("Download csv file: ") + str(input_csv_path))

    def start(self) -> None:
        """
        Method which reads the glacier csv files and parses its rows in order to begin the processing of each one.
        :return: None
        """
        """Opens the csv file and starts the searching and downloading process."""
        with open(self.glacier_csv_path, 'r', newline='', encoding='ISO-8859-1') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            self.parse_rows(csv_reader)

    @staticmethod
    def create_search_arglist(row, json_query_filename) -> list:
        """
        Method which creates the search task from the command line which will be transferred to the multiprocessing
        handler. It calculates the bounding box of coordinates.
        :param row: The current row which is being processed from the csv.
        :param json_query_filename: The name of the json query filename which will contain the results of the search.
        :return: list
        """
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
    def create_download_arglist(json_query_filename, download_dir) -> list:
        """
        Method which creates the download task from the command line which will be transferred to the multiprocessing
        handler. It specifies that only the green band, swir1 band, MTL file and the thumbnail should be downloaded.
        :param json_query_filename: The name fo the json query resulted from searching.
        :param download_dir: The directory in which the files will be downloaded.
        :return: list
        """
        download_arglist = ["sat-search", "load", json_query_filename,
                            "--download", "B3", "B6", "MTL", "thumbnail",
                            "--datadir", download_dir]

        return download_arglist

    @staticmethod
    def process_handler(task_name, return_code) -> None:
        """
        The handler function which gets the return code from the subprocess and handles the result by outputting the
        message.
        :param task_name: The name of the task which finished.
        :param return_code: The return code of the process which finished.
        :return: None
        """
        return_codes = definitions.RETURN_CODES
        try:
            return_str = return_codes[return_code]
        except KeyError:
            return_str = "IDK"

        print("Return code of ", task_name, " is ", return_code, " meaning ", return_str)

    def parse_rows(self, csv_reader) -> None:
        """
        Method which parses the rows representing glaciers and their information from the glacier csv file. It handles
        dictionary creation as: for each glacier, create an directory which has the glacier name and its coordinates in
        the name.
        :param csv_reader: The csv handler.
        :return: None
        """
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

            def preexec_function():
                signal.signal(signal.SIGINT, signal.SIG_IGN)

            try:
                search_task = self.create_search_arglist(row, json_query_filename)
                print(yellow(search_task))
                # sync, will wait to finish
                self.search_process = subprocess.Popen(search_task, preexec_fn=preexec_function)
                self.search_process.wait()

                # async, will not wait to finish
                download_task = self.create_download_arglist(json_query_filename, directory_name)
                print(blue(download_task))

                self.mh.start_processing(task=download_task, task_name=json_query_filename, ignore_SIGINT=True)

            except KeyboardInterrupt:
                print("exiting ... 4")
                self.search_process.wait()
                print("exiting ... 3")
                self.mh.kill_all_processes(signal.SIGTERM)
                print("exiting ... 2")
                self.mh.wait_all_process_done()
                print("exiting ... 1")
                break

if __name__ == "__main__":
    """
    Handle called from GUI.
    """

    csv_path = sys.argv[1]
    download_dir = sys.argv[2]
    max_processes=int(sys.argv[3])

    signal.signal(signal.SIGINT, interrupt_handler)

    downloader = Downloader(csv_path, download_dir, max_processes)
    downloader.start()

    print("exited")
