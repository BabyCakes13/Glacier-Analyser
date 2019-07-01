# flake8: noqa 405

import os
import signal
import subprocess
from tkinter import *
from tkinter import filedialog

import definitions

sys.path.append(sys.path[0] + '/..')
from data_displaying import page as fh  # noqapep8 


class FrameProcess(fh.Page):
    """
    Class which handles process calling in the GUI.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor which initialises the frame object, and sets up the GUI parameters.
        :param args: Arguments from Frame.
        :param kwargs: Arguments from Frame.
        """
        fh.Page.__init__(self, *args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.create_buttons()
        self.create_labels()

        self.big_input_entry, self.input_entry, self.output_entry, self.max_process_entry = self.create_entries()
        self.sp = None

    def create_buttons(self) -> None:
        """
        Button creator.
        :return: None
        """

        browse = Button(self, text="BROWSE BIG INPUT DIRECTORY", command=self.browse_big_glacier_directory)
        browse.grid(row=0, column=2, sticky=W + E)

        browse = Button(self, text="BROWSE INPUT DIRECTORY", command=self.browse_glacier_directory)
        browse.grid(row=1, column=2, sticky=W + E)

        browse = Button(self, text="BROWSE OUTPUT DIRECTORY", command=self.browse_output_directory)
        browse.grid(row=2, column=2, sticky=W + E)

        process = Button(self, text="START PROCESS", command=self.start_process)
        process.grid(row=4, column=1, sticky=W + E)

        process = Button(self, text="STOOP PROCESS", command=self.stop_process)
        process.grid(row=5, column=1, sticky=W + E)

    def create_labels(self) -> None:
        """
        Label creator.
        :return: None
        """
        big_dir = Label(self, text="Big directory (blank if none):")
        glacier_dir = Label(self, text="Glacier directory:")
        output_dir = Label(self, text="Processing save directory:")
        max_process_dir = Label(self, text="Used processes:")

        big_dir.grid(row=0, column=0, sticky=W)
        glacier_dir.grid(row=1, column=0, sticky=W)
        output_dir.grid(row=2, column=0, sticky=W)
        max_process_dir.grid(row=3, column=0, sticky=W)

    def create_entries(self) -> tuple:
        """
        Creates entries as input fields.
        :return: None
        """
        big_entry = Entry(self)
        input_entry = Entry(self)
        output_entry = Entry(self)
        max_process_entry = Entry(self)

        big_entry.grid(row=0, column=1, sticky=W)
        input_entry.grid(row=1, column=1, sticky=W)
        output_entry.grid(row=2, column=1, sticky=W)
        max_process_entry.grid(row=3, column=1, sticky=W)

        return big_entry, input_entry, output_entry, max_process_entry

    def browse_big_glacier_directory(self) -> None:
        """
        Implement file hierarchy browsing to find the big glacier directory.
        :return: None
        """
        filename = filedialog.askdirectory(initialdir=definitions.ROOT_DIR, title="Select directory which has glacier "
                                                                                  "directories for processing.")
        self.set_input(filename, self.big_input_entry)

    def browse_glacier_directory(self):
        """
        Implement file hierarchy browsing to find the glacier directory.
        :return: None
        """
        filename = filedialog.askdirectory(initialdir=definitions.ROOT_DIR, title="Select directory which has the TIF"
                                                                                  "images for processing..")
        self.set_input(filename, self.input_entry)

    def browse_output_directory(self) -> None:
        """
        Implement file hierarchy browsing to find the output directory.
        :return: None
        """
        filename = filedialog.askdirectory(initialdir=definitions.ROOT_DIR, title="Select directory which will hold the"
                                                                                  "results from the processing")
        self.set_input(filename, self.output_entry)

    def get_input(self) -> tuple:
        """
        Get input from the entries.
        :return: None
        """
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

    def stop_process(self) -> None:
        """
        Handle the stop process signal from stop process button event.
        :return: None
        """
        if self.sp:
            self.sp.send_signal(signal.SIGINT)
            self.sp = None

    def start_process(self) -> None:
        """
        Starts the processing when start process is pressed.
        :return: None
        """
        big_glacier_dir, glacier_dir, output_dir, max_process = self.get_input()

        if self.validate_input(big_glacier_dir=big_glacier_dir,
                               glacier_dir=glacier_dir,
                               output_dir=output_dir,
                               max_process=max_process):
            task = ["python3", "./data_processing/process.py",
                    big_glacier_dir, glacier_dir,
                    output_dir, max_process]
            self.stop_process()
            self.sp = subprocess.Popen(task)

    @staticmethod
    def set_input(text, entry) -> None:
        """
        Sets the input of an entry.
        :param text: Text of entry.
        :param entry: The entry.
        :return: None
        """
        entry.delete(0, END)
        entry.insert(0, text)
