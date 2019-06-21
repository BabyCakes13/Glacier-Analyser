from tkinter import *
from tkinter import filedialog


class StartPage:
    def __init__(self):
        self.master = Tk()
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.title("Start Page")

        self.center_window()
        self.create_labels()
        self.create_buttons()

    def create_labels(self):
        Label(self.master, text="Please select one of the following options.").grid(row=0, column=0,
                                                                                    sticky=N + S + E + W)

    def create_buttons(self):
        download = Button(self.master, text="DOWNLOAD", command=self.create_download_window)
        process = Button(self.master, text="PROCESS", command=self.create_process_window)
        display = Button(self.master, text="DISPLAY", command=self.create_display_window)

        download.grid(row=1, column=0, sticky=N + S + E + W)
        process.grid(row=2, column=0, sticky=N + S + E + W)
        display.grid(row=3, column=0, sticky=N + S + E + W)

    def center_window(self):
        """
        Centers window to the middle of the screen.
        :return: None
        """
        windowWidth = self.master.winfo_reqwidth()
        windowHeight = self.master.winfo_reqheight()

        positionRight = int(self.master.winfo_screenwidth() / 2 - windowWidth / 2)
        positionDown = int(self.master.winfo_screenheight() / 2 - windowHeight / 2)

        self.master.geometry("+{}+{}".format(positionRight, positionDown))

    def create_download_window(self):
        new_window = Toplevel(self.master)
        app = DownloadPage(new_window)

    def create_process_window(self):
        new_window = Toplevel(self.master)
        app = ProcessPage(new_window)

    def create_display_window(self):
        new_window = Toplevel(self.master)
        app = DisplayPage(new_window)

    def start_looping(self):
        self.master.mainloop()


class DownloadPage():
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master).grid(row=0, column=0)

        self.create_labels()
        self.create_buttons()
        self.create_entry()

    def create_buttons(self):
        Button(self.frame, text='Quit', width=25, command=self.close_windows)

    def create_labels(self):
        csv = Label(self.frame, text="Path to the CSV file containing the glacier information.")
        output_dir = Label(self.frame, text="Path to the directory which will contain the downloaded data.")

        csv.grid(row=0, column=0)
        output_dir.grid(row=2, column=0)

    def create_entry(self):
        csv = Entry(self.frame)
        output_dir = Entry(self.frame)

        csv.grid(row=1, column=0)
        output_dir.grid(row=4, column=0)

    def close_windows(self):
        self.master.destroy()


class ProcessPage:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)

        self.create_labels()
        self.create_buttons()
        self.create_entry()

        self.frame.pack()

    def create_buttons(self):
        Button(self.frame, text='Quit', width=25, command=self.close_windows).pack()

    def create_labels(self):
        csv = Label(self.frame, text="Path to the CSV file containing the glacier information.")
        output_dir = Label(self.frame, text="Path to the directory which will contain the downloaded data.")

        csv.pack(side=LEFT)
        output_dir.pack(side=LEFT)

    def create_entry(self):
        csv = Entry(self.frame)
        output_dir = Entry(self.frame)

        csv.pack(side=RIGHT)
        output_dir.pack(side=RIGHT)

    def close_windows(self):
        self.master.destroy()


class DisplayPage:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)

        self.create_labels()
        self.create_buttons()
        self.create_entry()

        self.frame.pack()

    def create_buttons(self):
        Button(self.frame, text='Quit', width=25, command=self.close_windows).pack()

    def create_labels(self):
        csv = Label(self.frame, text="Path to the CSV file containing the glacier information.")
        output_dir = Label(self.frame, text="Path to the directory which will contain the downloaded data.")

        csv.pack(side=LEFT)
        output_dir.pack(side=LEFT)

    def create_entry(self):
        csv = Entry(self.frame)
        output_dir = Entry(self.frame)

        csv.pack(side=RIGHT)
        output_dir.pack(side=RIGHT)

    def close_windows(self):
        self.master.destroy()


# download
NDSI_CSV = None
DOWNLOAD_DIR = None

# process
INPUT_DIR = None
OUTPUT_DIR = None

# display
NDSI_CSV = None


class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class Download(Page):
    """
    Download page class.
    """

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

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

    def get_input(self):
        """
        Gets the text which is set in the entries.
        :param entries: CSV and output directory entries.
        :return: None
        """
        global NDSI_CSV, DOWNLOAD_DIR
        NDSI_CSV = self.csv_entry.get()
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


class Process(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

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


class Display(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.create_labels()
        self.create_buttons()

        self.csv_entry = self.create_entries()

    def create_buttons(self):
        """
        Button creator.
        :return:
        """
        submit = Button(self, text="SUBMIT", command=self.get_input)
        submit.grid(row=7, column=0)

        browse = Button(self, text="BROWSE NDSI CSV", command=self.browse_csv)
        browse.grid(row=2, column=0)

        # TODO show how many files have been processed till now and show loading button which finishes when it is done.

    def create_labels(self):
        """
        Label creator.
        :return:
        """
        csv = Label(self, text="Path to the NDSI CSV results from the processing.")
        csv.grid(row=0, column=0)

    def create_entries(self):
        """
        Creates entries as input fields.
        :return:
        """
        csv_entry = Entry(self)
        csv_entry.grid(row=1, column=0)
        return csv_entry

    def browse_csv(self):
        """
        Search for the csv file which contains glacier download data.
        :return: The path to the csv glacier inventory.
        """
        filename = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("CSV files", "*.csv"),))
        self.set_input(filename, self.csv_entry)

    def get_input(self):
        global NDSI_CSV
        NDSI_CSV = self.csv_entry.get()

    @staticmethod
    def set_input(text, entry):
        entry.delete(0, END)
        entry.insert(0, text)


class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.download = Download(self)
        self.process = Process(self)
        self.display = Display(self)

        # call first so it it placed at top
        self.create_buttons()
        self.create_container()

    def create_buttons(self):
        button_frame = Frame(self)
        button_frame.pack(side="top", fill="x", expand=False)

        b1 = Button(button_frame, text="DOWNLOAD", command=self.download.lift)
        b2 = Button(button_frame, text="PROCESS", command=self.process.lift)
        b3 = Button(button_frame, text="DISPLAY", command=self.display.lift)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")

    def create_container(self):
        container_frame = Frame(self)
        container_frame.pack(side="top", fill="both", expand=True)

        self.download.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)
        self.process.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)
        self.display.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    root = Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("600x600")
    root.mainloop()
