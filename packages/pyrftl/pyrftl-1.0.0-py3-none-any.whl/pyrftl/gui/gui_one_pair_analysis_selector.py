import tkinter
import customtkinter as ctk
import os.path
import time

try:
    import psutil
except:
    pass

from pyrftl.gui.helpbox import HelpWindowMain
from pyrftl.gui.gui_pair_selector import EflPupilCutoffTab, WavelengthFrame, PairConfigFrame, DistanceBeforePairFrame
from pyrftl.gui.gui_pair_display import PairOneDetail
from pyrftl.func.one_specific_pair_analysis import analyse_one_pair


class OnePairAnalysisParameters(ctk.CTkFrame):
    def __init__(self, master, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, **kwargs)

        # delete previous frame
        if hasattr(master, 'main_frame'):
            master.main_frame.destroy()

        # create a main frame
        master.main_frame = ctk.CTkFrame(master, fg_color="transparent")
        master.main_frame.pack(fill=tkinter.BOTH, expand=True)

        self.main_frame1 = master.main_frame

        self.main_frame = ctk.CTkScrollableFrame(self.main_frame1, fg_color="transparent")
        # if directly scrollable frame in master, it will not be well destroyed when master.main_frame is destroyed to
        # change the frame...
        self.main_frame.pack(fill=tkinter.BOTH, expand=True)

        if hasattr(master, 'font'):
            font = master.font
        else:
            font = ctk.CTkFont(size=15, weight="bold")

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)

        # input data from the user
        self.title_textbox = ctk.CTkTextbox(self.main_frame, wrap="word", font=font, width=200, height=60,
                                            fg_color="transparent")
        self.title_textbox.grid(row=0, column=0, columnspan=3, padx=0, pady=(5, 10), sticky='w')
        text = ("One pair analysis\n"
                "please fill parameters")
        self.title_textbox.insert("0.0", text)
        self.title_textbox.configure(state="disabled")  # configure textbox to be read-only
        self.text_title_textbox_help = ("Creates and analyses one pair of lenses, based on two (or one) lens files.\n"
                                        "Analysis is based on first-order parameters (ffl, bfl, efl, etc) and on "
                                        "RMS wavefront error. The lens pair is designed to be used as a tube lens for an infinity "
                                        "corrected microscope objective. It focuses an object at infinity onto a real image plane.")
        self.button_title_textbox_help = ctk.CTkButton(self.main_frame, text="?", width=20, height=20, font=font,
                                                       command=lambda: self.help_window.create_help_box(
                                                           self.text_title_textbox_help))
        self.button_title_textbox_help.grid(row=0, column=3, padx=(0, 30), pady=20)

        self.lens_frame = ctk.CTkFrame(self.main_frame)
        self.lens_frame.grid(row=1, column=0, columnspan=8, padx=(10, 10), pady=10)
        self.lens_frame_obj = LensesParameterFrame(self.lens_frame, help_window=self.help_window)

        self.pair_frame = ctk.CTkFrame(self.main_frame)
        self.pair_frame.grid(row=2, column=0, columnspan=8, padx=(10, 10), pady=10, sticky='w')
        self.pair_frame_obj = PairParameterFrame(self.pair_frame, help_window=self.help_window)

        self.button_start = ctk.CTkButton(self.main_frame, text="Start analysis", command=self.start, font=font)
        self.button_start.grid(row=3, column=0, padx=30, pady=(10, 30), sticky='n')

        self.textbox_start_error = ctk.CTkTextbox(self.main_frame, wrap="word", font=font, width=600, height=100,
                                                  fg_color="transparent", text_color="red")
        self.textbox_start_error.grid(row=3, column=1, columnspan=7, padx=0, pady=(5, 10), sticky='w')
        self.textbox_start_error.configure(state="disabled")  # configure textbox to be read-only

    def start(self):
        # get fields values and check if they are of the right type
        [lenses_ok, lenses_error, lenses_param] = self.lens_frame_obj.get_values()
        [pair_ok, pair_error, param] = self.pair_frame_obj.get_values()

        if lenses_ok and pair_ok:
            param['LensFile1'] = lenses_param['LensFile1']
            param['LensFile2'] = lenses_param['LensFile2']
            param['check_air_gap'] = lenses_param['check_air_gap']
            param['delete_air_gap'] = lenses_param['delete_air_gap']
            param['start_time'] = time.time()

            param['save_ram'] = 'no'
            param['nbRays_first_comparison'] = param['nbRays_high_comparison'] = param['grid']

            self.main_frame.destroy()
            self.main_frame = ctk.CTkFrame(self.main_frame1, fg_color="transparent")
            self.wait_label = ctk.CTkLabel(self.main_frame, text="Processing, please wait...")
            self.wait_label.grid(row=0, column=0)
            self.update()

            pair, rms, cutoff = analyse_one_pair(param)
            PairOneDetail(self.master, pair, param, help_window=self.help_window)

        else:
            error_txt = lenses_error + pair_error
            self.textbox_start_error.configure(state="normal")  # configure textbox to be modifiable
            self.textbox_start_error.delete("0.0", "end")  # delete all text
            self.textbox_start_error.insert("0.0", error_txt)  # add text
            self.textbox_start_error.configure(state="disabled")  # configure textbox to be read-only


