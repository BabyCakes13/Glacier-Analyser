import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA

# THRESHOLD = 1 # removes the big outliers
THRESHOLD = 1  # removes also the zero values from the down level


class CSVReader:
    def __init__(self, csv):
        self.csv = csv
        x, y = self.read_csv()
        self.plot_results(x, y)

    def read_csv(self):
        """
        Reads the csv and organizes the data for plotting, removing outliers.
        :return:
        """
        h = pd.read_csv(self.csv)
        snow = h['SNOW_RATIO']
        dates = self.create_datetime()
        sorted(dates)

        results = dict(zip(snow, dates))
        snow_outliers = self.detect_outliers(snow, THRESHOLD)
        results_normalized = {k: v for k, v in results.items() if k not in snow_outliers}

        snow_normalized = list(results_normalized.keys())
        dates_normalized = list(results_normalized.values())

        return dates_normalized, snow_normalized

    def plot_results(self, x, y):
        plt.xlabel('Years')
        plt.ylabel('Results')
        plt.title('Results over years.')
        plt.xticks(rotation=90)

        plt.plot(x, y, linestyle='-', marker='o')
        plt.show()

    def create_datetime(self):
        """
        Combines the year, month and day for each result in the ndsi csv.
        :return: A list formed of datetime objects as year, month and day
        """
        h = pd.read_csv(self.csv)
        years = h['YEAR']
        months = h['MONTH']
        days = h['DAY']

        dates = []
        for year, month, day in zip(years, months, days):
            date = datetime.datetime(year=year, month=month, day=day).date()
            dates.append(date)

        return dates

    def make_arima(self, dates, snow):
        train, test, history = self.make_test_train(snow)

        predictions = []
        dates = pd.date_range(dates[0], dates[len(dates) - 1], freq='MS')
        for t in range(len(test)):
            model = ARIMA(snow, order=(len(history), 2, 1), dates=dates)
            model_fit = model.fit()
            output = model_fit.forecast()
            yhat = output[0]
            obs = test[t]
            history.append(obs)
            predictions.append(yhat)
            print('predicted=%f, expected=%f' % (yhat, obs))
        plt.plot(test)
        plt.plot(predictions, color='red')
        plt.show()

    def make_stationary(self, dataset):
        snow = np.log(dataset)
        snow_diff = snow - snow.shift(1)
        snow_diff.dropna().plot()

    def create_hardcoded_dates(self):
        dates, snow = self.read_csv()
        frequency = pd.date_range(start=dates[0], end=dates[len(dates) - 1], freq='M')

        frequency_dates = []
        for i in range(0, len(snow)):
            frequency_dates.append(frequency[i])

        #        self.plot_results(frequency_dates, snow)
        return frequency_dates

    def create_dummy_dataset(self):
        dates, snow = self.read_csv()
        frequency = pd.date_range(start=dates[0], end=dates[len(dates) - 1], freq='M')

        frequency_dates = []
        for i in range(0, len(snow)):
            frequency_dates.append(frequency[i])
            snow[i] = i

        print(len(snow))
        print(len(frequency_dates))

        self.plot_results(frequency_dates, snow)
        return frequency_dates, snow

    @staticmethod
    def make_test_train(dataset):
        size = int(len(dataset) * 0.66)
        train, test = dataset[0:size], dataset[size:len(dataset)]
        history = [x for x in train]

        return train, test, history

    @staticmethod
    def detect_outliers(dataset, threshold):
        """
        Remove outliers from the datased based on the z-test with the specified threshold
        :param dataset: The set of data which will have its outliers removed.
        :param threshold: Threshold for detecting outliers.
        :return: A list formed of outliers from the dataset.
        """
        outliers = []
        mean_1 = np.mean(dataset)
        std_1 = np.std(dataset)

        for snow in dataset:
            z_score = (snow - mean_1) / std_1
            if np.abs(z_score) > threshold:
                outliers.append(snow)

        return outliers


if __name__ == "__main__":
    # csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112C0025_69.552_35.438/ndsi_152_036.csv")
    # csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112C0025_69.552_35.438/ndsi_153_035.csv")
    csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112B0009_68.891_34.807/ndsi_153_036.csv")

    date, snow_coverage = csv.read_csv()
    # csv.make_arima(snow_coverage)
    # csv.create_hardcoded_dates()
    # dates, snow = csv.create_dummy_dataset()
    # csv.make_arima(dates, snow)

    csv.make_stationary(snow_coverage)
