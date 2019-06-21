from tkinter import *
from tkinter import filedialog

sys.path.append(sys.path[0] + '/..')
from data_displaying import page as fh


class Process(fh.Page):
    def __init__(self, *args, **kwargs):
        fh.Page.__init__(self, *args, **kwargs)

        self.create_buttons()
        self.create_labels()

        self.input_entry, self.output_entry = self.create_entries()

    def create_buttons(self):
        """
        Button creator.
        :return:
        """
        submit = Button(self, text="SUBMIT", command=self.get_input)
        submit.grid(row=7, column=0)

        browse = Button(self, text="BROWSE INPUT DIRECTORY", command=self.browse_input_directory)
        browse.grid(row=2, column=0)

        browse = Button(self, text="BROWSE OUTPUT DIRECTORY", command=self.browse_output_directory)
        browse.grid(row=5, column=0)

        # TODO show how many files have been processed till now and show loading button which finishes when it is done.

    def create_labels(self):
        """
        Label creator.
        :return:
        """
        input_dir = Label(self, text="Path to the directory which contains the images.")
        output_dir = Label(self, text="Path to the directory which will contain the result images after processing.")

        input_dir.grid(row=0, column=0)
        output_dir.grid(row=3, column=0)

    def create_entries(self):
        """
        Creates entries as input fields.
        :return:
        """
        input_entry = Entry(self)
        output_entry = Entry(self)

        input_entry.grid(row=1, column=0)
        output_entry.grid(row=4, column=0)

        return input_entry, output_entry

    def browse_input_directory(self):
        filename = filedialog.askdirectory(initialdir="/", title="Select directory for input data.")
        self.set_input(filename, self.input_entry)

    def browse_output_directory(self):
        filename = filedialog.askdirectory(initialdir="/", title="Select directory for output data.")
        self.set_input(filename, self.output_entry)

    def get_input(self):
        global INPUT_DIR, OUTPUT_DIR
        INPUT_DIR = self.input_entry.get()
        OUTPUT_DIR = self.output_entry.get()

    @staticmethod
    def set_input(text, entry):
        entry.delete(0, END)
        entry.insert(0, text)
