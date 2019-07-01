# flake8: noqa 405
"""
Module which handles download GUI.
"""
import os
import signal
import subprocess
from tkinter import *
from tkinter import filedialog

import definitions

sys.path.append(sys.path[0] + '/..')
from data_displaying import page as fh  # noqa


class FrameDownload(fh.Page):
    """
    Class which holds the items for the download window.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor which initialises the frame object,
         and sets up the GUI parameters.
        :param args: Arguments from Frame.
        :param kwargs: Arguments from Frame.
        """
        fh.Page.__init__(self, *args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.create_buttons()
        self.create_labels()
        self.sp = None

        self.csv_entry, self.download_dir_entry, \
        self.max_processes_entry = self.create_entries()

    def create_buttons(self) -> None:
        """
        Button creator.
        :return: None
        """
        browse = Button(self, text="BROWSE CSV", command=self.browse_csv)
        browse.grid(row=0, column=2, sticky=W + E)

        browse = Button(self, text="BROWSE OUTPUT DIRECTORY",
                        command=self.browse_output_directory)
        browse.grid(row=1, column=2, sticky=W + E)

        submit = Button(self, text="START DOWNLOAD",
                        command=self.start_download)
        submit.grid(row=3, column=1, sticky=W + E)

        submit = Button(self, text="STOP DOWNLOAD", command=self.stop_download)
        submit.grid(row=4, column=1, sticky=W + E)

    def create_labels(self) -> None:
        """
        Label creator.
        :return: None
        """
        csv = Label(self, text="Glacier CSV:")
        output_dir = Label(self, text="Download directory:")
        max_processes = Label(self, text="Used processes:")

        csv.grid(row=0, column=0, sticky=W)
        output_dir.grid(row=1, column=0, sticky=W)
        max_processes.grid(row=2, column=0, sticky=W)

    def create_entries(self) -> tuple:
        """
        Creates entries as input fields.
        :return: tuple
        """
        csv = Entry(self)
        output_dir = Entry(self)
        max_processes = Entry(self)

        csv.grid(row=0, column=1, sticky=W)
        output_dir.grid(row=1, column=1, sticky=W)
        max_processes.grid(row=2, column=1, sticky=W)

        return csv, output_dir, max_processes

    def browse_csv(self) -> None:
        """
        Search for the csv file which contains glacier download data.
        :return: The path to the csv glacier inventory.
        """
        filename = \
            filedialog.askopenfilename(initialdir=definitions.FILES_DIR,
                                       title="Select file",
                                       filetypes=(("CSV files", "*.csv"),))
        self.set_input(filename, self.csv_entry)

    def browse_output_directory(self) -> None:
        """
        Search for the csv file which contains glacier download data.
        :return: The path to the csv glacier inventory.
        """
        filename = \
            filedialog.askdirectory(initialdir=definitions.ROOT_DIR,
                                    title="Select directory for download output.")
        self.set_input(filename, self.download_dir_entry)

    def get_input(self) -> tuple:
        """
        Gets the text which is set in the entries.
        :return: Tuple formed of the inputs.
        """
        csv = self.csv_entry.get()
        download_dir = self.download_dir_entry.get()
        max_processes = self.max_processes_entry.get()

        return csv, download_dir, max_processes

    @staticmethod
    def validate_input(csv, download_dir, max_processes) -> bool:
        """
        Checks whether the input variables are correct or not, type wise.
        :param csv: The csv should be the path to the input
        world glacier inventory csv.
        :param download_dir: The download dir should be the path to the
        download directory for storing the items.
        :param max_processes: Max processes should be the max number of
        processes the application will open to run, a
        min of 1, and a max of 30.
        :return: True if the input is valid, False otherwise.
        """
        if not os.path.isfile(csv):
            return False
        elif not os.path.isdir(download_dir):
            return False
        elif not max_processes.isdigit():
            return False
        elif not 1 <= int(max_processes) < 30:
            return False

        return True

    def stop_download(self) -> None:
        """
        Handle the stop process signal from stop process button event.
        :return: None
        """
        if self.sp:
            self.sp.send_signal(signal.SIGINT)
            self.sp = None

    def start_download(self) -> None:
        """
        Start the download process.
        :return: None
        """
        csv, download_dir, max_processes = self.get_input()

        if self.validate_input(csv, download_dir, max_processes):
            task = ["python3", "./data_gathering/download.py",
                    csv, download_dir, max_processes]
            self.stop_download()
            self.sp = subprocess.Popen(task)

    @staticmethod
    def set_input(text, entry) -> None:
        """
        Sets text in an entry.
        :param text: The text from the entry.
        :param entry: The entry.
        :return: None
        """
        entry.delete(0, END)
        entry.insert(0, text)
