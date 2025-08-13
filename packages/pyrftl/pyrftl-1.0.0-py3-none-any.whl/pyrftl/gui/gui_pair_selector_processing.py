import time
import tkinter
import customtkinter as ctk
import os.path
from queue import Queue

from PIL import Image
import threading

from pyrftl.gui.helpbox import HelpWindowMain, create_help_box
from pyrftl.select_pair_successive import select_pair
from pyrftl.gui.gui_pair_display import PairDfDetail


class PairSelectorProcessing(ctk.CTkFrame):
    def __init__(self, master, param, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, **kwargs)

        # delete previous frame
        if hasattr(master, 'main_frame'):
            master.main_frame.destroy()

        # create a main frame
        master.main_frame = ctk.CTkFrame(master, fg_color="transparent")
        master.main_frame.pack(fill=tkinter.BOTH, expand=True)

        self.main_frame = master.main_frame

        if hasattr(master, 'font'):
            font = master.font
        else:
            font = ctk.CTkFont(size=15, weight="bold")

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)

        self.label_1 = ctk.CTkLabel(self.main_frame, font=font, text="Processing...")
        self.label_1.grid(row=0, column=0, columnspan=1, padx=(10, 10), pady=7)

        self.progressbar_1 = ctk.CTkProgressBar(self.main_frame)
        self.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1.start()

        # create a separate thread to run the pair selector function without freezing graphical interface
        result_queue = Queue() # queue to get the result

        thread_select_pair = threading.Thread(target=thread_function, args=(param, result_queue))
        thread_select_pair.start()

        while thread_select_pair.is_alive() :
            time.sleep(0.1)
            self.update()

        result = result_queue.get()
        thread_select_pair.join()

        pair_dataframe, pair_dict, lenses_list = result

        if pair_dataframe is not None :
            # more pair than 0
            PairDfDetail(master, pair_dataframe, pair_dict, lenses_list, param,
                           help_window=self.help_window)

        else:
            # delete previous frame
            if hasattr(master, 'main_frame'):
                master.main_frame.destroy()

            # create a main frame
            master.main_frame = ctk.CTkFrame(master, fg_color="transparent")
            master.main_frame.pack(fill=tkinter.BOTH, expand=True)

            self.main_frame = master.main_frame

            self.label_end_nothing1 = ctk.CTkLabel(self.main_frame, font=font, text="No pair has been selected !")
            self.label_end_nothing1.grid(row=0, column=0, columnspan=1, padx=(10, 10), pady=7)

            self.label_end_nothing2 = ctk.CTkLabel(self.main_frame, font=font,
                                                   text="You should add more lenses or change your criteria.")
            self.label_end_nothing2.grid(row=2, column=0, columnspan=1, padx=(10, 10), pady=7)


def thread_function(param, result_queue):
    result = select_pair(param)
    result_queue.put(result)


