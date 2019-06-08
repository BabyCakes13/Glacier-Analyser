import csv
import os
import definitions
from data_processing import process_alignment
from util import strings


class HomographyCSV:
    """Class which validates the homography of the alignment."""
    def __init__(self, glacier_id, homography_csv):
        """The results are written in the homography file."""
        self.glacier_id = glacier_id
        self.homography_csv = homography_csv

    def start(self):
        """Start validating."""
        self.validate_csv()
        self.generate_csv_item()
        self.add_item_to_csv()
        self.add_item_to_csv()

    def generate_csv_item(self):
        """Generates the csv item with the corresponding attributes."""
        if process_alignment.VALID_TRANSFORMATIONS == 0:
            ratio = 0
        else:
            ratio = process_alignment.VALID_TRANSFORMATIONS / process_alignment.TOTAL_TRANSFORMATIONS
        item = [
            self.glacier_id,
            definitions.MAX_FEATURES,
            definitions.GOOD_MATCH_PERCENT,
            definitions.ALLOWED_ERROR,
            definitions.ALLOWED_INTEGRAL,
            process_alignment.VALID_TRANSFORMATIONS,
            process_alignment.TOTAL_TRANSFORMATIONS,
            ratio
        ]
        return item

    def add_item_to_csv(self):
        """Adds the generated csv item in the homography file."""
        result = self.generate_csv_item()

        with open(self.homography_csv, "a") as file:
            writer = csv.writer(file)
            writer.writerow(result)

    def validate_csv(self):
        """Verifies if the first column, which represents the names of the columns, exist. If it doesn't, that measns
        the csv file is not created yet."""
        if os.path.isfile(self.homography_csv) is False:
            with open(self.homography_csv, "w") as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(strings.get_default_homography_csv())
                file.flush()

        with open(self.homography_csv, "r+") as file:
            reader = csv.reader(file)
            rows_list = list(reader)

            if len(rows_list) == 0:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(strings.get_default_homography_csv())

