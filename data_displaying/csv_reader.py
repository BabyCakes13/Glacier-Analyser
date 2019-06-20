#!/usr/bin/env python3

import datetime
import sys

import matplotlib
matplotlib.use('gtk3cairo')
from matplotlib import pyplot as plt
import collections
import numpy as np
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# THRESHOLD = 1 # removes the big outliers
THRESHOLD = 1  # removes also the zero values from the down level


class CSVReader:
    def __init__(self, csv):
        self.csv = csv
        self.data_sorted = self.read_csv()

        #self.plot_results(data)
        self.plot_show()

    def read_csv(self):
        """
        Reads the csv and organizes the data for plotting, removing outliers.
        :return:
        """
        h = pd.read_csv(self.csv)
        snow = h['SNOW_RATIO']
        dates = self.create_datetime()

        input_data = list(zip(dates, snow))
        input_data.sort()

        self.plot_results ("Sorted INPUT data", input_data)

        #input_data = self.remove_zeros(input_data)

        #self.plot_results ("NO zeros", input_data)

        input_data = self.remove_outliers(input_data, THRESHOLD)

        self.plot_results ("Inliers", input_data)

        self.make_arima(input_data)

        #input_data = self.interpolate(input_data)
        #self.plot_results ("Interpolated", input_data)

        return input_data

    def interpolate(self, input):
        interpolated_dates = pd.date_range(input[0][0], input[len(input)-1][0], freq='1Y')

        output = []

        dense_ndsi = []
        for date in interpolated_dates:
            for real_date, ndsi in input:

                real_date = datetime.datetime(real_date.year, real_date.month, real_date.day)
                delta = real_date - date

                if(delta.days < 175 and delta.days > -175):
                    dense_ndsi.append(ndsi)
                else:
                    dense_ndsi.append(np.nan)

                print(" REAL: ", real_date, " FAKE: ", date, " delta: ", delta)

        print(dense_ndsi)

        s = pd.Series(dense_ndsi)
        s.interpolate(method='linear', limit = 100)

        print (s)

        output = list(zip(interpolated_dates, s))

        return output


    def remove_zeros(self, input, threshold = 0.002):
        output = []

        for d in input:
            if d[1] > threshold:
                output.append(d)

        return output

    def plot_results(self, title, data):
        plt.xlabel('Years')
        plt.ylabel('Results')
        plt.xticks(rotation=90)

        plt.plot(*zip(*data), linestyle='-', marker='o', label=title)

    def plot_show(self):
        plt.legend(loc='upper left')
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

    def make_arima(self, dataset):
        COUNT = 10
        predictions = []
        train, test, history = self.make_test_train(dataset)

        #TODO: this might be removed and just specify period to ARIMA directly
        fake_dates = pd.date_range(history[0][0], periods=100, freq='M')
        future_dates = pd.date_range(dataset[len(dataset) - 1][0], periods=COUNT+1, freq='M')

        print(fake_dates)

        print ("Fake dates count ", len(fake_dates), " values: ", fake_dates)
        print ("Train datas count ", len(history), " values: ", history)

        last_model = None
        last_model_fit = None

        for index in range(len(test) + COUNT):
            print("estimating on: ", history)
            real_dates, ndsi = zip(*history)
            try:
                model = ARIMA(ndsi, order=(5, 1, 0), dates=fake_dates)
                model_fit = model.fit()
                output = model_fit.forecast(steps=COUNT)
            except:
                #prepare next iteration of model estimating
                if(index < len(test)):
                    observed = test[index][1]
                    history.append((test[index][0], observed))
                    continue

            last_model = model
            last_model_fit = model_fit

            predicted = output[0][0]
            error = output[1][0]

            print("outpout is ", output)
            print("predicted is ", predicted)

            if(index < len(test)):
                observed = test[index][1]
                #prepare next iteration of model estimating
                history.append((test[index][0], observed))
                predictions.append((test[index][0], predicted))
                print('predicted=%f, expected=%f' % (predicted, observed))
            else:

                for predicted in output[0]:
                    #prepare next iteration of model estimating
                    history.append((future_dates[index - len(test)].date(), predicted))
                    predictions.append((future_dates[index - len(test)].date(), predicted))
                    index+=1
                break


        #self.plot_results("train", train)
        #self.plot_results("test", test)
        self.plot_results("predicted", predictions)


        #for t in range(len(test)):
        #    model = ARIMA(snow, order=(len(history), 2, 1), dates=dates)
        #    model_fit = model.fit()
        #    output = model_fit.forecast()
        #    yhat = output[0]
        #    obs = test[t]
        #    history.append(obs)
        #    predictions.append(yhat)
        #    print('predicted=%f, expected=%f' % (yhat, obs))
        #plt.plot(test)
        #plt.plot(predictions, color='red')
        #plt.show()

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
    def remove_outliers(dataset, threshold):
        """
        Remove outliers from the datased based on the z-test with the specified threshold
        :param dataset: The set of data which will have its outliers removed.
        :param threshold: Threshold for detecting outliers.
        :return: A list formed of outliers from the dataset.
        """
        inliers = []
        dates,ndsi = zip(*dataset)
        mean = np.mean(ndsi)
        std = np.std(ndsi)

        for entry in dataset:
            z_score = (entry[1] - mean) / std
            if np.abs(z_score) < threshold:
                inliers.append(entry)

        return inliers


if __name__ == "__main__":
    # csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112C0025_69.552_35.438/ndsi_152_036.csv")
    # csv = CSVReader("/storage/maria/D/Programming/Facultate/test_12_06/AF5Q112C0025_69.552_35.438/ndsi_153_035.csv")
    csv = CSVReader(sys.argv[1])

    #date, snow_coverage = csv.read_csv()
    # csv.make_arima(snow_coverage)
    # csv.create_hardcoded_dates()
    # dates, snow = csv.create_dummy_dataset()
    # csv.make_arima(dates, snow)

    #csv.make_stationary(snow_coverage)
