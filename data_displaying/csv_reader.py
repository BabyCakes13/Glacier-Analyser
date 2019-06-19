import matplotlib.pyplot as plt
import pandas as pd
from stat


class CSVReader:
    def __init__(self, csv):
        self.csv = csv

    def read_csv(self):
        h = pd.read_csv(self.csv)
        snow_coverage = h['SNOW_RATIO']
        date = self.combine_year_month_day()

        plt.xlabel('Years')
        plt.ylabel('Results')
        plt.title('Results over years.')
        plt.xticks(rotation=90)

        plt.plot(date, snow_coverage, linestyle='-', marker='o')
        plt.show()

    def combine_year_month_day(self):
        """
        Combines the year, month and day for each result in the ndsi csv.
        :return:
        """
        h = pd.read_csv(self.csv)
        years = h['YEAR']
        months = h['MONTH']
        day = h['DAY']

        combined = [str(a) + "-" + str(b) + "-" + str(c) for a, b, c in zip(years, months, day)]
        return combined


if __name__ == "__main__":
    # csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112C0025_69.552_35.438/ndsi_152_036.csv")
    # csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112C0025_69.552_35.438/ndsi_153_035.csv")
    csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112B0009_68.891_34.807/ndsi_153_036.csv")
    csv.read_csv()
