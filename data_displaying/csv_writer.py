import csv
import os

import definitions
from util import strings

ALIGN_CSV = 'align'
NDSI_CSV = 'ndsi'


class CSVWriter:
    def __init__(self, output, arguments, path=None, row=None):
        """
        Writes or appends to a csv based on the option (either align or process ndsi.
        :param arguments: arguments of alignment or ndsi
        """
        # if path and row are specified that means that the csv is done for the ndsi calculation, not alignment; align
        # research is done independent of the path, taking a ratio out of all images from a glacier.
        if path and row:
            self.csv_name = NDSI_CSV + "_" + path + "_" + row + ".csv"
        else:
            self.csv_name = ALIGN_CSV

        self.csv_path = os.path.join(output, self.csv_name)
        self.arguments = arguments

    def start(self) -> None:
        """
        Starts creating and writing to the csv.
        :return: None
        """
        self.create()
        self.add_item()

    def create(self) -> None:
        """Verifies if the first column, which represents the names of the columns, exist. If it doesn't, that means
               the csv file is not created yet. Create it if it doesn't exist, append if it does."""
        if os.path.isfile(self.csv_path):
            print("Is file.")
            return
        else:
            print(definitions.PRINT_CODES[0] + "Creating csv...")
            with open(self.csv_path, "w") as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # align
                if ALIGN_CSV in self.csv_name:
                    writer.writerow(self.get_default_align_csv())
                # ndsi
                elif NDSI_CSV in self.csv_name:
                    writer.writerow(self.get_default_ndsi_csv())
                else:
                    print(definitions.PRINT_CODES[1] + "There option is not valid. Not writing.")
                    return

                file.flush()

    def add_item(self) -> None:
        """
        Adds the argument to the csv file.
        :return: None
        """
        result = self.arguments

        print(result)

        with open(self.csv_path, "a") as file:
            writer = csv.writer(file)
            writer.writerow(result)

    @staticmethod
    def get_default_align_csv():
        attributes = ['GLACIER_ID',
                      'PATH',
                      'ROW',
                      'TOTAL PROCESSED',
                      'VALID ALIGNED',
                      'RATIO']
        return attributes

    @staticmethod
    def get_default_ndsi_csv():
        attributes = [
            'GLACIER_ID',
            'SCENE',
            'YEAR',
            'MONTH',
            'DAY',
            'PATH',
            'ROW',
            'SNOW_RATIO'
        ]
        return attributes