class LensesParameterFrame(ctk.CTkFrame):
    def __init__(self, master, new_frame=False, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, **kwargs)

        if new_frame:
            self.frame = ctk.CTkFrame(master)
            self.frame.pack(fill=tkinter.BOTH, expand=True)

        else:
            self.frame = master

        if hasattr(master, 'font'):
            font = master.font
            font.weight = "normal"
        else:
            font = ctk.CTkFont(size=15, weight="normal")

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)

        pady1 = 7

        # give weight 0 to all columns, so they can have minimal size
        self.frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)

        self.textbox = ctk.CTkTextbox(self.frame, wrap="word", font=font, width=500, height=60, fg_color="transparent")
        self.textbox.grid(row=0, column=0, padx=0, pady=5, columnspan=5, sticky="w")
        text1 = ("Lenses import parameters\n"
                 "Lenses can be in format Zemax .zmx, CodeV .seq or RayOptics .roa")
        self.textbox.insert("0.0", text1)
        self.textbox.configure(state="disabled")  # configure textbox to be read-only

        # button, help and textbox Lens import
        self.textbox_file1 = ctk.CTkEntry(self.frame, font=font, width=700, height=40)
        self.textbox_file1.grid(row=1, column=2, columnspan=5, padx=10, pady=(5, 10))
        self.button_file1 = ctk.CTkButton(self.frame, text="Select lens 1 file",
                                          command=lambda:self.askfile(self.textbox_file1), font=font)
        self.button_file1.grid(row=1, column=0, padx=5, pady=pady1)
        self.text_folder_help = ("Select the file of each lens. Sequential model files need to "
                                 "be of type Zemax .zmx, CodeV .seq or RayOptics .roa. Files should have the "
                                 "extension in their name to be detected.")
        self.button_folder_help = ctk.CTkButton(self.frame, text="?", width=20, height=20, font=font,
                                                command=lambda: self.help_window.create_help_box(self.text_folder_help))
        self.button_folder_help.grid(row=1, column=1, padx=(0, 30), pady=pady1)

        self.textbox_file2 = ctk.CTkEntry(self.frame, font=font, width=700, height=40)
        self.textbox_file2.grid(row=2, column=2, columnspan=5, padx=10, pady=(5, 10))
        self.button_file2 = ctk.CTkButton(self.frame, text="Select lens 2 file",
                                          command=lambda:self.askfile(self.textbox_file2), font=font)
        self.button_file2.grid(row=2, column=0, padx=5, pady=pady1)

        self.switch_advanced_param = ctk.CTkSwitch(self.frame, text="Advanced parameters", font=font,
                                                   command=self.showhide_advanced_frame)
        self.switch_advanced_param.grid(row=3, column=0, padx=0, pady=pady1, sticky="w")
        self.switch_advanced_param.deselect()  # default : OFF

        self.advanced_param_frame = ctk.CTkFrame(self.frame)
        self.advanced_param_frame.grid(row=4, column=0, columnspan=6, padx=5, pady=pady1, sticky="w")
        self.advanced_param_frame.grid_remove()  # hide the frame by default

        self.checkbox_checkairgaps = ctk.CTkCheckBox(self.advanced_param_frame, text="check air gaps", font=font,
                                                     command=self.showhide_checkbox_delete)
        self.checkbox_checkairgaps.grid(row=0, column=0, padx=10, pady=pady1)
        self.checkbox_checkairgaps.select()  # default ON
        self.checkbox_deleteairgaps = ctk.CTkCheckBox(self.advanced_param_frame, text="delete air gaps", font=font)
        self.checkbox_deleteairgaps.grid(row=0, column=1, padx=10, pady=pady1)
        self.checkbox_deleteairgaps.deselect()  # default OFF

        self.advanced_param_frame.grid_columnconfigure(1, weight=1)  # keep always the column

        self.text_airgaps_help = ("If check air gaps is ON, imported files are checked for air gaps before and after the optical surfaces."
                                  " Indices of lens layers for further analysis are defined"
                                  " taking these air gaps into account.\n"
                                  "In case check air gaps is ON, it is possible to delete them when they exist, or not"
                                  " (but if the air gap exist for a good reason (for example a diaphragm) removing it "
                                  "can change lens parameters).")
        self.help_airgaps = ctk.CTkButton(self.advanced_param_frame, text="?", width=20, height=20, font=font,
                                          command=lambda: self.help_window.create_help_box(self.text_airgaps_help))
        self.help_airgaps.grid(row=0, column=2, padx=(0, 10), pady=pady1)

    def askfile(self, textbox):
        filepath = tkinter.filedialog.askopenfilename(filetypes=[("All accepted models", ".roa .seq .zmx"),
                                                                 ("RayOptics model", "*.roa"), ("CodeV model", "*.seq"),
                                                                 ("Zemax model", "*.zmx")])
        textbox.delete(0, "end")  # delete all text
        textbox.insert(0, filepath)  # add text

    def showhide_advanced_frame(self):
        # show or hide the frame with advanced parameters
        # get the switch state
        state = self.switch_advanced_param.get()
        if state == 0:  # OFF
            self.advanced_param_frame.grid_remove()  # hide the frame
        else:  # ON
            self.advanced_param_frame.grid()  # show the frame

    def showhide_checkbox_delete(self):
        # show or hide the frame with advanced parameters
        state = self.checkbox_checkairgaps.get()
        if state == 0:  # OFF
            self.checkbox_deleteairgaps.grid_remove()  # hide the frame
        else:  # ON
            self.checkbox_deleteairgaps.grid()  # show the frame

    def get_values(self):
        values = {'LensFile1': self.textbox_file1.get(),
                  'LensFile2': self.textbox_file2.get(),
                  'check_air_gap': self.checkbox_checkairgaps.get(),
                  'delete_air_gap': self.checkbox_deleteairgaps.get()}

        # initialisation
        everything_correct = True
        error_txt = ''

        # put back all borders well (see below)
        self.textbox_file1.configure(border_color=['#979DA2', '#565B5E'], border_width=0)
        self.textbox_file2.configure(border_color=['#979DA2', '#565B5E'], border_width=0)

        # check if everything is correct (and change wrong field appearance)
        if not os.path.isfile(values['LensFile1']):
            everything_correct = False
            error_txt = error_txt + "Lens 1 path do not exist or is not a file.\n"
            self.textbox_file1.configure(border_color='red', border_width=4)

        if values['LensFile2'] == '':
            values['LensFile2'] = None
        elif not os.path.isfile(values['LensFile2']):
            everything_correct = False
            error_txt = error_txt + "Lens 2 path do not exist or is not a file.\n"
            self.textbox_file2.configure(border_color='red', border_width=4)

        return [everything_correct, error_txt, values]


