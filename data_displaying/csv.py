import csv
import os
import definitions
from util import strings


ALIGN_CSV = 'align.csv'
NDSI_CSV = 'ndsi.csv'


class CSV:
    def __init__(self, csv_name, output, arguments):
        """
        Writes or appends to a csv based on the option (either align or process ndsi.
        :param option: alignment or ndsi
        :param arguments: arguments of alignment or ndsi
        """
        self.csv_name = csv_name
        self.csv_path = os.path.join(output, csv_name)
        self.arguments = arguments

    def start(self) -> None:
        """
        Starts creating and writing to the csv.
        :return: None
        """
        self.create()
        self.check_first_row()
        self.add_item()

    def create(self) -> None:
        """Verifies if the first column, which represents the names of the columns, exist. If it doesn't, that means
               the csv file is not created yet. Create it if it doesn't exist, append if it does."""
        if os.path.isfile(self.csv_path) is False:
            print(definitions.PRINT_CODES[0] + "Creating csv...")
            with open(self.csv_path, "w") as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # align
                if ALIGN_CSV == self.csv_name:
                    writer.writerow(self.get_default_align_csv())
                # ndsi
                elif NDSI_CSV == self.csv_name:
                    writer.writerow(strings.get_default_ndsi_csv())
                else:
                    print(definitions.PRINT_CODES[1] + "There option is not valid. Not writing.")
                    return

                file.flush()

    def check_first_row(self):
        with open(self.csv_path, "r") as file:
            reader = csv.reader(file)
            first_row = next(reader)

    def add_item(self) -> None:
        """
        Adds the argument to the csv file.
        :return: None
        """
        result = self.arguments

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

