import csv
import definitions
import os
import itertools


class CSVHandler:

    def __init__(self, start_row=0, end_row=definitions.MAX_ROW):

        self.glacier_csv = os.path.join(definitions.FILES_DIR, definitions.GLACIER_COORDINATES_FILENAME + '.csv')
        endwith = '_' + str(start_row) + '_' + str(end_row) + '.txt'
        self.glacier_txt = os.path.join(definitions.FILES_DIR,
                                        definitions.GLACIER_COORDINATES_FILENAME + endwith)

        self.start_row = start_row
        self.end_row = end_row

        self.txt_file = open(self.glacier_txt, "w")

    def open_csv(self):

        with open(self.glacier_csv, 'r', newline='', encoding='ISO-8859-1') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            self.parse_rows(csv_reader)

    # TODO remove \n from end of file.
    # TODO make parser skip reading redundant rows til it gets to start_row
    def parse_rows(self, csv_reader):
        """Method which parses the csv rows and writes the coordinates to the text file."""
        # first row is the row name

        for row in csv_reader: # csv_without_first_row:
            coordinates = ( row['lat'], row['lon'] )
            self.txt_file.write(str(coordinates) + '\n')

        self.txt_file.close()