class PairParameterFrame(ctk.CTkFrame):
    def __init__(self, master, new_frame=False, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, **kwargs)

        if new_frame:
            self.frame = ctk.CTkFrame(master)
            self.frame.pack(fill=tkinter.BOTH, expand=True)

        else:
            self.frame = master

        if hasattr(master, 'font'):
            font = master.font
            font.weight = "normal"
        else:
            font = ctk.CTkFont(size=15, weight="normal")

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)

        pady1 = 7

        ################## pupil and cut off angle ##################
        # create frame
        self.efl_pupil_cutoff_frame = ctk.CTkFrame(self.frame)
        self.efl_pupil_cutoff_frame.grid(row=0, column=0, columnspan=8, padx=(10, 10), pady=pady1)
        self.efl_pupil_cutoff_frame.font = font
        # instructions & helpbox
        self.efl_pupil_cutoff_label = ctk.CTkLabel(self.efl_pupil_cutoff_frame, font=font,
                                                   text=("Select below effective focal length, entrance pupil diameter "
                                                         "and cut-off angle parameters for the tube lens."))
        self.efl_pupil_cutoff_label.grid(row=0, column=0, padx=(10, 10), pady=pady1)

        self.text_efl_pupil_cutoff_help = (
            "You need to enter below the desire effective focal length of the desire tube"
            " lens, its entrance pupil diameter (diameter of the entering field) as well "
            "as its maximum field angle (maximum angle that the entering field can have,"
            " and should pass the tube lens). You can directly enter theses values, or "
            "give your objectives properties.\n\n"
            "Remote refocus is when you have a system like the one of Botcherby 2007. "
            "Only one objective, is when you want a tube lens for a specific infinity"
            " corrected objective, without being in an optical remote refocusing system.\n\n"
            "In the case of remote refocusing, the desired tube length is TL2.\n\n"
            "All distances are in mm."
            )
        self.button_efl_pupil_cutoff_help = ctk.CTkButton(self.efl_pupil_cutoff_frame, text="?", width=20, height=20,
                                                          font=font,
                                                          command=lambda: self.help_window.create_help_box(
                                                              self.text_efl_pupil_cutoff_help))
        self.button_efl_pupil_cutoff_help.grid(row=0, column=1, padx=(0, 30), pady=pady1)

        self.efl_pupil_cutoff_tab = EflPupilCutoffTab(self.efl_pupil_cutoff_frame, help_window=self.help_window,
                                                      fg_color="transparent", height=100)
        self.efl_pupil_cutoff_tab.grid(row=1, column=0, columnspan=8, padx=(10, 10), pady=pady1)

        ################## wavelength ##################
        self.wvl_frame = ctk.CTkFrame(self.frame)
        self.wvl_frame.grid(row=1, column=0, columnspan=1, padx=(10, 10), pady=pady1, sticky='w')
        self.wvl_frame_class = WavelengthFrame(self.wvl_frame, help_window=help_window)

        ################## config ##################
        self.config_frame = ctk.CTkFrame(self.frame)
        self.config_frame.grid(row=1, column=1, columnspan=8, padx=(10, 10), pady=pady1, sticky='w')
        self.config_frame_class = PairConfigFrame(self.config_frame, help_window=self.help_window, only_one=True)

        ################## distance entering field to pair ##################
        self.distance_frame = ctk.CTkFrame(self.frame)
        self.distance_obj = DistanceBeforePairFrame(self.distance_frame, help_window=help_window)
        self.distance_frame.grid(row=2, column=0, columnspan=6, padx=5, pady=7, sticky="w")

        ################## computing settings ##################
        self.computing_param_frame = ctk.CTkFrame(self.frame)
        self.computing_param_frame.grid(row=5, column=0, columnspan=6, padx=20, pady=15, sticky="w")

        self.computing_frame_class = ComputingSettings(self.computing_param_frame, help_window=self.help_window)

    def get_values(self):
        wvl_ok, wvl_txt, wvl_and_weight = self.wvl_frame_class.get_values()
        tl_design_ok, tl_design_txt, tl_design_values = self.efl_pupil_cutoff_tab.get_values()
        config_ok, config_txt, configs = self.config_frame_class.get_values()
        dist_ok, dist_txt, dist_values = self.distance_obj.get_values()
        computing_ok, computing_txt, computing_values = self.computing_frame_class.get_values()

        everything_correct = wvl_ok and tl_design_ok and config_ok and dist_ok and computing_ok
        error_txt = wvl_txt + tl_design_txt + config_txt + dist_txt + computing_txt

        param0 = {'expected_focal_length': tl_design_values['expected_focal_length'],
                  'pupil': tl_design_values['pupil'],
                  'cut_off_angle_min': tl_design_values['cut_off_angle_min'],
                  'wvl_and_weight': wvl_and_weight,
                  'config': configs,
                  'dist_pupil_pair': dist_values['dist_pupil_pair'],
                  'cut_off_angle_test_end': computing_values['cut_off_angle_test_end'],
                  'cut_off_angle_precision': computing_values['cut_off_angle_precision'],
                  'best_focus_fast': computing_values['best_focus_fast'],
                  'grid': computing_values['grid'],
                  'focus_polychromatic': computing_values['focus_polychromatic'],
                  'polychromatic': computing_values['polychromatic']}

        return [everything_correct, error_txt, param0]


