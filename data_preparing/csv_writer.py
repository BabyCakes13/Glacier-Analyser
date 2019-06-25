"""Module which handles writing NDSI process results in the NDSI csv file which will be used by ARIMA."""
import csv
import os

from filelock import FileLock

import definitions

ALIGN_CSV = 'align'
NDSI_CSV = 'ndsi'


class CSVWriter:
    """
    Class which handles NDSI results writing to the NDSI csv file. It gets an NDSI item, and writes it into the csv file
    which will be used by ARIMA in order to make the prediction on snow coverage.
    """

    def __init__(self, output_dir, arguments, path=None, row=None):
        """
        Writes or appends to a csv based on the option (either align or process ndsi).
        :param arguments: arguments of alignment or ndsi
        """
        # if path and row are specified that means that the csv is done for the ndsi calculation, not alignment; align
        if path and row:
            self.csv_name = NDSI_CSV + "_" + path + "_" + row + ".csv"
        else:
            self.csv_name = ALIGN_CSV

        self.csv_path = os.path.join(output_dir, self.csv_name)
        self.arguments = arguments

    def start(self) -> None:
        """
        Starts creating and writing to the csv.
        :return: None
        """
        self.create()
        self.add_item()

    def create(self) -> None:
        """Verifies if the file already exists. If it doesn't, that means the csv file is not created yet.
        Create it if it doesn't exist, append if it does."""
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
        Adds the argument returned from the processing to the NDSI csv file, while locking the file for multiprocess
        protection.
        :return: None
        """
        result = self.arguments

        lock = FileLock(self.csv_path + ".lock")
        with lock:
            with open(self.csv_path, "a") as file:
                writer = csv.writer(file)
                writer.writerow(result)

    @staticmethod
    def get_default_align_csv() -> list:
        """
        Creates the default align item csv design. It has the glacier_id, path and row for identifying the glacier which
         was processed, and the total processed and valid in order to create a ratio of successful alignments.
        :return: list which will represent the keys for the ndsi csv dictionary.
        """
        attributes = ['GLACIER_ID',
                      'PATH',
                      'ROW',
                      'TOTAL PROCESSED',
                      'VALID ALIGNED',
                      'RATIO']
        return attributes

    @staticmethod
    def get_default_ndsi_csv() -> list:
        """
        Creates the default ndsi csv degisn, which contains the glacier_id, path, row, year, month and day in order to
        identify and analyze the result of the ARIMA prediction, and the snow ratio which will be the input to ARIMA for
        prediction.
        :return: list which will represent the keys for the ndsi csv dictionary.
        """
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
