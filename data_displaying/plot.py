#!/usr/bin/env python3

# fixed the no background matplotlib bug
# matplotlib.use('gtk3cairo')
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from pandas.plotting import register_matplotlib_converters

# fixing the future pandas warning
register_matplotlib_converters()

from data_processing import arima as ari
from data_preparing import dataset_handler as dh


class Plot:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

        self.first_pick = None
        self.second_pick = None

        self.first_an = None
        self.second_an = None

    def start(self, csv):
        """
        Method which is called on command line display argument.
        :return: None
        """
        h = dh.DatasetHandler(csv)
        input_data = h.read_csv()
        self.plot_results("Input Data Sorted", input_data)

        input_data_inliers = h.remove_outliers(input_data)
        self.plot_results("Input Data Sorted Inliers", input_data_inliers)

        # input_data_no_zeros = h.remove_zeros(input_data)
        # self.plot_results("Input Data Sorted No Zeros", input_data_inliers)

        arima = ari.Arima(input_data)
        predictions = arima.start(count=10)

        if len(predictions) > 0:
            self.plot_results("predicted", predictions)

        self.plot_show()

    def plot_results(self, title, data):
        """
        Plots the result in a matplotlib window.
        :param title:
        :param data:
        :return:
        """
        plot = self.ax

        plot.set_xlabel('Years')
        plot.set_ylabel('Results')

        plot.plot(*zip(*data), linestyle='-', marker='o', label=title, picker=3.14)

    def plot_show(self):
        plot = self.ax

        self.fig.canvas.mpl_connect('pick_event', self.onpick3)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        plot.legend(loc='upper left')

        plt.show()

    def onpick3(self, event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind

            current_pick = (xdata[ind], ydata[ind])

            if current_pick == self.first_pick:
                return

            self.remove_an()

            self.second_pick = self.first_pick
            self.first_pick = (xdata[ind], ydata[ind])

            print("First", self.first_pick)
            print("Second", self.second_pick)

            if self.second_pick:
                self.second_an = self.ax.annotate('second', xy=self.second_pick,
                                                  xytext=(self.second_pick[0], self.second_pick[1] + 0.1),
                                                  arrowprops=dict(facecolor='black', shrink=0.05))
            self.first_an = self.ax.annotate('first', xy=self.first_pick,
                                             xytext=(self.first_pick[0], self.first_pick[1] + 0.1),
                                             arrowprops=dict(facecolor='black', shrink=0.05))
        plt.show()

    def on_key(self, event):
        if event.key == "delete":
            print("in delet")
            self.first_pick = None
            self.second_pick = None
            self.remove_an()
        plt.show()

    def remove_an(self):
        if self.first_an:
            self.first_an.remove()
            self.first_an = None

        if self.second_an:
            self.second_an.remove()
            self.second_an = None

        # TODO delete annotations


def handle_scene_pick(self):
    pass
