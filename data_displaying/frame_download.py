from tkinter import *
from tkinter import filedialog

sys.path.append(sys.path[0] + '/..')
from data_displaying import page as fh


class Download(fh.Page):
    """
    Download page class.
    """

    def __init__(self, *args, **kwargs):
        fh.Page.__init__(self, *args, **kwargs)

        self.create_buttons()
        self.create_labels()

        self.csv_entry, self.download_dir_entry = self.create_entries()

    def create_buttons(self):
        """
        Button creator.
        :return:
        """
        submit = Button(self, text="SUBMIT", command=self.get_input)
        submit.grid(row=7, column=0)

        browse = Button(self, text="BROWSE CSV", command=self.browse_csv)
        browse.grid(row=2, column=0)

        browse = Button(self, text="BROWSE OUTPUT DIRECTORY", command=self.browse_output_directory)
        browse.grid(row=5, column=0)

    def create_labels(self):
        """
        Label creator.
        :return:
        """
        csv = Label(self, text="Path to the CSV file containing the glacier information.")
        output_dir = Label(self, text="Path to the directory which will contain the downloaded data.")

        csv.grid(row=0, column=0)
        output_dir.grid(row=3, column=0)

    def create_entries(self):
        """
        Creates entries as input fields.
        :return:
        """
        csv = Entry(self)
        output_dir = Entry(self)

        csv.grid(row=1, column=0)
        output_dir.grid(row=4, column=0)

        return csv, output_dir

    def browse_csv(self):
        """
        Search for the csv file which contains glacier download data.
        :return: The path to the csv glacier inventory.
        """
        filename = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("CSV files", "*.csv"),))
        self.set_input(filename, self.csv_entry)

    def browse_output_directory(self):
        """
        Search for the csv file which contains glacier download data.
        :return: The path to the csv glacier inventory.
        """
        filename = filedialog.askdirectory(initialdir="/", title="Select directory for download output.")
        self.set_input(filename, self.download_dir_entry)

    def get_input(self) -> None:
        """
        Gets the text which is set in the entries.
        :return: None
        """
        global DOWNLOAD_CSV, DOWNLOAD_DIR
        DOWNLOAD_CSV = self.csv_entry.get()
        DOWNLOAD_DIR = self.download_dir_entry.get()

    @staticmethod
    def set_input(text, entry):
        """
        Sets text in an entry.
        :param text:
        :param entry:
        :return:
        """
        entry.delete(0, END)
        entry.insert(0, text)
