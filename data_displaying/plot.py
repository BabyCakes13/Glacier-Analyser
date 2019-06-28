"""
Module which handles plotting of data generated from prediction, and difference movement images.
"""
# !/usr/bin/env python3

# fixed the no background matplotlib bug
# !/usr/bin/env python3
import os
import signal
import subprocess

# fixed the no background matplotlib bug
import matplotlib

matplotlib.use('gtk3cairo')
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from pandas.plotting import register_matplotlib_converters

# fixing the future pandas warning
register_matplotlib_converters()

from data_processing import arima as ari
from data_preparing import dataset_handler as dh

INTERACTIVE = True

class Plot:
    """
    Class which handles plotting of data.
    """

    def __init__(self, csv):
        """
        Initializes the needed NDSI csv containing the snow pixel data in order to create data sets and plot.
        :param csv: The path to the csv file.
        """
        self.csv = csv

        self.fig, self.ax = plt.subplots()

        self.first_pick = None
        self.second_pick = None

        self.first_an = None
        self.second_an = None

        self.input_data = None
        self.scenes = None

        self.sp = []

    def start(self) -> None:
        """
        Method which is called on command line display argument.
        :return: None
        """
        h = dh.DatasetHandler(self.csv)
        self.input_data, self.scenes = h.read_csv()
        self.plot_results("Input Data Sorted", self.input_data)

        input_data_inliers = h.remove_outliers(self.input_data)
        self.plot_results("Input Data Sorted Inliers", input_data_inliers)

        # input_data_no_zeros = h.remove_zeros(input_data)
        # self.plot_results("Input Data Sorted No Zeros", input_data_inliers)

        arima = ari.Arima(self.input_data)
        predictions, mean_error = arima.start(count=5)

        if len(predictions) > 0:
            self.plot_results("predicted", predictions )
            plt.gcf().text(0.0, 0.94, 'Prediction Error is: %02.2f %%' % mean_error)

        plt.gcf().text(0.0, 0.97, "File Processed:" + self.csv)

        self.plot_show()

    def plot_results(self, title, data) -> None:
        """
        Plots the result in a matplotlib window.
        :param title: The title of the plot
        :param data: The data set of the plot.
        :return: None
        """
        plot = self.ax

        plot.set_xlabel('Years')
        plot.set_ylabel('Results')

        data, snow = zip(*data)
        plot.plot(data, snow, linestyle='-', marker='o', label=title, picker=3.14)

    def plot_show(self) -> None:
        """
        Show the plot.
        :return: None
        """
        plot = self.ax

        self.fig.canvas.mpl_connect('pick_event', self.onpick3)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('close_event', self.handle_close)

        plot.legend(loc='upper left')

        if INTERACTIVE:
            plt.show()
        else:
            plt.savefig(self.csv + '.plot.png')

    def handle_close(self, evt) -> None:
        """
        Method which handles close button, and stops all processes in the backend.
        :param evt: Event.
        :return: None
        """
        for p in self.sp:
            p.send_signal(signal.SIGTERM)
        print('Closed Figure!')

    def onpick3(self, event) -> None:
        """
        Event handler for picking in interactive mode graphic.
        :param event: Event.
        :return: None
        """
        if isinstance(event.artist, Line2D):
            this_line = event.artist
            x_data = this_line.get_xdata()
            y_data = this_line.get_ydata()
            ind = event.ind

            current_pick = (x_data[ind][0], y_data[ind][0])
            if current_pick == self.first_pick:
                return
            self.remove_an()

            self.second_pick = self.first_pick
            self.first_pick = current_pick

            # print("First", self.first_pick)
            # print("Second", self.second_pick)

            if self.second_pick:
                self.second_an = self.ax.annotate('second', xy=self.second_pick,
                                                  xytext=(self.second_pick[0], self.second_pick[1] + 0.1),
                                                  arrowprops=dict(facecolor='black', shrink=0.05))
            self.first_an = self.ax.annotate('first', xy=self.first_pick,
                                             xytext=(self.first_pick[0], self.first_pick[1] + 0.1),
                                             arrowprops=dict(facecolor='black', shrink=0.05))
        if self.first_pick and self.second_pick:
            self.start_displaying_diff_move(self.first_pick[0], self.second_pick[0])

        plt.draw()

    def start_displaying_diff_move(self, first_date, second_date) -> None:
        """
        Method which calls difference and movement image creation on pick of two images.
        :param first_date: The first image to compare.
        :param second_date: The second image to compare.
        :return: None
        """
        path, file = os.path.split(self.csv)

        first_scene = self.find_scene(first_date)
        second_scene = self.find_scene(second_date)

        first_path = os.path.join(path, first_scene + "_NDSI.TIF")
        second_path = os.path.join(path, second_scene + "_NDSI.TIF")

        if os.path.isfile(first_path) and os.path.isfile(second_path):
            task = ["python3", "data_processing/difference_movement.py",
                    first_path, second_path, path, first_scene, second_scene]
            self.sp.append(subprocess.Popen(task))

            plt.gcf().text(0.5, 0.9, "Processing " + first_scene + " vs " + second_scene + " ...",
                           horizontalalignment='center', verticalalignment='center',
                           fontsize=12, bbox=dict(facecolor='red'))

    def find_scene(self, date) -> str:
        """
        Find the scene of processing based on the picked date.
        :param date: The parameter returned on pick from graphic.
        :return: None
        """
        for i, item in enumerate(self.input_data):
            if date == item[0]:
                print("Date ", date, " scene ", self.scenes[i])
                return self.scenes[i]

    def on_key(self, event) -> None:
        """
        Handle delete of pickings in interactive mode graphic.
        :param event: Key pressing event, delete.
        :return: None
        """
        if event.key == "delete":
            self.first_pick = None
            self.second_pick = None
            self.remove_an()
        plt.show()

    def remove_an(self):
        """
        Remove arrows.
        :return: None
        """
        if self.first_an:
            self.first_an.remove()
            self.first_an = None

        if self.second_an:
            self.second_an.remove()
            self.second_an = None
