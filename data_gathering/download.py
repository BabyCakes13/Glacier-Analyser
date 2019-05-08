import csv
import definitions
import os
import itertools
import subprocess

class CSVHandler:

    def __init__(self, input_csv, output_dir, start_row=0, end_row=definitions.MAX_ROW):

        self.glacier_csv = input_csv
        self.output_dir = output_dir

        self.start_row = start_row
        self.end_row = end_row

        self.max_threads = 10

        print ( "Input: " + str(input_csv) + " from : ", start_row, " to: ", end_row)

    def open_csv(self):
        with open(self.glacier_csv, 'r', newline='', encoding='ISO-8859-1') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            self.parse_rows(csv_reader)

    def parse_rows(self, csv_reader):
        """Method which parses the csv rows and writes the coordinates to the text file."""
        # first row is the row name

        pQuery = []

        for row in csv_reader: # csv_without_first_row:
            coordinates = ( row['lon'], row['lat'] )

            bbox_size = 0.0000001

            id = row['wgi_glacier_id'] # + "_" + row['lon'] + "_" + row['lat']

            dirname = os.path.join(self.output_dir, id)
            json_query_filename = os.path.join(dirname, "query.json")
            os.mkdir(dirname)

            queryArglist = ["sat-search", "search", "--bbox",
                            str(float(row['lon']) - bbox_size),
                            str(float(row['lat']) - bbox_size),
                            str(float(row['lon']) + bbox_size),
                            str(float(row['lat']) + bbox_size),
                            "--save", json_query_filename]

            downloadArglist = ["sat-search", "load", json_query_filename,
                            "--download", "B3", "B6",
                            "--datadir", dirname]

            if len(pQuery) >= self.max_threads:
                filename, sp = pQuery.pop()
                sp.wait()
                print("Query done: ", filename)

            print( queryArglist )
            sp = subprocess.call( queryArglist )

            print( downloadArglist )
            sp = subprocess.Popen( downloadArglist )
            pQuery.append((json_query_filename, sp))

            for filename, sp in pQuery:
                if sp.poll() == 0:
                    pQuery.remove((filename, sp))
                    print("Query done: ", filename)

        self.txt_file.close()
