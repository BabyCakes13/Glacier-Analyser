"""
Class which handles the main view of the GUI.
"""
from tkinter import *
import sys

sys.path.append(sys.path[0] + '/..')
from data_displaying import frame_process as fp, frame_download as fdw, frame_display as fds


class MainView(Frame):
    """
    Main frame class.
    """
    def __init__(self, *args, **kwargs):
        """
        Set the button frame and the container frame for the Main frame.
        :param args: Any arguments
        :param kwargs: Aby arguments
        """
        Frame.__init__(self, *args, **kwargs)
        self.download = fdw.FrameDownload(self)
        self.process = fp.FrameProcess(self)
        self.display = fds.FrameDisplay(self)

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
        button_frame.configure(background='#b0b0b0')
        b1 = Button(button_frame, text="DOWNLOAD", command=self.download.lift, padx=15, pady=15)
        b2 = Button(button_frame, text="PROCESS", command=self.process.lift, padx=15, pady=15)
        b3 = Button(button_frame, text="DISPLAY", command=self.display.lift, padx=15, pady=15)

        b1.pack(side="left", padx=5, pady=5, expand=True)
        b2.pack(side="left", padx=5, pady=5, expand=True)
        b3.pack(side="left", padx=5, pady=5, expand=True)

    def create_container(self) -> None:
        """
        Create the container for the Main page which hold all the other frames.
        :return: None
        """
        container_frame = Frame(self)
        container_frame.configure(background='#e0e0e0')
        container_frame.place(relx=.5, rely=.5, anchor="c")
        container_frame.pack(side="top", fill="both", expand=True)

        self.download.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)
        self.process.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)
        self.display.place(in_=container_frame, x=0, y=0, relwidth=1, relheight=1)


def center_frame(master) -> None:
    """
    Position to the center of the screen.
    :param master: The tkinter root.
    :return: None
    """
    w = 560  # width for the Tk root
    h = 250  # height for the Tk root

    ws = master.winfo_screenwidth()  # width of the screen
    hs = master.winfo_screenheight()  # height of the screen

    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    master.geometry('%dx%d+%d+%d' % (w, h, x, y))


def start():
    """
    Starting point of the GUI.
    :return: None
    """
    master = Tk()
    master.title('Satellite Glacier Images Analyzer')
    master.resizable(False, False)
    master.configure(background='black')
    main = MainView(master)
    center_frame(master)
    main.pack(side="top", fill="both", expand=True)
    master.mainloop()
