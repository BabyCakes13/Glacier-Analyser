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
        self.h = None

    def read_csv(self):
        """
        Reads the csv and organizes the data for plotting, removing outliers.
        :return:
        """
        self.h = pd.read_csv(self.csv)
        snow = self.h['SNOW_RATIO']
        scene = self.h['SCENE']
        dates = self.create_datetime()

        input_data = list(zip(dates, snow, scene))
        input_data.sort()

        dates, snow, scene = zip(*input_data)

        input_data = list(zip(dates, snow))

        return input_data, scene

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
