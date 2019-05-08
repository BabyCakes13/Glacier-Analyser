import csv
import definitions
import os
import itertools


class CSVHandler:

    def __init__(self, start_row=-0, end_row=definitions.MAX_ROW):

        self.glacier_csv = os.path.join(definitions.FILES_DIR, definitions.GLACIER_COORDINATES_FILENAME + '.csv')
        endwith = '_' + str(start_row) + '_' + str(end_row) + '.txt'
        self.glacier_txt = os.path.join(definitions.FILES_DIR,
                                        definitions.GLACIER_COORDINATES_FILENAME + endwith)

        self.start_row = start_row
        self.end_row = end_row

        self.txt_file = open(self.glacier_txt, "w")

    def open_csv(self):

        with open(self.glacier_csv, 'r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.parse_rows(csv_reader)

    # TODO remove \n from end of file.
    # TODO make parser skip reading redundant rows til it gets to start_row
    def parse_rows(self, csv_reader):
        """Method which parses the csv rows and writes the coordinates to the text file."""
        # first row is the row name
        csv_without_first_row = itertools.islice(enumerate(csv_reader), 1, None)

        for current_row, row in csv_without_first_row:
            if current_row == self.end_row:
                break
            if self.start_row <= current_row <= self.end_row:
                coordinates = extract_coordinates(row)
                self.txt_file.write(str(coordinates) + '\n')

        self.txt_file.close()


def extract_coordinates(row) -> tuple:
    """Method which extracts the coordinates from the given csv row."""
    coordinates = (row[definitions.CSV_LATITUDE_POSITION],
                   row[definitions.CSV_LONGITUDE_POSITION])

    return coordinates

