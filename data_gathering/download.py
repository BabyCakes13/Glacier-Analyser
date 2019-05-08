import csv
import os
import subprocess
import definitions


class DataHandler:
    """Class which handles searching and downloading landsat files."""

    def __init__(self, input_csv, output_dir, start_row=0, end_row=definitions.MAX_ROW, max_threads=4):
        """Initialises variables needed for the processes."""
        self.glacier_csv = input_csv
        self.output_dir = output_dir

        self.start_row = start_row
        self.end_row = end_row

        self.max_threads = max_threads
        self.process_queue = []

        print ( "Input: " + str(input_csv) + " from : ", start_row, " to: ", end_row)

    def open_csv(self):
        """Opens the csv file."""
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

    def check_process_full(self):
        """Checks if the process queue is full."""
        if len(self.process_queue) >= self.max_threads:
            filename, sp = self.process_queue.pop()
            sp.wait()
            print("Query done: ", filename)

    def call_processes(self, search_arglist, download_arglist, json_query_filename):
        """Calls and appends sat-search and sat-load processes."""

        print(search_arglist)
        sp = subprocess.call(search_arglist)

        print(download_arglist)
        sp = subprocess.Popen(download_arglist)

        self.process_queue.append((json_query_filename, sp))

    def check_process_done(self):
        """Checks if a process from the process queue is done, removes if so."""
        for filename, sp in self.process_queue:
            if sp.poll() == 0:
                self.process_queue.remove((filename, sp))
                print("Query done: ", filename)

    def parse_rows(self, csv_reader):
        """Parses and processes each row in the CSV file."""
        for row in csv_reader:
            
            directory_id = row['wgi_glacier_id'] + "_" + row['lon'] + "_" + row['lat']
            directory_name = os.path.join(self.output_dir, directory_id)
            json_query_filename = os.path.join(directory_name, definitions.JSON_QUERY)

            try:
                os.mkdir(directory_name)
            except FileExistsError:
                print("Directory already exists.")

            search_arglist = self.create_search_arglist(row, json_query_filename)
            download_arglist = self.create_download_arglist(json_query_filename, directory_name)

            self.check_process_full()
            self.call_processes(search_arglist, download_arglist, json_query_filename)
            self.check_process_done()

