#!/usr/bin/env python3

import datetime

import numpy as np
import pandas as pd
# fixed the no background matplotlib bug
# matplotlib.use('gtk3cairo')
from pandas.plotting import register_matplotlib_converters

# fixing the future pandas warning
register_matplotlib_converters()


class DatasetHandler:
    def __init__(self, csv):
        self.csv = csv

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

        return input_data

    @staticmethod
    def remove_zeros(input_data, minimum=0.002):
        """
        Keeps only values from the input data set if they are greater than the allowed minimum..
        :param input_data:
        :param minimum:
        :return:
        """
        output = []

        for d in input_data:
            if d[1] > minimum:
                output.append(d)

        return output

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

    @staticmethod
    def remove_outliers(dataset, threshold=1):
        """
        Remove outliers from the datased based on the z-test with the specified threshold
        :param dataset: The set of data which will have its outliers removed.
        :param threshold: Threshold for detecting outliers.
        :return: A list formed of outliers from the dataset.
        """
        inliers = []
        dates, ndsi = zip(*dataset)
        mean = np.mean(ndsi)
        std = np.std(ndsi)

        for entry in dataset:
            z_score = (entry[1] - mean) / std
            if np.abs(z_score) < threshold:
                inliers.append(entry)

        return inliers

    @staticmethod
    def interpolate(input_data):
        """
        Interpolation for later. # TODO
        :param input_data:
        :return:
        """
        interpolated_dates = pd.date_range(input_data[0][0], input_data[len(input_data) - 1][0], freq='1Y')

        dense_ndsi = []
        for date in interpolated_dates:
            for real_date, ndsi in input_data:

                real_date = datetime.datetime(real_date.year, real_date.month, real_date.day)
                delta = real_date - date

                if 175 > delta.days > -175:
                    dense_ndsi.append(ndsi)
                else:
                    dense_ndsi.append(np.nan)

                print(" REAL: ", real_date, " FAKE: ", date, " delta: ", delta)

        s = pd.Series(dense_ndsi)
        s.interpolate(method='linear', limit=100)

        output = list(zip(interpolated_dates, s))

        return output