import customtkinter as ctk
from pyrftl.gui.helpbox import HelpWindowMain
import tkinter


class Frame(ctk.CTkFrame):
    # frame with a textbox which show some details of the optical model, and allow to modify it
    def __init__(self, master, new_frame=False, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, **kwargs)

        if new_frame:
            self.frame = ctk.CTkFrame(master)
            self.frame.pack(fill=tkinter.BOTH, expand=True)

        else:
            self.frame = master

        if hasattr(master, 'font'):
            self.font = master.font
            self.font.weight = "normal"
        else:
            self.font = ctk.CTkFont(size=15, weight="normal")

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)
