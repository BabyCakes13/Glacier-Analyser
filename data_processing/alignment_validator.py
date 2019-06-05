import csv
import os
import definitions
from data_processing import alignment_ORB
from util import strings


class HomographyCSV:
    def __init__(self, glacier_id, homography_csv):
        self.glacier_id = glacier_id
        self.homography_csv = homography_csv

    def start(self):
        self.validate_csv()
        self.generate_csv_item()
        self.add_item_to_csv()

    def generate_csv_item(self):
        if alignment_ORB.TOTAL_PROCESSED == 0:
            ratio = 0
        else:
            ratio = alignment_ORB.VALID_HOMOGRAPHIES / alignment_ORB.TOTAL_PROCESSED

        item = [
            self.glacier_id,
            definitions.MAX_FEATURES,
            definitions.GOOD_MATCH_PERCENT,
            definitions.ALLOWED_ERROR,
            definitions.ALLOWED_INTEGRAL,
            alignment_ORB.VALID_HOMOGRAPHIES,
            alignment_ORB.TOTAL_PROCESSED,
            ratio
        ]
        return item

    def add_item_to_csv(self):
        result = self.generate_csv_item()

        with open(self.homography_csv, "a") as file:
            writer = csv.writer(file)
            writer.writerow(result)

    def validate_csv(self):
        """Verify if the column names exist, write them if not."""
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
