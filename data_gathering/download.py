import csv
import definitions
import os
import itertools
import subprocess

class CSVHandler:

    def __init__(self, start_row=0, end_row=definitions.MAX_ROW):

        self.glacier_csv = os.path.join(definitions.FILES_DIR, definitions.GLACIER_COORDINATES_FILENAME + '.csv')
        endwith = '_' + str(start_row) + '_' + str(end_row) + '.txt'
        self.glacier_txt = os.path.join(definitions.FILES_DIR,
                                        definitions.GLACIER_COORDINATES_FILENAME + endwith)

        self.start_row = start_row
        self.end_row = end_row

        self.max_threads = 100

        self.txt_file = open(self.glacier_txt, "w")

    def open_csv(self):
        with open(self.glacier_csv, 'r', newline='', encoding='ISO-8859-1') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            self.parse_rows(csv_reader)

    def parse_rows(self, csv_reader):
        """Method which parses the csv rows and writes the coordinates to the text file."""
        # first row is the row name

        simultaneous_processes = []

        for row in csv_reader: # csv_without_first_row:
            coordinates = ( row['lon'], row['lat'] )
            self.txt_file.write(str(coordinates) + '\n')

            bbox_size = 0.0000001

            json_query_filename = os.path.join(definitions.FILES_DIR,
                                               "query_" + row['lon'] + "_" + row['lat'] + ".json")

            arglist = ["sat-search", "search", "--bbox",
                       str(float(row['lon']) - bbox_size),
                       str(float(row['lat']) - bbox_size),
                       str(float(row['lon']) + bbox_size),
                       str(float(row['lat']) + bbox_size),
                       "--save", json_query_filename]

            if len(simultaneous_processes) >= self.max_threads:
                simultaneous_processes.pop().wait()

            print( arglist )
            sp = subprocess.Popen( arglist )
            simultaneous_processes.append(sp)

            for sp in simultaneous_processes:
                if sp.poll() == 0:
                    simultaneous_processes.remove(sp)

        self.txt_file.close()
