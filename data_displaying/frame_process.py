import os
import subprocess
import signal

from tkinter import *
from tkinter import filedialog

import definitions

sys.path.append(sys.path[0] + '/..')
from data_displaying import page as fh
from data_processing import process


class Process(fh.Page):
    INPUT_DIR = None
    OUTPUT_DIR = None

    def __init__(self, *args, **kwargs):
        fh.Page.__init__(self, *args, **kwargs)

        self.create_buttons()
        self.create_labels()

        self.big_input_entry, self.input_entry, self.output_entry, self.max_process_entry = self.create_entries()
        self.sp = None

    def create_buttons(self):
        """
        Button creator.
        :return:
        """

        browse = Button(self, text="BROWSE BIG INPUT DIRECTORY", command=self.browse_big_glacier_directory)
        browse.grid(row=2, column=0)

        browse = Button(self, text="BROWSE INPUT DIRECTORY", command=self.browse_glacier_directory)
        browse.grid(row=5, column=0)

        browse = Button(self, text="BROWSE OUTPUT DIRECTORY", command=self.browse_output_directory)
        browse.grid(row=8, column=0)

        process = Button(self, text="START PROCESS", command=self.start_process)
        process.grid(row=11, column=0)

        process = Button(self, text="STOOP PROCESS", command=self.stop_process)
        process.grid(row=12, column=0)

        # TODO show how many files have been processed till now and show loading button which finishes when it is done.

    def create_labels(self):
        """
        Label creator.
        :return:
        """
        big_dir = Label(self, text="Path to the directory which contains directories of glaciers."
                                   "Leave blank if not the case")
        glacier_dir = Label(self, text="Path to the glacier directory which contains the images.")
        output_dir = Label(self, text="Path to the directory which will contain the result images after processing.")
        max_process_dir = Label(self, text="The number of max processes which can run for processing..")

        big_dir.grid(row=0, column=0)
        glacier_dir.grid(row=3, column=0)
        output_dir.grid(row=6, column=0)
        max_process_dir.grid(row=9, column=0)

    def create_entries(self):
        """
        Creates entries as input fields.
        :return:
        """
        big_entry = Entry(self)
        input_entry = Entry(self)
        output_entry = Entry(self)
        max_process_entry = Entry(self)

        big_entry.grid(row=1, column=0)
        input_entry.grid(row=4, column=0)
        output_entry.grid(row=7, column=0)
        max_process_entry.grid(row=10, column=0)

        return big_entry, input_entry, output_entry, max_process_entry

    def browse_big_glacier_directory(self):
        filename = filedialog.askdirectory(initialdir=definitions.ROOT_DIR, title="Select directory which has glacier "
                                                                                  "directories for processing.")
        self.set_input(filename, self.big_input_entry)

    def browse_glacier_directory(self):
        filename = filedialog.askdirectory(initialdir=definitions.ROOT_DIR, title="Select directory which has the TIF"
                                                                                  "images for processing..")
        self.set_input(filename, self.input_entry)

    def browse_output_directory(self):
        filename = filedialog.askdirectory(initialdir=definitions.ROOT_DIR, title="Select directory which will hold the"
                                                                                  "results from the processing")
        self.set_input(filename, self.output_entry)

    def get_input(self):
        big_glacier_dir = self.big_input_entry.get()
        glacier_dir = self.input_entry.get()
        output_dir = self.output_entry.get()
        max_process = self.max_process_entry.get()

        return big_glacier_dir, glacier_dir, output_dir, max_process

    @staticmethod
    def validate_input(big_glacier_dir, glacier_dir, output_dir, max_process) -> bool:
        """
        Checks whether the input variables are correct or not, type wise
        :return: True if the input is valid, False otherwise.
        """
        print(max_process)
        if not os.path.isdir(big_glacier_dir) and big_glacier_dir != "":
            print("The big glacier directory is not valid.")
            return False
        elif not os.path.isdir(glacier_dir):
            print("The glacier directory is not valid.")
            return False
        elif not os.path.isdir(output_dir):
            print("The output directory is not valid.")
            return False
        elif not max_process.isdigit():
            print("The number of processes must be a number.")
            return False
        elif not (1 <= int(max_process) < 30):
            print("The number of processes must be between 1 and 30.")
            return False
        else:
            return True

    def stop_process(self):
        if self.sp:
            self.sp.send_signal(signal.SIGINT)

    def start_process(self):
        big_glacier_dir, glacier_dir, output_dir, max_process = self.get_input()

        if self.validate_input(big_glacier_dir=big_glacier_dir,
                               glacier_dir=glacier_dir,
                               output_dir=output_dir,
                               max_process=max_process):

            task = ["python3", "./data_processing/process.py",
                    big_glacier_dir, glacier_dir,
                    output_dir, max_process]

            self.sp = subprocess.Popen(task)

    @staticmethod
    def set_input(text, entry):
        entry.delete(0, END)
        entry.insert(0, text)
