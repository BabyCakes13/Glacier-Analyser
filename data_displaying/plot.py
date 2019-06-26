#!/usr/bin/env python3

import numpy as np
# fixed the no background matplotlib bug
# matplotlib.use('gtk3cairo')
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from pandas.plotting import register_matplotlib_converters

# fixing the future pandas warning
register_matplotlib_converters()

from data_processing import arima as ari
from data_preparing import dataset_handler as dh


class Plot:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

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

        plot.plot(*zip(*data), linestyle='-', marker='o', label=title, picker=20)

    def plot_show(self):
        plot = self.ax

        def onpick3(event):
            if isinstance(event.artist, Line2D):
                thisline = event.artist
                xdata = thisline.get_xdata()
                ydata = thisline.get_ydata()
                ind = event.ind
                print('onpick1 line:', np.column_stack([xdata[ind], ydata[ind]]))
            elif isinstance(event.artist, Rectangle):
                patch = event.artist
                print('onpick1 patch:', patch.get_path())
            elif isinstance(event.artist, Text):
                text = event.artist
                print('onpick1 text:', text.get_text())

        def onpress(event):
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))

        self.fig.canvas.mpl_connect('pick_event', onpick3)
        self.fig.canvas.mpl_connect('button_press_event', onpress)

        plot.legend(loc='upper left')

        plt.show()

    def handle_scene_pick(self):
        pass

