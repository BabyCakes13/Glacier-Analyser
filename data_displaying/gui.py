from tkinter import *

sys.path.append(sys.path[0] + '/..')
from data_displaying import frame_process as fp, frame_download as fdw, frame_display as fds


class MainView(Frame):
    def __init__(self, *args, **kwargs):
        """
        Set the button frame and the container frame for the Main frame.
        :param args: Any arguments
        :param kwargs: Aby arguments
        """
        Frame.__init__(self, *args, **kwargs)
        self.download = fdw.Download(self)
        self.process = fp.Process(self)
        self.display = fds.Display(self)

        # call first so it it placed at top
        self.create_buttons()
        self.create_container()

    def create_buttons(self) -> None:
        """
        Create buttons for the Main frame.
        :return: None
        """
        button_frame = Frame(self)
        button_frame.place(relx=.5, rely=.5, anchor="c")
        button_frame.pack(side="top", fill="x", expand=False)

        b1 = Button(button_frame, text="DOWNLOAD", command=self.download.lift, padx=15, pady=15)
        b2 = Button(button_frame, text="PROCESS", command=self.process.lift, padx=15, pady=15)
        b3 = Button(button_frame, text="DISPLAY", command=self.display.lift, padx=15, pady=15)

        b1.pack(side="left", padx=10, pady=10)
        b2.pack(side="left", padx=10, pady=10)
        b3.pack(side="left", padx=10, pady=10)

    def create_container(self) -> None:
        """
        Create the container for the Main page which hold all the other frames.
        :return: None
        """
        container_frame = Frame(self)
        container_frame.place(relx=.5, rely=.5, anchor="c")
        container_frame.pack(side="top", fill="both", expand=True)

        self.download.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)
        self.process.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)
        self.display.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)


def position_master(master):
    w = 500  # width for the Tk root
    h = 300  # height for the Tk root

    ws = master.winfo_screenwidth()  # width of the screen
    hs = master.winfo_screenheight()  # height of the screen

    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    master.geometry('%dx%d+%d+%d' % (w, h, x, y))


def start():
    master = Tk()
    main = MainView(master)
    position_master(master)
    main.pack(side="top", fill="both", expand=True)
    master.mainloop()
