import tkinter
import customtkinter as ctk

from pyrftl.gui.gui_pair_selector import PairSelectorParameters
from pyrftl.gui.gui_one_pair_analysis_selector import OnePairAnalysisParameters
from pyrftl.gui.helpbox import HelpWindowMain
from pyrftl.gui.gui_roa_file import RoaFileSelect


class App(ctk.CTk):
    # main app for the gui
    def __init__(self, scaling=None):
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

        super().__init__()

        if scaling is not None:
            ctk.set_widget_scaling(scaling)

        # configure window
        self.title("PyRFTL gui")
        self.geometry(f"{1100}x{680}")

        # # create a base scrollable frame
        # self.masterframe = ctk.CTkScrollableFrame(self, fg_color=("#eaeaea", "black"))
        # self.masterframe.pack(fill=tkinter.BOTH, expand=True, side=tkinter.TOP)

        # create help object
        self.help_window = HelpWindowMain()

        # top frame
        # self.window_setting_frame = WindowSettingFrame(self.masterframe)
        self.window_setting_frame = WindowSettingFrame(self)

        # changing frame
        # self.changing_frame = ctk.CTkFrame(self.masterframe, fg_color="transparent")#("#eaeaea", "black"))#("lightgray", "black"))
        self.changing_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.changing_frame.pack(fill=tkinter.BOTH, expand=True, side=tkinter.BOTTOM)
        self.changing_frame.main_menu_frame = MainMenu(self.changing_frame, help_window=self.help_window)


class MainMenu(ctk.CTkFrame) :
    # first menu, to select what program to launch
    def __init__(self, master, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, **kwargs)

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


        # title
        self.logo_label = ctk.CTkLabel(self.main_frame, text="What are you interested in ?",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, columnspan=6, padx=30, pady=(10, 10))

        # button 1 and help
        self.button_pairselector = ctk.CTkButton(self.main_frame, text="pair selector", command=self.pair_selector,
                                                 font=font)
        self.button_pairselector.grid(row=1, column=0, padx=(20,5), pady=20)
        self.text_pairselector_help = ("Create and analyse pairs of lenses.\n"
                                       "Analysis is based on first-on parameters (ffl, bfl, efl, etc) and on "
                                       "RMS wavefront error.  The lens pair is designed to be used as a tube lens for an infinity "
                                        "corrected microscope objective. It focuses an object at infinity onto a real image plane.")
                                      
        self.button_pairselector_help = ctk.CTkButton(self.main_frame, text="?", width=20, height=20, font=font,
                                                      command=lambda:self.help_window.create_help_box(self.text_pairselector_help))
        self.button_pairselector_help.grid(row=1, column=1, padx=(0,30), pady=20)

        # button 2 and help
        self.button_onepair = ctk.CTkButton(self.main_frame, text="one pair analysis", command=self.one_pair, font=font)
        self.button_onepair.grid(row=1, column=2, padx=(20,5), pady=20)
        self.text_onepair_help = 'Analyse one pair of lenses.'
        self.button_onepair_help = ctk.CTkButton(self.main_frame, text="?", width=20, height=20, font=font,
                                                      command=lambda:self.help_window.create_help_box(self.text_onepair_help))
        self.button_onepair_help.grid(row=1, column=3, padx=(0,30), pady=20)

        # button 4 and help
        self.button_roa = ctk.CTkButton(self.main_frame, text="open roa files", command=self.open_roa, font=font)
        self.button_roa.grid(row=2, column=0, padx=(20,5), pady=20)
        self.text_roa_help = "Open optical model files from RayOptics (.roa files)."
        self.button_roa_help = ctk.CTkButton(self.main_frame, text="?", width=20, height=20, font=font,
                                                      command=lambda:self.help_window.create_help_box(self.text_roa_help))
        self.button_roa_help.grid(row=2, column=1, padx=(0,30), pady=20)

        # textbox for publication reference and git
        ads_txt = ("See project git at "
                   "https://gitlab.unistra.fr/opm_tools/pyrftl \n"
                   "and codeberg\n\n"
                   "This software is published at reference : DOI")

        self.textbox_ads = ctk.CTkTextbox(self.main_frame, wrap="word", width=500, height=300,
                                          font=font, fg_color="transparent")
        self.textbox_ads.grid(row=3, column=0, columnspan=4, padx=5, pady=(0,10), sticky="w")

        self.textbox_ads.insert("0.0", ads_txt)  # add text
        self.textbox_ads.configure(state="disabled")  # configure textbox to be read-only

    def pair_selector(self):
        PairSelectorParameters(self.master, help_window=self.help_window)

    def open_roa(self):
        # PairSelectorParameters(self.master, help_window=self.help_window)
        RoaFileSelect(self.master, self.help_window)

    def one_pair(self):
        OnePairAnalysisParameters(self.master, self.help_window)


class WindowSettingFrame(ctk.CTkFrame):
    # frame that will stay all time, to select UI scale and theme
    def __init__(self, master):
        super().__init__(master)

        self.master = master

        # create the frame
        self.window_setting_frame = ctk.CTkFrame(master,  corner_radius=0)
        self.window_setting_frame.pack(fill=tkinter.X, expand=False, side=tkinter.TOP)

        # name
        self.logo_label = ctk.CTkLabel(self.window_setting_frame, text="PyRFTL",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=30, pady=(10, 10))

        # button to change app theme
        self.appearance_mode_label = ctk.CTkLabel(self.window_setting_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=0, column=4, padx=0, pady=(0, 0))
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.window_setting_frame,
                                                            values=["Light", "Dark", "System"],
                                                            command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=0, column=5, padx=10, pady=(0, 0))

        # button to change scaling
        self.scaling_label = ctk.CTkLabel(self.window_setting_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=0, column=2, padx=0, pady=(0, 0))
        self.scaling_optionmenu = ctk.CTkOptionMenu(self.window_setting_frame,
                                                    values=["50%", "65%", "85%", "100%", "120%", "150%", "200%", "250%"],
                                                    command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=0, column=3, padx=10, pady=(0, 0))
        self.scaling_optionmenu.set("100%")

        # button for cancelling transparency when bug
        self.button_transparency = ctk.CTkButton(self.window_setting_frame, text="cancel transparency",
                                                 command=self.cancel_transparency)
        self.button_transparency.grid(row=0, column=6, padx=(20, 5), pady=0)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def cancel_transparency(self):
        self.master.attributes("-alpha", 1)


def pyrftl_gui():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    app = App()
    app.mainloop()