class ComputingSettings(ctk.CTkFrame):
    def __init__(self, master, new_frame=False, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, **kwargs)

        if new_frame:
            self.frame = ctk.CTkFrame(master)
            self.frame.pack(fill=tkinter.BOTH, expand=True)

        else:
            self.frame = master

        if hasattr(master, 'font'):
            font = master.font
            font.weight = "normal"
        else:
            font = ctk.CTkFont(size=15, weight="normal")

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)


        # help
        self.text_help = ("The cut-off angle is the maximum field angle which will be able"
                          " to enter in the pair."
                          " By default, the cut-off angle determination stop when the entering "
                          "angle is higher than 45° (if the needed cut-off angle defined above is < 35°, it is "
                          "2*minimal_cut_off_angle in other cases.) "
                          "That means that if the cut-off angle is higher than this value, it will"
                          " be shown as this value. It is possible to change the maximum value to determine for the "
                          "cut-off angle. In all cases, it should be higher than the cut-off angle needed for the pair, "
                          "defined before. It is possible to change the precision of the cut-off angle determination "
                          "(better precision will increase computing time)."
                          "\n\n"
                          "For wavefront analysis, the RMS will be determined for the field at the cut-off angle. "
                          "If best focus wavefront is ON, the image plane position is at the position which "
                          "minimize the 0° field RMS wavefront error. If it is OFF, the image distance is the pair back"
                          " focal length."
                          )
        self.help = ctk.CTkButton(self.frame, text="?", width=20, height=20, font=font,
                                  command=lambda: self.help_window.create_help_box(self.text_help))
        self.help.grid(row=0, column=0, padx=(0, 10), pady=7)


        # wavefront analysis - type
        self.label_wvf_poly_rms_formula = ctk.CTkLabel(master=self.frame, font=font, text="Polychromatic RMS formula")
        self.label_wvf_poly_rms_formula.grid(row=3, column=2, padx=(20, 0), pady=30, sticky='e')

        self.optionmenu_wvf_poly_rms_formula = ctk.CTkOptionMenu(self.frame, font=font,
                                                                 values=["rms", "worst"])
        self.optionmenu_wvf_poly_rms_formula.grid(row=3, column=3, columnspan=2, padx=10, pady=7, sticky='w')
        self.optionmenu_wvf_poly_rms_formula.set("rms")

        self.checkbox_best_focus_wvf = ctk.CTkCheckBox(self.frame, font=font,
                                                       command=self.activate_deactivate_focuspoly,
                                                       text="Best focus wavefront 0°")
        self.checkbox_best_focus_wvf.grid(row=4, column=0, columnspan=2, padx=10, pady=7)
        self.checkbox_best_focus_wvf.select()  # default ON

        self.label_wvf_focuspoly = ctk.CTkLabel(master=self.frame, font=font, text="Best focus polychromatic")
        self.label_wvf_focuspoly.grid(row=4, column=2, padx=(20, 0), pady=30, sticky='e')

        self.optionmenu_wvf_focuspoly = ctk.CTkOptionMenu(self.frame, font=font,
                                                          values=["reference wavelength", "rms"])
        self.optionmenu_wvf_focuspoly.grid(row=4, column=3, columnspan=2, padx=10, pady=7, sticky='w')
        self.optionmenu_wvf_focuspoly.set("reference wavelength")

        # wavefront analysis - nb rays
        self.label_nbrays = ctk.CTkLabel(master=self.frame, font=font, text="Number of rays used for\n"
                                                                             "RMS wavefront error :")
        self.label_nbrays.grid(row=3, column=0, padx=(10, 0), pady=7, sticky='e')
        self.entry_nbrays = ctk.CTkEntry(self.frame, placeholder_text="64", font=font, width=60)
        self.entry_nbrays.grid(row=3, column=1, columnspan=1, padx=0, sticky='w')

        # cut-off angle
        self.label_cutoff_end = ctk.CTkLabel(master=self.frame, font=font, text="Cut-off angle test end [°] :")
        self.label_cutoff_end.grid(row=6, column=0, padx=(10, 0), pady=7, sticky='e')
        self.entry_cutoff_end = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=60)
        self.entry_cutoff_end.grid(row=6, column=1, columnspan=1, padx=0, sticky='w')

        self.label_cutoff_precision = ctk.CTkLabel(master=self.frame, font=font, text="Cut-off angle precision [°] :")
        self.label_cutoff_precision.grid(row=6, column=3, columnspan=2, padx=(10, 0), pady=20, sticky='e')
        self.entry_cutoff_precision = ctk.CTkEntry(self.frame, placeholder_text="0.1", font=font, width=60)
        self.entry_cutoff_precision.grid(row=6, column=5, columnspan=1, padx=0, sticky='w')

    def get_values(self):
        # this function check if all fields have the right type of values (int is int etc)
        # and return [everything_correct, error_txt, values]

        # obtain all fields
        values = {'best_focus_fast': self.checkbox_best_focus_wvf.get(),
                  'grid': self.entry_nbrays.get(),
                  'cut_off_angle_test_end': self.entry_cutoff_end.get(),
                  'cut_off_angle_precision': self.entry_cutoff_precision.get(),
                  'focus_polychromatic': self.optionmenu_wvf_focuspoly.get(),
                  'polychromatic': self.optionmenu_wvf_poly_rms_formula.get()}

        # initialisation
        everything_correct = True
        error_txt = ''

        # put back all borders well (see below)
        self.entry_nbrays.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_cutoff_end.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_cutoff_precision.configure(border_color=['#979DA2', '#565B5E'], border_width=2)

        # check if everything is correct (and change wrong field appearance)
        if values['grid'] == '':
            values['grid'] = 64
        else:
            try:
                values['grid'] = int(values['grid'])
            except:
                everything_correct = False
                error_txt = error_txt + "The ray grid size for RMS wavefront error should be an int or nothing.\n"
                self.entry_nbrays.configure(border_color='red', border_width=4)

        if values['cut_off_angle_test_end'] == '':
            values['cut_off_angle_test_end'] = None
        else:
            try:
                values['cut_off_angle_test_end'] = float(values['cut_off_angle_test_end'])

                if values['cut_off_angle_test_end'] < 0 :
                    everything_correct = False
                    error_txt = error_txt + "The maximum tested cut-off angle should be positive.\n"
                    self.entry_cutoff_end.configure(border_color='red', border_width=4)
            except:
                everything_correct = False
                error_txt = error_txt + "The maximum tested cut-off angle should be a float or nothing.\n"
                self.entry_cutoff_end.configure(border_color='red', border_width=4)

        if values['cut_off_angle_precision'] == '':
            values['cut_off_angle_precision'] = 0.1
        else:
            try:
                values['cut_off_angle_precision'] = float(values['cut_off_angle_precision'])

                if values['cut_off_angle_precision'] < 0 :
                    everything_correct = False
                    error_txt = error_txt + "The precision for cut-off angle should be positive.\n"
                    self.entry_cutoff_precision.configure(border_color='red', border_width=4)
            except:
                everything_correct = False
                error_txt = error_txt + "The precision for cut-off angle should be a float or nothing.\n"
                self.entry_cutoff_precision.configure(border_color='red', border_width=4)

        match values['focus_polychromatic'] :
            case 'reference wavelength' :
                values['focus_polychromatic'] = 'ref_wvl_i'
            case "rms":
                values['focus_polychromatic'] = 'rmse_rms'
            case _ :
                pass

        match values['polychromatic'] :
            case "rms":
                values['polychromatic'] = 'rmse_rms'
            case _ :
                pass

        return [everything_correct, error_txt, values]

    def activate_deactivate_focuspoly(self):
        if self.checkbox_best_focus_wvf.get() :
            self.optionmenu_wvf_focuspoly.configure(state="normal")
        else:
            self.optionmenu_wvf_focuspoly.configure(state="disabled")

