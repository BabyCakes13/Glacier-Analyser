"""
The module has contains the superclass which handles frame creation.
"""
from tkinter import *


class Page(Frame):
    """
    Class which handles download, display and process frame creation as subclasses.
    """
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

    def show(self):
        """
        Show the frames.
        :return:
        """
        self.lift()

