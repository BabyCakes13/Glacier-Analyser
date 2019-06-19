import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
import datetime


THRESHOLD = 1 # removes the big outliers
# THREHOLD = 0.5 # removes also the zero values from the down level


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

    def make_arima(self, series, dates):
        size = int(len(series) * 0.80)
        train, test = series[0:size], series[size:len(series)]
        history = [x for x in train]
        predictions = []
        for t in range(len(test)):
            dates = self.create_datetime()
            dates = pd.date_range(start='1973-05-01', end='1973-09-30', freq='D')
            model = ARIMA(series, order=(len(history), 1, 1), dates=dates)
            model_fit = model.fit(disp=0)
            output = model_fit.forecast()
            yhat = output[0]
            obs = test[t]
            history.append(obs)
            predictions.append(yhat)
            print('predicted=%f, expected=%f' % (yhat, obs))
        plt.plot(test)
        plt.plot(predictions, color='red')
        plt.show()

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

    snow_coverage, date = csv.read_csv()
    
    #csv.make_arima(snow_coverage, date)

