import os
from tkinter import *
from tkinter import filedialog

import definitions

sys.path.append(sys.path[0] + '/..')
from data_displaying import page as fh
from data_displaying import plot


class Display(fh.Page):
    """
    Class which holds the items for the display window.
    """

    def __init__(self, *args, **kwargs):
        fh.Page.__init__(self, *args, **kwargs)

        self.create_labels()
        self.create_buttons()

        self.csv_entry = self.create_entries()

    def create_buttons(self):
        """
        Creates submit and browse buttons.
        :return:
        """
        browse = Button(self, text="BROWSE NDSI CSV", command=self.browse_csv)
        browse.grid(row=0, column=2, sticky=W)

        submit = Button(self, text="SUBMIT", command=self.start_displaying)
        submit.grid(row=1, column=1)

        # TODO show how many files have been processed till now and show loading button which finishes when it is done.

    def create_labels(self) -> None:
        """
        Creates the necessary labels for the entry input specifying the directions.
        :return: None
        """
        csv = Label(self, text="Path to the NDSI CSV results from the processing.")
        csv.grid(row=0, column=0, sticky=W)

    def create_entries(self) -> Entry:
        """
        Creates entries as input fields which will be filled with a path to the NDSI csv file.
        :return: None
        """
        csv_entry = Entry(self)
        csv_entry.grid(row=0, column=1, sticky=W)

        return csv_entry

    def browse_csv(self):
        """
        Open a file search dialog window to search for the csv file containing the results of the NDSI processing.
        :return: None
        """
        filename = filedialog.askopenfilename(initialdir=definitions.FILES_DIR, title="Select file containing the NDSI"
                                                                                      " results from the  processing.",
                                              filetypes=(("CSV files", "*.csv"),))
        self.set_input(filename, self.csv_entry)

    def get_input(self) -> str:
        """
        Gets the input from the csv entry and sets the global variable with it.
        :return: None
        """
        csv = self.csv_entry.get()

        return csv

    @staticmethod
    def validate_input(csv) -> bool:
        filename, file_extension = os.path.splitext(csv)

        if not os.path.isfile(csv):
            print("The input is not a file.")
            return False
        elif file_extension != '.csv':
            print("The input file is not a csv file.")
            return False

        return True

    def start_displaying(self):
        csv = self.get_input()

        if self.validate_input(csv=csv):
            displayer = plot.Plot(csv=csv)
            displayer.start()

    @staticmethod
    def set_input(text, entry) -> None:
        """
        Sets input for an entry.
        :param text: Text which will be the input.
        :param entry: The entry which represents the input box.
        :return: None
        """
        entry.delete(0, END)
        entry.insert(0, text)
