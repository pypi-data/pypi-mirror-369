import tkinter
import customtkinter as ctk
import os.path

from PIL import Image
import psutil

import pyrftl.func.lens_selection as fls
from pyrftl.func.various_stuff import is_between
from pyrftl.func.save import create_save_folder
from pyrftl.gui.helpbox import HelpWindowMain
from pyrftl.gui.gui_pair_selector_processing import PairSelectorProcessing


class PairSelectorParameters(ctk.CTkFrame):
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
        # self.main_frame = ctk.CTkFrame(self.main_frame1, fg_color="transparent")
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
        text = ("Pair Selector\n"
                "please fill parameters")
        self.title_textbox.insert("0.0", text)
        self.title_textbox.configure(state="disabled")  # configure textbox to be read-only
        self.text_title_textbox_help = ("Create and analyse pairs of lenses.\n"
                                        "Analysis is based on first-order parameters (ffl, bfl, efl, etc) and on "
                                        "RMS wavefront error. The lens pair is designed to be used as a tube lens for an infinity "
                                        "corrected microscope objective. It focuses an object at infinity onto a real image plane."
                                        "\n\n"                                        
                                        "The analysis is done in the following way :\n"
                                        "   - two lenses are grouped in a pair\n"
                                        "   - a thin lens analysis is done, and pairs which do not satisfy geometrical "
                                        "criteria are rejected. (optional)\n"
                                        "   - a raytracing analysis is done, and pairs which do not satisfy geometrical "
                                        "criteria are rejected\n"
                                        "   - a first RMS wavefront error analysis is done\n"
                                        "   - a second RMS wavefront error analysis is done between best pairs. This "
                                        "analysis use a ray grid with more rays, in order to be more precise than the "
                                        "first analysis (but more rays means more computing time)."
                                        "\n\n"
                                        "On this page, you should first select the directory which contain the lenses to"
                                        " use. In order to save computing time, please remove all unnecessary lenses"
                                        " from the folder and its subfolders.\n"
                                        "Then you can specify the characteristics of the tube lens to generate.")
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
        self.button_start.grid(row=3, column=0, padx=30, pady=(10,30), sticky='n')

        self.textbox_start_error = ctk.CTkTextbox(self.main_frame, wrap="word", font=font, width=600, height=100,
                                                  fg_color="transparent", text_color="red")
        self.textbox_start_error.grid(row=3, column=1, columnspan=7, padx=0, pady=(5, 10), sticky='w')
        self.textbox_start_error.configure(state="disabled")  # configure textbox to be read-only

    def start(self):
        # get fields values and check if they are of the right type
        [lenses_ok, lenses_error, lenses_param] = self.lens_frame_obj.get_values()
        [pair_ok, pair_error, param] = self.pair_frame_obj.get_values()

        if lenses_ok and pair_ok:
            param['lenses_param'] = lenses_param

            try:
                complete_save_folder_path, analysis_name, t0 = create_save_folder(param['save_folder_path'],
                                                                                  param['analysis_name'])
                param['save_folder_path'] = complete_save_folder_path
                param['analysis_name'] = analysis_name
                param['start_time'] = t0

            except Exception as exception:
                error_txt = "Error while trying to create the working folder. Please change the saving directory path."
                self.textbox_start_error.configure(state="normal")  # configure textbox to be modifiable
                self.textbox_start_error.delete("0.0", "end")  # delete all text
                self.textbox_start_error.insert("0.0", error_txt)  # add text
                self.textbox_start_error.configure(state="disabled")  # configure textbox to be read-only
                return

            PairSelectorProcessing(self.master, param, self.help_window)  # execute only if no error while create the
                                                                          # save folder

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

        # give weight 0 to all columns so they can have minimal size
        self.frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)

        self.textbox = ctk.CTkTextbox(self.frame, wrap="word", font=font, width=500, height=60, fg_color="transparent")
        self.textbox.grid(row=0, column=0, padx=0, pady=5, columnspan=5, sticky="w")
        text1 = ("Lenses import parameters\n"
                 "Lenses can be in format Zemax .zmx, CodeV .seq or RayOptics .roa")
        self.textbox.insert("0.0", text1)
        self.textbox.configure(state="disabled")  # configure textbox to be read-only

        # button, help and textbox Lens import
        self.button_folder = ctk.CTkButton(self.frame, text="Select lenses directory", command=self.askdir, font=font)
        self.button_folder.grid(row=1, column=0, padx=5, pady=pady1)
        self.text_folder_help = ("Select the folder where lenses files are. Lenses can be in subfolders, they need to "
                                 "be of type Zemax .zmx, CodeV .seq or RayOptics .roa. Files should have the "
                                 "extension in their name to be detected.\n"
                                 "Please remove all unnecessary lenses of subfolders before importing the parent "
                                 "directory, since the more lenses present, the higher the computational cost.")
        self.button_folder_help = ctk.CTkButton(self.frame, text="?", width=20, height=20, font=font,
                                                command=lambda: self.help_window.create_help_box(self.text_folder_help))
        self.button_folder_help.grid(row=1, column=1, padx=(0, 30), pady=pady1)
        self.textbox_folder = ctk.CTkEntry(self.frame, font=font, width=700, height=40)
        self.textbox_folder.grid(row=1, column=2, columnspan=5, padx=10, pady=(5, 10))

        # lens diameter/efl
        self.label_diam_min = ctk.CTkLabel(self.frame, text="Diameter min [mm] :  ", font=font)
        self.label_diam_min.grid(row=2, column=0, padx=(5, 0), pady=pady1, sticky='e')
        self.entry_diam_min = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_diam_min.grid(row=2, column=1, columnspan=1, padx=0, pady=pady1)

        self.label_diam_max = ctk.CTkLabel(self.frame, text="Diameter max [mm] :  ", font=font)
        self.label_diam_max.grid(row=2, column=2, padx=5, pady=pady1, sticky="e")
        self.entry_diam_max = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_diam_max.grid(row=2, column=3, columnspan=1, padx=0, pady=pady1, sticky="w")

        self.text_diam_efl_help = ("These parameters are used to filter the imported lenses to use in the analysis."
                                   "They can be filled with a float or left empty. If a filter is empty, it will be "
                                   "ignored. All dimensions are in millimeter.\n"
                                   "Define maximum and minimum lenses diameter to use.\n"
                                   "Define maximum and minimum effective focal length of lenses to use.")
        self.help_diam_efl = ctk.CTkButton(self.frame, text="?", width=20, height=20, font=font,
                                           command=lambda: self.help_window.create_help_box(self.text_diam_efl_help))
        self.help_diam_efl.grid(row=2, column=4, padx=(0, 30), pady=pady1)

        self.label_efl_min = ctk.CTkLabel(self.frame, text="Effective focal\n length min [mm] :  ", font=font)
        self.label_efl_min.grid(row=3, column=0, padx=(5, 0), pady=pady1, sticky='e')
        self.entry_efl_min = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_efl_min.grid(row=3, column=1, columnspan=1, padx=0, pady=pady1)

        self.label_efl_max = ctk.CTkLabel(self.frame, text="Effective focal\n length max [mm] :  ", font=font)
        self.label_efl_max.grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.entry_efl_max = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_efl_max.grid(row=3, column=3, columnspan=1, padx=0, pady=pady1, sticky="w")

        self.switch_advanced_param = ctk.CTkSwitch(self.frame, text="Advanced parameters", font=font,
                                                   command=self.showhide_advanced_frame)
        self.switch_advanced_param.grid(row=3, column=4, padx=0, pady=pady1, sticky="w")
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

        self.text_airgaps_help = ("If check air gaps is ON, it is determined if some air gaps exist before and after "
                                  "lenses in imported files. Indices of lens layers for further analysis are defined"
                                  " taking these air gaps into account.\n"
                                  "In case check air gaps is ON, it is possible to delete them when they exist, or not"
                                  " (but if the air gap exist for a good reason (for example a diaphragm) removing it "
                                  "can change lens parameters).")
        self.help_airgaps = ctk.CTkButton(self.advanced_param_frame, text="?", width=20, height=20, font=font,
                                          command=lambda: self.help_window.create_help_box(self.text_airgaps_help))
        self.help_airgaps.grid(row=0, column=2, padx=(0, 10), pady=pady1)

    def askdir(self):
        dirpath = tkinter.filedialog.askdirectory()
        self.textbox_folder.delete(0, "end")  # delete all text
        self.textbox_folder.insert(0, dirpath)  # add text

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
        values = {'LensesFolderPath': self.textbox_folder.get(),
                  'check_air_gap': self.checkbox_checkairgaps.get(),
                  'delete_air_gap': self.checkbox_deleteairgaps.get(),
                  'lens_diameter_min': self.entry_diam_min.get(),
                  'lens_diameter_max': self.entry_diam_max.get(),
                  'lens_efl_min': self.entry_efl_min.get(),
                  'lens_efl_max': self.entry_efl_max.get()}

        # initialisation
        everything_correct = True
        error_txt = ''

        # put back all borders well (see below)
        self.textbox_folder.configure(border_color=['#979DA2', '#565B5E'], border_width=0)
        self.entry_diam_min.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_diam_max.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_efl_min.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_efl_max.configure(border_color=['#979DA2', '#565B5E'], border_width=2)

        # check if everything is correct (and change wrong field appearance)
        if not os.path.isdir(values['LensesFolderPath']):
            everything_correct = False
            error_txt = error_txt + "Directory of lenses is not a directory or path do not exist.\n"
            self.textbox_folder.configure(border_color='red', border_width=4)

        if values['lens_diameter_min'] == '':
            values['lens_diameter_min'] = None
        else:
            try:
                values['lens_diameter_min'] = float(values['lens_diameter_min'])
            except:
                everything_correct = False
                error_txt = error_txt + "The minimum lens diameter should be a float or nothing.\n"
                self.entry_diam_min.configure(border_color='red', border_width=4)

        if values['lens_diameter_max'] == '':
            values['lens_diameter_max'] = None
        else:
            try:
                values['lens_diameter_max'] = float(values['lens_diameter_max'])

                if everything_correct and (values['lens_diameter_min'] is not None) and (
                        values['lens_diameter_max'] < values['lens_diameter_min']):
                    everything_correct = False
                    error_txt = error_txt + "The maximum lens diameter should be superior to the minimum one.\n"
                    self.entry_diam_max.configure(border_color='red', border_width=4)
                    self.entry_diam_min.configure(border_color='red', border_width=4)
            except:
                everything_correct = False
                error_txt = error_txt + "The maximum lens diameter should be a float or nothing.\n"
                self.entry_diam_max.configure(border_color='red', border_width=4)

        if values['lens_efl_min'] == '':
            values['lens_efl_min'] = None
        else:
            try:
                values['lens_efl_min'] = float(values['lens_efl_min'])
            except:
                everything_correct = False
                error_txt = error_txt + "The minimum lens effective focal length should be a float or nothing.\n"
                self.entry_efl_min.configure(border_color='red', border_width=4)

        if values['lens_efl_max'] == '':
            values['lens_efl_max'] = None
        else:
            try:
                values['lens_efl_max'] = float(values['lens_efl_max'])

                if everything_correct and (values['lens_efl_min'] is not None) and (
                        values['lens_efl_max'] < values['lens_efl_min']):
                    everything_correct = False
                    error_txt = error_txt + ("The maximum lens effective focal length should be"
                                             " superior to the minimum one.\n")
                    self.entry_efl_min.configure(border_color='red', border_width=4)
                    self.entry_efl_max.configure(border_color='red', border_width=4)
            except:
                everything_correct = False
                error_txt = error_txt + "The maximum lens effective focal length should be a float or nothing.\n"
                self.entry_efl_max.configure(border_color='red', border_width=4)

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
            " and which should pass the tube lens). You can directly enter theses values or "
            "give your objectives properties.\n\n"
            "Remote refocus is when you have a system like the one of Botcherby et al. 2007. (doi:10.1364/OL.32.002007)"
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
        self.config_frame_class = PairConfigFrame(self.config_frame, help_window=self.help_window)

        ################## geometrical distances ##################
        self.geometry_frame = ctk.CTkFrame(self.frame)
        self.geometry_frame.grid(row=2, column=0, columnspan=8, padx=(10, 10), pady=pady1, sticky='w')
        self.geometry_frame_class = PairGeometryFrame(self.geometry_frame, help_window=self.help_window)

        ################## save folder ##################
        self.save_frame = ctk.CTkFrame(self.frame)
        self.save_frame.grid(row=3, column=0, columnspan=9, padx=(10, 10), pady=pady1, sticky='w')
        self.save_frame_class = PairSaveFrame(self.save_frame, help_window=self.help_window)

        ################## computing settings ##################
        self.switch_advanced_computing_param = ctk.CTkSwitch(self.frame, text="Advanced computing settings", font=font,
                                                             command=self.showhide_advanced_computing_frame)
        self.switch_advanced_computing_param.grid(row=4, column=0, padx=20, pady=pady1, sticky="w")
        self.switch_advanced_computing_param.deselect()  # default : OFF

        self.advanced_computing_param_frame = ctk.CTkFrame(self.frame)
        self.advanced_computing_param_frame.grid(row=5, column=0, columnspan=6, padx=20, pady=15, sticky="w")
        self.advanced_computing_param_frame.grid_remove()  # hide the frame by default

        self.advanced_computing_frame_class = AdvancedComputingSettings(self.advanced_computing_param_frame,
                                                                        help_window=self.help_window)

    def showhide_advanced_computing_frame(self):
        # show or hide the frame with advanced parameters
        # get the switch state
        state = self.switch_advanced_computing_param.get()
        if state == 0:  # OFF
            self.advanced_computing_param_frame.grid_remove()  # hide the frame
        else:  # ON
            self.advanced_computing_param_frame.grid()  # show the frame

    def get_values(self):
        wvl_ok, wvl_txt, wvl_and_weight = self.wvl_frame_class.get_values()
        tl_design_ok, tl_design_txt, tl_design_values = self.efl_pupil_cutoff_tab.get_values()
        config_ok, config_txt, configs = self.config_frame_class.get_values()
        dist_ok, dist_txt, dist_values = self.geometry_frame_class.get_values()
        save_ok, save_txt, save_values = self.save_frame_class.get_values()
        computing_ok, computing_txt, computing_values = self.advanced_computing_frame_class.get_values()

        everything_correct = wvl_ok and tl_design_ok and config_ok and dist_ok and save_ok and computing_ok
        error_txt = wvl_txt + tl_design_txt + config_txt + dist_txt + save_txt + computing_txt

        dist_criteria = dist_values['dist_criteria0']
        dist_criteria['tolerance_prcent'] = computing_values['tolerance_prcent']

        param0 = {'expected_focal_length': tl_design_values['expected_focal_length'],
                  'pupil': tl_design_values['pupil'],
                  'cut_off_angle_min': tl_design_values['cut_off_angle_min'],
                  'wvl_and_weight': wvl_and_weight,
                  'config': configs,
                  'dist_criteria': dist_criteria,
                  'dist_pupil_pair': dist_values['dist_pupil_pair'],
                  'save_folder_path': save_values['save_folder_path'],
                  'analysis_name': save_values['analysis_name'],
                  'output_csv': save_values['output_csv'],
                  'save_roa': save_values['save_roa'],
                  'save_seq_detail': save_values['save_seq_detail'],
                  'thin_lens_first_analysis': computing_values['thin_lens_first_analysis'],
                  'save_ram': computing_values['save_ram'],
                  'nb_subprocesses': computing_values['nb_subprocesses'],
                  'force_affinity_core': computing_values['force_affinity_core'],
                  'cut_off_angle_test_end': computing_values['cut_off_angle_test_end'],
                  'cut_off_angle_precision': computing_values['cut_off_angle_precision'],
                  'polychromatic': computing_values['polychromatic'],
                  'focus_polychromatic': computing_values['focus_polychromatic'],
                  'best_focus_fast': computing_values['best_focus_fast'],
                  'nbRays_first_comparison': computing_values['nbRays_first_comparison'],
                  'nbRays_high_comparison': computing_values['nbRays_high_comparison'],
                  'number_best_pair_high_comparison': computing_values['number_best_pair_high_comparison'],
                  'tolerance_wavefront_RMS_high_percent': computing_values['tolerance_wavefront_RMS_high_percent']}

        return [everything_correct, error_txt, param0]


class WavelengthFrame(ctk.CTkFrame):
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

        self.wvl_label = ctk.CTkLabel(self.frame, font=font,
                                      text="Select here wavelengths to use in the analysis.")
        self.wvl_label.grid(row=0, column=0, columnspan=4, padx=(10, 10), pady=7)

        self.wvl_label2 = ctk.CTkLabel(self.frame, font=font, text="Wavelength to add [nm] : ")
        self.wvl_label2.grid(row=1, column=0, columnspan=1, padx=(10, 10), pady=7, sticky='e')

        self.wvl_entry = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.wvl_entry.grid(row=1, column=1, columnspan=1, padx=0)

        self.wvl_add_button = ctk.CTkButton(self.frame, text="Add wavelength", width=20, height=20,
                                            font=font, command=self.add_wvl)
        self.wvl_add_button.grid(row=2, column=0, columnspan=1, padx=0)

        self.text_help = (
            "The reference wavelength is the wavelength used to determine the first order properties of the system "
            "(effective, front and back focal length, etc). The reference sphere used for the wavefront error is the "
            " reference wavelength one.")
        self.button_help = ctk.CTkButton(self.frame, text="?", width=20, height=20, font=font,
                                         command=lambda: self.help_window.create_help_box(self.text_help))
        self.button_help.grid(row=2, column=1, padx=(0, 30), pady=0)

        self.error_textbox = ctk.CTkTextbox(self.frame, wrap="word", font=font, width=300, height=71,
                                            fg_color="transparent", text_color="red")
        self.error_textbox.grid(row=3, column=0, padx=0, pady=5, columnspan=2, sticky="w")
        text1 = 'An error occurred ! Write only one wavelength in the field to add. It should be a float or an int.'
        self.error_textbox.insert("0.0", text1)
        self.error_textbox.configure(state="disabled")  # configure textbox to be read-only
        self.error_textbox.grid_remove()  # hide by default

        self.scrollable_wvl = ScrollableWvlFrame(self.frame)
        self.scrollable_wvl.grid(row=1, rowspan=3, column=2, columnspan=3, pady=7, padx=7)
        self.scrollable_wvl.add_wvl([486.1327, 587.5618, 656.2725])
        self.scrollable_wvl.set_ref_wvl(587.5618)

    def add_wvl(self):
        try:
            wvl = float(self.wvl_entry.get())
            self.error_textbox.grid_remove()  # hide error

            self.scrollable_wvl.add_wvl(wvl)
        except:
            self.error_textbox.grid()  # show error

    def get_values(self):
        wvl_and_weight = self.scrollable_wvl.get_wvl_and_weight()

        if wvl_and_weight :  # not empty
            everything_correct = True
            error_txt = ''
            self.wvl_entry.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
            self.wvl_add_button.configure(border_width=0)
        else :
            everything_correct = False
            error_txt = 'No wavelength has been specified\n'
            self.wvl_entry.configure(border_color='red', border_width=4)
            self.wvl_add_button.configure(border_color='red', border_width=4)

        return [everything_correct, error_txt, wvl_and_weight]


class ScrollableWvlFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.wvl_list = []
        self.wvl_label = []
        self.button_list = []
        self.ref_wavelength = None
        self.checkbox_list = []

    def create_scroll(self):
        # create a scrollable list with all wavelengths
        for i, wvl in enumerate(self.wvl_list):
            self.create_label_button(wvl, i)

    def create_label_button(self, wvl, i):
        # create one label and one button
        wvl_txt = str(wvl) + " nm"
        wvl_label = ctk.CTkLabel(self, text=wvl_txt, compound="left", padx=5, anchor="w")
        wvl_button = ctk.CTkButton(self, text="Remove", width=50, height=24, command=lambda: self.remove_wvl(wvl))
        wvl_check = ctk.CTkCheckBox(self, text="ref", width=40, command=lambda: self.set_ref_wvl(wvl),
                                    checkbox_height=15, checkbox_width=15)
        wvl_label.grid(row=i, column=0, pady=(0, 10), padx=2, sticky="w")
        wvl_check.grid(row=i, column=1, pady=(0, 0), padx=2, sticky="nw")
        wvl_button.grid(row=i, column=2, pady=(0, 0), padx=2, sticky="nw")
        self.wvl_label.append(wvl_label)
        self.button_list.append(wvl_button)
        self.checkbox_list.append(wvl_check)

        if wvl == self.ref_wavelength :
            wvl_check.select()

    def set_ref_wvl(self, wvl):
        # can have only one reference wavelength. Deselect wavelength which are not reference ones.
        # and set ref wavelength to wvl

        try :
            # get index of ref wavelength
            i = self.wvl_list.index(wvl)
            self.checkbox_list[i].select()
            self.ref_wavelength = wvl
        except Exception as exception:  # ref wavelength do not exist
            self.ref_wavelength = None
            i = -1
            print(exception)
            print(self.wvl_list)
            print(wvl)

        for j, checkbox in enumerate(self.checkbox_list):
            if i != j:
                checkbox.deselect()

    def delete_scroll(self):
        # delete the scrollable list of wavelengths
        for label, button, checkbox in zip(self.wvl_label, self.button_list, self.checkbox_list):
            label.destroy()
            button.destroy()
            checkbox.destroy()

        self.wvl_label = []
        self.button_list = []
        self.checkbox_list = []

    def remove_wvl(self, wvl):
        # remove a wavelength from the list

        # get index of element to remove
        i_wvl = self.wvl_list.index(wvl)

        # remove wavelength from scroll (remove from gui objects)
        self.wvl_label[i_wvl].destroy()
        self.button_list[i_wvl].destroy()
        self.checkbox_list[i_wvl].destroy()

        # remove wavelength from lists (remove references to destroyed gui elements)
        self.wvl_list.remove(wvl)
        del self.wvl_label[i_wvl]
        del self.button_list[i_wvl]
        del self.checkbox_list[i_wvl]

        # check if ref wavelength
        if wvl == self.ref_wavelength :
            if self.wvl_list :  # not empty
                self.set_ref_wvl(self.wvl_list[0])
            else:
                self.ref_wavelength = None

    def add_wvl(self, wavelength):
        # add one or a list of wavelengths
        if type(wavelength) is list:
            wvls = wavelength
        else:
            wvls = [wavelength]

        for wvl in wvls:
            if wvl not in self.wvl_list:
                self.wvl_list.append(wvl)

        self.wvl_list.sort()

        self.delete_scroll()
        self.create_scroll()

    def get_wvl_and_weight(self):
        wvl_and_weight = []

        if self.ref_wavelength is None:
            i_ref = -1
        else:
            i_ref = self.wvl_list.index(self.ref_wavelength)
            wvl_and_weight.append((self.ref_wavelength, 1))

        for i, wvl in enumerate(self.wvl_list):
            if i != i_ref :
                wvl_and_weight.append((wvl, 1))

        return wvl_and_weight


class EflPupilCutoffTab(ctk.CTkTabview):
    def __init__(self, master, help_window=None, **kwargs):
        super().__init__(master, **kwargs)

        if hasattr(master, 'font'):
            font = master.font
            font.weight = "normal"
        else:
            font = ctk.CTkFont(size=15, weight="normal")

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)

        self._segmented_button.configure(font=font)

        # create tabs
        self.add("define parameters manually")
        self.add("remote refocus")
        self.add("only one infinity corrected objective")

        self.tab_man = self.tab("define parameters manually")
        self.tab_rf = self.tab("remote refocus")
        self.tab_1o = self.tab("only one infinity corrected objective")

        # TAB define parameters manually
        self.tab_man_label_efl = ctk.CTkLabel(master=self.tab_man, font=font,
                                              text="Desire effective focal length [mm] :  ")
        self.tab_man_label_efl.grid(row=0, column=0, padx=(5, 0), pady=7, sticky='e')
        self.tab_man_entry_efl = ctk.CTkEntry(self.tab_man, placeholder_text="float", font=font, width=70)
        self.tab_man_entry_efl.grid(row=0, column=1, columnspan=1, padx=0)

        self.tab_man_label_epd = ctk.CTkLabel(master=self.tab_man, font=font,
                                              text="Desire entrance pupil diameter [mm] :  ")
        self.tab_man_label_epd.grid(row=0, column=2, padx=(100, 0), pady=7, sticky='e')
        self.tab_man_entry_epd = ctk.CTkEntry(self.tab_man, placeholder_text="float", font=font, width=70)
        self.tab_man_entry_epd.grid(row=0, column=3, columnspan=1, padx=0)

        self.tab_man_label_coff = ctk.CTkLabel(master=self.tab_man, font=font,
                                               text="Cut-off angle [°] :  ")
        self.tab_man_label_coff.grid(row=1, column=0, padx=(100, 0), pady=7, sticky='e')
        self.tab_man_entry_coff = ctk.CTkEntry(self.tab_man, placeholder_text="float", font=font, width=70)
        self.tab_man_entry_coff.grid(row=1, column=1, columnspan=1, padx=0)

        # TAB remote refocus
        # row 0
        self.tab_rf_label_info = ctk.CTkLabel(master=self.tab_rf, font=font,
                                              text="TL2 is the focal lens to be designed.\n"
                                                   "O2 is the objective near TL2"
                                                   " and O1 is the other objective. TL1 is the other tube lens.\n"
                                                   "Refractive indices outside of the system are n1 at O1's side and n2"
                                                   " at O2's side.\n"
                                                   "n1 <> O1 <> TL1 <> TL2 (to design) <> O2 <> n2")
        self.tab_rf_label_info.grid(row=0, column=0, columnspan=8, padx=(5, 0), pady=7, sticky='w')

        # row 1
        self.tab_rf_label_MO1 = ctk.CTkLabel(master=self.tab_rf, font=font, text="MO1 :  ")
        self.tab_rf_label_MO1.grid(row=1, column=0, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_MO1 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_MO1.grid(row=1, column=1, columnspan=1, padx=0)

        self.tab_rf_label_NAO1 = ctk.CTkLabel(master=self.tab_rf, font=font, text="NA_O1 :  ")
        self.tab_rf_label_NAO1.grid(row=1, column=2, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_NAO1 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_NAO1.grid(row=1, column=3, columnspan=1, padx=0)

        self.tab_rf_label_fnO1 = ctk.CTkLabel(master=self.tab_rf, font=font, text="FN_O1 [mm] :  ")
        self.tab_rf_label_fnO1.grid(row=1, column=4, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_fnO1 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_fnO1.grid(row=1, column=5, columnspan=1, padx=0)

        # row 2
        self.tab_rf_label_n1 = ctk.CTkLabel(master=self.tab_rf, font=font, text="n1 :  ")
        self.tab_rf_label_n1.grid(row=2, column=0, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_n1 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_n1.grid(row=2, column=1, columnspan=1, padx=0)

        self.tab_rf_label_ftl1m = ctk.CTkLabel(master=self.tab_rf, font=font, text="ftl1_manufacturer [mm] : ")
        self.tab_rf_label_ftl1m.grid(row=2, column=2, padx=(50, 0), pady=7, sticky='e')
        self.tab_rf_entry_ftl1m = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_ftl1m.grid(row=2, column=3, columnspan=1, padx=0)

        self.tab_rf_label_ftl1u = ctk.CTkLabel(master=self.tab_rf, font=font, text="ftl1_used [mm] : ")
        self.tab_rf_label_ftl1u.grid(row=2, column=4, padx=(50, 0), pady=7, sticky='e')
        self.tab_rf_entry_ftl1u = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_ftl1u.grid(row=2, column=5, columnspan=1, padx=0)

        # row 3
        self.tab_rf.grid_rowconfigure(3, minsize=40)

        # row 4
        self.tab_rf_label_MO2 = ctk.CTkLabel(master=self.tab_rf, font=font, text="MO2 :  ")
        self.tab_rf_label_MO2.grid(row=4, column=0, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_MO2 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_MO2.grid(row=4, column=1, columnspan=1, padx=0)

        self.tab_rf_label_NAO2 = ctk.CTkLabel(master=self.tab_rf, font=font, text="NA_O2 :  ")
        self.tab_rf_label_NAO2.grid(row=4, column=2, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_NAO2 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_NAO2.grid(row=4, column=3, columnspan=1, padx=0)

        self.tab_rf_label_fnO2 = ctk.CTkLabel(master=self.tab_rf, font=font, text="FN_O2 [mm] :  ")
        self.tab_rf_label_fnO2.grid(row=4, column=4, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_fnO2 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_fnO2.grid(row=4, column=5, columnspan=1, padx=0)

        # row 5
        self.tab_rf_label_n2 = ctk.CTkLabel(master=self.tab_rf, font=font, text="n2 :  ")
        self.tab_rf_label_n2.grid(row=5, column=0, padx=(5, 0), pady=7, sticky='e')
        self.tab_rf_entry_n2 = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_n2.grid(row=5, column=1, columnspan=1, padx=0)

        self.tab_rf_label_ftl2m = ctk.CTkLabel(master=self.tab_rf, font=font, text="ftl2_manufacturer [mm] : ")
        self.tab_rf_label_ftl2m.grid(row=5, column=2, padx=(50, 0), pady=7, sticky='e')
        self.tab_rf_entry_ftl2m = ctk.CTkEntry(self.tab_rf, placeholder_text="float", font=font, width=70)
        self.tab_rf_entry_ftl2m.grid(row=5, column=3, columnspan=1, padx=0)

        self.tab_rf_text_help = ("Optical remote refocusing as described in Botcherby et al. 2008 "
                                 "(doi:10.1016/j.optcom.2007.10.007).\n"
                                 "TL2 is the focal lens to be designed.\n"
                                 "O2 is the objective near TL2 and O1 is the other objective. TL1 is the other tube lens.\n"
                                 "Refractive indices outside of the system are n1 at O1's side and n2 at O2's side.\n"
                                 "n1 <> O1 <> TL1 <> TL2 (to design) <> O2 <> n2\n"
                                 "O1 and O2 are infinity corrected microscope objectives.\n\n"
                                 "MO1 & MO2 : magnification of O1 and O2\n"
                                 "NA_O1 & NA_O2 : Numerical Aperture of O1 and O2\n"
                                 "FN_01 & FN_O2 : Field Number of O1 and O2\n"
                                 "n1 & n2 : refractive indices outside of the system at O1 and O2 side (ex: immersion "
                                 "refractive index of objective or of the sample...).\n"
                                 "ftl1_manufacturer : tube lens focal length which was supposed to be used for the "
                                 "microscope objective O1 (ex: 180mm for Olympus)\n"
                                 "ftl1_used : tube lens focal length which is used for O1 in your system. In case "
                                 "ftl1_used is not filled, it is supposed to be the same than ftl1_manufacturer.\n"
                                 "ftl2_manufacturer : same than ftl1_manufacturer but for O2.\n\n"
                                 "Given Botcherby et al. 2008, magnification from n1 space to n2 space is n1/n2.")
        self.tab_rf_button_help = ctk.CTkButton(self.tab_rf, text="?", width=20, height=20, font=font,
                                                command=lambda: self.help_window.create_help_box(self.tab_rf_text_help))
        self.tab_rf_button_help.grid(row=5, column=4, padx=(0, 30), pady=7, sticky="e")

        # row 6
        self.tab_rf.grid_rowconfigure(6, minsize=40)

        # row 7
        self.tab_rf_button_preview = ctk.CTkButton(self.tab_rf, text="Preview values", width=20, height=20, font=font,
                                                   command=self.tab_rf_preview)
        self.tab_rf_button_preview.grid(row=7, column=0, columnspan=2, padx=(0, 30), pady=7)

        self.tab_rf_textbox_preview = ctk.CTkTextbox(self.tab_rf, wrap="word", font=font, width=530, height=71)
        self.tab_rf_textbox_preview.grid(row=7, column=2, padx=0, pady=5, columnspan=4, sticky="w")
        text1 = ('Click on "Preview values" to get a view of needed effective focal length, pupil diameter and cut-off'
                 ' angle.')
        self.tab_rf_textbox_preview.insert("0.0", text1)
        self.tab_rf_textbox_preview.configure(state="disabled")  # configure textbox to be read-only

        # TAB ONE OBJECTIVE
        # row 0
        self.tab_rf_label_info = ctk.CTkLabel(master=self.tab_1o, font=font,
                                              text="You want to design a tube lens for an infinity corrected microscope"
                                                   " objective.")
        self.tab_rf_label_info.grid(row=0, column=0, columnspan=8, padx=(5, 0), pady=7, sticky='w')

        # row 1
        self.tab_1o_label_mag = ctk.CTkLabel(master=self.tab_1o, font=font, text="Obj Mag :  ")
        self.tab_1o_label_mag.grid(row=1, column=0, padx=(20, 0), pady=7, sticky='e')
        self.tab_1o_entry_mag = ctk.CTkEntry(self.tab_1o, placeholder_text="float", font=font, width=70)
        self.tab_1o_entry_mag.grid(row=1, column=1, columnspan=1, padx=0)

        self.tab_1o_label_NA = ctk.CTkLabel(master=self.tab_1o, font=font, text="Obj NA :  ")
        self.tab_1o_label_NA.grid(row=1, column=2, padx=(20, 0), pady=7, sticky='e')
        self.tab_1o_entry_NA = ctk.CTkEntry(self.tab_1o, placeholder_text="float", font=font, width=70)
        self.tab_1o_entry_NA.grid(row=1, column=3, columnspan=1, padx=0)

        self.tab_1o_label_fn = ctk.CTkLabel(master=self.tab_1o, font=font, text="Obj FN [mm] :  ")
        self.tab_1o_label_fn.grid(row=1, column=4, padx=(20, 0), pady=7, sticky='e')
        self.tab_1o_entry_fn = ctk.CTkEntry(self.tab_1o, placeholder_text="float", font=font, width=70)
        self.tab_1o_entry_fn.grid(row=1, column=5, columnspan=1, padx=0)

        # row 2
        self.tab_1o_label_ftlm = ctk.CTkLabel(master=self.tab_1o, font=font, text="ftl_manufacturer [mm] :  ")
        self.tab_1o_label_ftlm.grid(row=2, column=0, columnspan=1, padx=(20, 0), pady=7, sticky='e')
        self.tab_1o_entry_ftlm = ctk.CTkEntry(self.tab_1o, placeholder_text="float", font=font, width=70)
        self.tab_1o_entry_ftlm.grid(row=2, column=1, columnspan=1, padx=0)

        self.tab_1o_label_ftld = ctk.CTkLabel(master=self.tab_1o, font=font, text="ftl_to_design [mm] :  ")
        self.tab_1o_label_ftld.grid(row=2, column=2, columnspan=1, padx=(20, 0), pady=7, sticky='e')
        self.tab_1o_entry_ftld = ctk.CTkEntry(self.tab_1o, placeholder_text="float", font=font, width=70)
        self.tab_1o_entry_ftld.grid(row=2, column=3, columnspan=1, padx=0)

        self.tab_1o_text_help = ("You want to design a tube lens for an infinity corrected microscope objective.\n\n"
                                 "Obj Mag : magnification of the objective\n"
                                 "Obj NA : Numerical Aperture of the objective\n"
                                 "Obj FN : Field Number of the objective\n"
                                 "ftl_manufacturer : focal length of the tube lens which should be used with the "
                                 "objective (ex: 180mm for Olympus)\n"
                                 "ftl_to_design : focal length that you want the tube lens to design to have. "
                                 "If not filled, ftl_to_design will be ftl_manufacturer")
        self.tab_1o_button_help = ctk.CTkButton(self.tab_1o, text="?", width=20, height=20, font=font,
                                                command=lambda: self.help_window.create_help_box(self.tab_1o_text_help))
        self.tab_1o_button_help.grid(row=2, column=5, padx=0, pady=7, sticky="e")

        # row 3
        self.tab_1o.grid_rowconfigure(3, minsize=40)

        # row 4
        self.tab_1o_button_preview = ctk.CTkButton(self.tab_1o, text="Preview values", width=20, height=20, font=font,
                                                   command=self.tab_1o_preview)
        self.tab_1o_button_preview.grid(row=7, column=0, columnspan=1, padx=(0, 30), pady=7)

        self.tab_1o_textbox_preview = ctk.CTkTextbox(self.tab_1o, wrap="word", font=font, width=500, height=71)
        self.tab_1o_textbox_preview.grid(row=7, column=1, padx=0, pady=5, columnspan=5, sticky="w")
        text1 = ('Click on "Preview values" to get a view of needed effective focal length, pupil diameter and cut-off'
                 ' angle.')
        self.tab_1o_textbox_preview.insert("0.0", text1)
        self.tab_1o_textbox_preview.configure(state="disabled")  # configure textbox to be read-only

    def tab_rf_preview(self):
        # preview efl, epd and cut off angle in tab_rf

        # get values
        get_results, computed_data = self.tab_rf_calcul()

        if get_results:
            [epd, efl, cut_off] = computed_data
            text1 = ('TL2 required effective focal length : ' + '{:.5}'.format(efl) + ' mm\n'
                     'TL2 required entrance pupil diameter : ' + '{:.5}'.format(epd) + ' mm\n'
                     'TL2 required minimum cut-off angle : ' + '{:.4}'.format(cut_off) + ' °')
        else:
            text1 = computed_data

        # write on the textbox
        self.tab_rf_textbox_preview.configure(state="normal")  # change textbox to writable
        self.tab_rf_textbox_preview.delete("0.0", "end")  # delete all text
        self.tab_rf_textbox_preview.insert("0.0", text1)  # write text
        self.tab_rf_textbox_preview.configure(state="disabled")  # change textbox to read only

    def tab_rf_calcul(self):
        # get data entered in field of tab_rf, and compute pupil diameter, effective focal length and cut-off angle.
        # return [epd, efl, cut_off] if data are valid, False if not.
        try:
            mo1_ok, mo1_txt, mo1 = check_entry_type(self.tab_rf_entry_MO1,
                                         float, error_txt_type="O1 magnification should be a float.\n",
                                         inf=0, error_txt_inf="O1 magnification should be positive.\n")
            mo2_ok, mo2_txt, mo2 = check_entry_type(self.tab_rf_entry_MO2,
                                         float, error_txt_type="O2 magnification should be a float.\n",
                                         inf=0, error_txt_inf="O2 magnification should be positive.\n")
            nao1_ok, nao1_txt, nao1 = check_entry_type(self.tab_rf_entry_NAO1,
                                         float, error_txt_type="NAO1 magnification should be a float.\n",
                                         inf=0, error_txt_inf="NAO1 magnification should be positive.\n")
            nao2_ok, nao2_txt, nao2 = check_entry_type(self.tab_rf_entry_NAO2,
                                         float, error_txt_type="NAO2 magnification should be a float.\n",
                                         inf=0, error_txt_inf="NAO2 magnification should be positive.\n")
            fno1_ok, fno1_txt, fno1 = check_entry_type(self.tab_rf_entry_fnO1,
                                         float, error_txt_type="FNO1 magnification should be a float.\n",
                                         inf=0, error_txt_inf="FNO1 magnification should be positive.\n")
            fno2_ok, fno2_txt, fno2 = check_entry_type(self.tab_rf_entry_fnO2,
                                         float, error_txt_type="FNO2 magnification should be a float.\n",
                                         inf=0, error_txt_inf="FNO2 magnification should be positive.\n")
            n1_ok, n1_txt, n1 = check_entry_type(self.tab_rf_entry_n1,
                                         float, error_txt_type="n1 magnification should be a float.\n",
                                         inf=0, error_txt_inf="n1 magnification should be positive.\n")
            n2_ok, n2_txt, n2 = check_entry_type(self.tab_rf_entry_n2,
                                         float, error_txt_type="n2 magnification should be a float.\n",
                                         inf=0, error_txt_inf="n2 magnification should be positive.\n")
            ftl1m_ok, ftl1m_txt, ftl1m = check_entry_type(self.tab_rf_entry_ftl1m,
                                         float, error_txt_type="Manufacturer tube lens 1 focal length should be a float.\n")
            ftl2m_ok, ftl2m_txt, ftl2m = check_entry_type(self.tab_rf_entry_ftl2m,
                                         float, error_txt_type="Manufacturer tube lens 2 focal length should be a float.\n")

            ftl1u = self.tab_rf_entry_ftl1u.get()

            if ftl1u == '':  # entry not filled
                ftl1u_ok, ftl1u_txt, ftl1u = ftl1m_ok, ftl1m_txt, ftl1m
            else:
                ftl1u_ok, ftl1u_txt, ftl1u = check_entry_type(self.tab_rf_entry_ftl1u,
                                         float, error_txt_type="Used tube lens 1 focal length should be a float or nothing.\n")

            if (mo1_ok and mo2_ok and nao1_ok and nao2_ok and n1_ok and n2_ok and fno1_ok and fno2_ok and ftl1m_ok and
                ftl2m_ok and ftl1u_ok):
                mtot = n1 / n2
                epd = fls.pupil_diameter(nao2, mo2, ftl2m, mtot, nao1)
                efl = fls.f_tl2_from_f_tl1(mo1, ftl1m, ftl1u, mo2, ftl2m, n1, n2)
                cut_off = fls.max_fld_angle(fno2, mo2, ftl2m, mtot, fno1, mo1)

                return True, [epd, efl, cut_off]

            else:
                error_txt = (mo1_txt + mo2_txt + n1_txt + n2_txt + nao1_txt + nao2_txt + ftl1m_txt + ftl1u_txt +
                             ftl2m_txt + fno1_txt + fno2_txt)
                return False, error_txt

        except:
            return False, 'An error occurred, please check if all entries are filled with float or int.'

    def tab_1o_preview(self):
        # preview efl, epd and cut off angle in tab_1o

        # get values
        get_results, computed_data = self.tab_1o_calcul()

        if get_results:
            [epd, efl, cut_off] = computed_data
            text1 = ('TL2 required effective focal length : ' + '{:.5}'.format(efl) + ' mm\n'
                     'TL2 required entrance pupil diameter : ' + '{:.5}'.format(epd) + ' mm\n'
                     'TL2 required minimum cut-off angle : ' + '{:.4}'.format(cut_off) + ' °')
        else:
            text1 = computed_data

        # write on the textbox
        self.tab_1o_textbox_preview.configure(state="normal")  # change textbox to writable
        self.tab_1o_textbox_preview.delete("0.0", "end")  # delete all text
        self.tab_1o_textbox_preview.insert("0.0", text1)  # write text
        self.tab_1o_textbox_preview.configure(state="disabled")  # change textbox to read only

    def tab_1o_calcul(self):
        # get data entered in field of tab_rf, and compute pupil diameter, effective focal length and cut-off angle.
        # return [epd, efl, cut_off] if data are valid, False if not.
        try:
            # get all fields, and check if they are float or not, and if some are positive.
            # If not, wrong fields are highlighted
            ftld = self.tab_1o_entry_ftld.get()

            mag_ok, mag_txt, mag = check_entry_type(
                self.tab_1o_entry_mag, float, error_txt_type="The objective magnification should be a float.\n",
                inf=0, error_txt_inf="The objective magnification should be positive.\n")
            na_ok, na_txt, na = check_entry_type(
                self.tab_1o_entry_NA, float, error_txt_type="The objective numerical aperture should be a float.\n",
                inf=0, error_txt_inf="The objective numerical aperture should be positive.\n")
            fn_ok, fn_txt, fn = check_entry_type(
                self.tab_1o_entry_fn, float, error_txt_type="The objective field number should be a float.\n",
                inf=0, error_txt_inf="The objective field number should be positive.\n")
            ftlm_ok, ftlm_txt, ftlm = check_entry_type(
                self.tab_1o_entry_ftlm, float,
                error_txt_type="The manufacturer tube lens focal length should be a float.\n")

            if ftld == '':  # entry not filled
                ftld_ok, ftld_txt, ftld = ftlm_ok, '', ftlm
            else:
                ftld_ok, ftld_txt, ftld = check_entry_type(
                    self.tab_1o_entry_ftld, float,
                    error_txt_type="The designed tube lens focal length should be a float.\n")

            # return results
            if mag_ok and na_ok and fn_ok and ftlm_ok and ftld_ok :
                epd = fls.pupil_diameter(na, mag, ftlm)
                efl = ftld
                cut_off = fls.max_fld_angle(fn, mag, ftlm)

                return True, [epd, efl, cut_off]

            else:
                error_txt = mag_txt + na_txt + fn_txt + ftlm_txt + ftld_txt
                return False, error_txt

        except:
            return False, 'An error occurred, please check if all entries are filled with float or int.'

    def get_values(self):
        current_tab_name = self.get()

        match current_tab_name:
            case "define parameters manually":
                return self.get_values_tab_man()
            case "remote refocus":
                return self.get_values_tab_1o_rf(self.tab_rf_calcul())
            case "only one infinity corrected objective":
                return self.get_values_tab_1o_rf(self.tab_1o_calcul())

    def get_values_tab_1o_rf(self, tab_calcul):
        everything_correct, computed_data = tab_calcul

        if everything_correct:
            # [epd, efl, cut_off] = computed_data
            values = {'expected_focal_length': computed_data[1],
                      'pupil': computed_data[0],
                      'cut_off_angle_min': computed_data[2]}
            error_txt = ''
        else:
            error_txt = computed_data
            values = {'expected_focal_length': '', 'pupil': '', 'cut_off_angle_min': ''}

        return [everything_correct, error_txt, values]

    def get_values_tab_man(self):
        values = {'expected_focal_length': self.tab_man_entry_efl.get(),
                  'pupil': self.tab_man_entry_epd.get(),
                  'cut_off_angle_min': self.tab_man_entry_coff.get()}

        everything_correct = True
        error_txt = ''

        try:
            values['expected_focal_length'] = float(values['expected_focal_length'])
            self.tab_man_entry_efl.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        except:
            everything_correct = False
            error_txt = error_txt + "The pair desire effective focal length should be a float.\n"
            self.tab_man_entry_efl.configure(border_color='red', border_width=4)

        try:
            values['pupil'] = float(values['pupil'])
            self.tab_man_entry_epd.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        except:
            everything_correct = False
            error_txt = error_txt + "The pair entrance pupil should be a float.\n"
            self.tab_man_entry_epd.configure(border_color='red', border_width=4)

        try:
            values['cut_off_angle_min'] = float(values['cut_off_angle_min'])
            self.tab_man_entry_coff.configure(border_color=['#979DA2', '#565B5E'], border_width=2)

            if values['cut_off_angle_min'] < 0:
                everything_correct = False
                error_txt = error_txt + "The pair minimal cut-off angle should be positive.\n"
                self.tab_man_entry_coff.configure(border_color='red', border_width=4)

        except:
            everything_correct = False
            error_txt = error_txt + "The pair minimal cut-off angle should be a float.\n"
            self.tab_man_entry_coff.configure(border_color='red', border_width=4)

        return [everything_correct, error_txt, values]


#       "The distance between pupil and pair is the distance between the entrance pupil and the first physical "
#            "surface of the first lens of the pair. In case of remote refocusing systems as defined by Botcherby 2008, "
#            "this distance is the front focal lens of the pair. The entrance pupil is the position from which"
#            " entrance field angle will vary. "
# Entrance field rotating position distance to first pair surface.


class PairConfigFrame(ctk.CTkFrame):
    def __init__(self, master, new_frame=False, help_window=None, only_one=False, **kwargs):
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

        self.only_one = only_one

        # label for main indication
        self.title_label = ctk.CTkLabel(self.frame, font=font, text="Select here configurations of\n"
                                                                    "lenses orientations to use.")
        self.title_label.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=7)

        if only_one :
            several_txt = 'one or no configuration.'
        else :
            several_txt = 'none, one, or several configurations.'

        # help window
        self.text_help = (
            "You can select here configurations of lenses orientations to be used in the analysis.\n"
            "You can check " + several_txt + " They are detailed below :\n\n"
            "With ( the more curved side of the lens and | the less curved side, and the objective "
            "is at the infinite side, we have :\n\n"
            "A : infinity |) |) image\n"
            "B : infinity |) (| image\n"
            "C : infinity (| (| image\n"
            "D : infinity (| |) image\n"
            "None : lenses orientations are the ones of the file from where they are obtained. None is when no "
            "configuration is selected.\n\n"
            "Configurations are also shown in the image at the right of this help window.")

        try:
            image_path = os.path.join(os.path.dirname(__file__), r"..\img\config.png")
            self.image_help = ctk.CTkImage(Image.open(image_path), size=(173, 429))
        except:
            self.image_help = None
        self.button_help = ctk.CTkButton(self.frame, text="?", width=20, height=20,font=font,
                                         command=lambda: self.help_window.create_help_box(self.text_help, self.image_help))
        self.button_help.grid(row=0, column=3, padx=(0, 20), pady=7)

        # checkboxes
        self.checkbox_A = ctk.CTkCheckBox(master=self.frame, text="Config A\ninf |) |) img", font=font,
                                          command=lambda : self.deselect("A"))
        self.checkbox_A.grid(row=1, column=0, pady=(0, 0), padx=20, sticky="n")

        self.checkbox_B = ctk.CTkCheckBox(master=self.frame, text="Config B\ninf |) (| img", font=font,
                                          command=lambda : self.deselect("B"))
        self.checkbox_B.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")

        self.checkbox_C = ctk.CTkCheckBox(master=self.frame, text="Config C\ninf (| (| img", font=font,
                                          command=lambda : self.deselect("C"))
        self.checkbox_C.grid(row=3, column=0, pady=(20, 0), padx=20, sticky="n")

        self.checkbox_D = ctk.CTkCheckBox(master=self.frame, text="Config D\ninf (| |) img", font=font,
                                          command=lambda : self.deselect("D"))
        self.checkbox_D.grid(row=4, column=0, pady=(20,10), padx=20, sticky="n")

    def deselect(self, config):
        if self.only_one:
            match config:
                case "A":
                    if self.checkbox_A.get() :
                        self.checkbox_B.deselect()
                        self.checkbox_C.deselect()
                        self.checkbox_D.deselect()

                case "B":
                    if self.checkbox_B.get():
                        self.checkbox_A.deselect()
                        self.checkbox_C.deselect()
                        self.checkbox_D.deselect()

                case "C":
                    if self.checkbox_C.get():
                        self.checkbox_B.deselect()
                        self.checkbox_A.deselect()
                        self.checkbox_D.deselect()

                case "D":
                    if self.checkbox_D.get():
                        self.checkbox_B.deselect()
                        self.checkbox_C.deselect()
                        self.checkbox_A.deselect()

    def get_values(self):
        configs = []

        if self.checkbox_A.get():
            configs.append("A")

        if self.checkbox_B.get():
            configs.append("B")

        if self.checkbox_C.get():
            configs.append("C")

        if self.checkbox_D.get():
            configs.append("D")

        if not configs:  # empty
            configs.append(None)

        everything_correct = True
        error_txt = ''

        return [everything_correct, error_txt, configs]


class PairGeometryFrame(ctk.CTkFrame):
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

        # label for main indication
        self.title_label = ctk.CTkLabel(self.frame, font=font, text="Define here distances between main surfaces of "
                                                                    "pairs.")
        self.title_label.grid(row=0, column=0, columnspan=3, padx=(10, 10), pady=7)

        # help window
        self.text_help = (
            "You can define here distances between main surfaces of pairs. Pairs which does not meet these criteria "
            "would be rejected of the analysis. This is useful to be sure to get a pair that will physically fit in "
            "your set-up.\n"
            "All distances are in mm. They are optional fields.\n\n"
            "The distance between lenses is between physical surfaces of lenses. "
            "It is required that: maximal distance between lenses >= minimal distance between lenses >= 0 mm.\n"
            "Another distance to give is -ffl, from the front focal plane to the first physical"
            " surface of the pair. A negative distance is when the object focal plane is inside the pair (or after the "
            "second lens).\n"
            "The back focal distance is between the last physical surface of the last lens of the pair, and the"
            " pair's image focal plane.\n\n"
            "In case fields are not filled, no limit will be defined for unfilled fields, except for the minimal "
            "distance between lenses, which would be 0 mm.\n"
            "See figure at the right for visual explanations. The positive direction is from the left to the right for"
            " all distances (see '+' arrows).")

        try:
            image_path = os.path.join(os.path.dirname(__file__), r"..\img\focal_planes.png")
            self.image_help = ctk.CTkImage(Image.open(image_path), size=(265, 202))
        except:
            self.image_help = None

        self.button_help = ctk.CTkButton(self.frame, text="?", width=20, height=20,font=font,
                                         command=lambda: self.help_window.create_help_box(self.text_help,
                                                                                          self.image_help))
        self.button_help.grid(row=0, column=3, padx=(0, 30), pady=7)

        self.label_min_between = ctk.CTkLabel(master=self.frame, font=font,
                                              text="Minimal distance between\nlenses [mm] :  ")
        self.label_min_between.grid(row=1, column=0, padx=(20, 0), pady=7, sticky='e')
        self.entry_min_between = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_min_between.grid(row=1, column=1, columnspan=1, padx=10)

        self.label_max_between = ctk.CTkLabel(master=self.frame, font=font,
                                              text="Maximal distance between\nlenses [mm] :  ")
        self.label_max_between.grid(row=1, column=2, padx=(20, 0), pady=7, sticky='e')
        self.entry_max_between = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_max_between.grid(row=1, column=3, columnspan=1, padx=10)

        self.label_min_before = ctk.CTkLabel(master=self.frame, font=font,
                                              text="Minimal distance\nffp -> pair [mm] :  ")
        self.label_min_before.grid(row=2, column=0, padx=(20, 0), pady=7, sticky='e')
        self.entry_min_before = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_min_before.grid(row=2, column=1, columnspan=1, padx=10)

        self.label_max_before = ctk.CTkLabel(master=self.frame, font=font,
                                              text="Maximal distance\nffp -> pair [mm] :  ")
        self.label_max_before.grid(row=2, column=2, padx=(20, 0), pady=7, sticky='e')
        self.entry_max_before = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_max_before.grid(row=2, column=3, columnspan=1, padx=10)

        self.label_min_after = ctk.CTkLabel(master=self.frame, font=font,
                                              text="Minimal back focal\ndistance [mm] :  ")
        self.label_min_after.grid(row=3, column=0, padx=(20, 0), pady=7, sticky='e')
        self.entry_min_after = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_min_after.grid(row=3, column=1, columnspan=1, padx=10)

        self.label_max_after = ctk.CTkLabel(master=self.frame, font=font,
                                              text="Maximal back focal\ndistance [mm] :  ")
        self.label_max_after.grid(row=3, column=2, padx=(20, 0), pady=7, sticky='e')
        self.entry_max_after = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_max_after.grid(row=3, column=3, columnspan=1, padx=10)

        # advanced parameters
        self.switch_advanced_param = ctk.CTkSwitch(self.frame, text="Advanced distances parameters", font=font,
                                                   command=self.showhide_advanced_frame)
        self.switch_advanced_param.grid(row=4, column=0, padx=5, columnspan=2, pady=7, sticky="w")
        self.switch_advanced_param.deselect()  # default : OFF

        self.advanced_param_frame = ctk.CTkFrame(self.frame)
        self.advanced_param_obj = DistanceBeforePairFrame(self.advanced_param_frame, help_window=help_window)
        self.advanced_param_frame.grid(row=5, column=0, columnspan=6, padx=5, pady=7, sticky="w")
        self.advanced_param_frame.grid_remove()  # hide the frame by default

    def showhide_advanced_frame(self):
        # show or hide the frame with advanced parameters
        # get the switch state
        state = self.switch_advanced_param.get()
        if state == 0:  # OFF
            self.advanced_param_frame.grid_remove()  # hide the frame
        else:  # ON
            self.advanced_param_frame.grid()  # show the frame

    def get_values(self):
        # check distance from stop aperture to pair first lens
        everything_correct, error_txt, values = self.advanced_param_obj.get_values()
        if not everything_correct:
            self.switch_advanced_param.select()
            self.showhide_advanced_frame()

        # check distance between lenses
        [o1_o2_ok, o1_o2_error_txt, o1_o2_min, o1_o2_max] = check_entry_min_max(
            self.entry_min_between, self.entry_max_between, default_values=True,
            default_value_min=0, default_value_max=None,
            error_txt_min="The minimum distance between lenses should be a float or nothing.\n",
            error_txt_max="The maximum distance between lenses should be a float or nothing.\n",
            error_txt_min_sup_max="The minimum distance between lenses should be inferior to the maximum one.\n")

        # check distance before pair
        [ffl_ok, ffl_error_txt, offl_min, offl_max] = check_entry_min_max(
            self.entry_min_before, self.entry_max_before, default_values=True,
            error_txt_min="The minimum distance before the pair should be a float or nothing.\n",
            error_txt_max="The maximum distance before the pair should be a float or nothing.\n",
            error_txt_min_sup_max="The minimum distance before the pair should be inferior to the maximum one.\n")

        if offl_max is not None:
            ffl_min = -offl_max
        else :
            ffl_min = None

        if offl_min is not None:
            ffl_max = -offl_min
        else :
            ffl_max = None

        # check distance after pair
        [bfl_ok, bfl_error_txt, bfl_min, bfl_max] = check_entry_min_max(
            self.entry_min_after, self.entry_max_after, default_values=True,
            error_txt_min="The minimum distance after the pair should be a float or nothing.\n",
            error_txt_max="The maximum distance after the pair should be a float or nothing.\n",
            error_txt_min_sup_max="The minimum distance after the pair should be inferior to the maximum one.\n")

        # put all values together
        values['dist_criteria0'] = {'O1O2_min': o1_o2_min, 'O1O2_max': o1_o2_max, 'ffl_min': ffl_min,
                                    'ffl_max': ffl_max, 'bfl_min': bfl_min, 'bfl_max': bfl_max}

        everything_correct = everything_correct and o1_o2_ok and ffl_ok and bfl_ok
        error_txt = error_txt + o1_o2_error_txt + ffl_error_txt + bfl_error_txt

        return [everything_correct, error_txt, values]


class DistanceBeforePairFrame(ctk.CTkFrame):
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

        self.advanced_text_help = (
            "Here can be configure the distance from the field rotating position (objective exit pupil)"
            " to the first lens of the pair."
            " See Figure at the right.\n"
            "In the case of a remote refocusing system, this distance should be the pair front focal length.\n"
            "Indeed, objectives and tube lenses are in 4f system.")

        try:
            image_path = os.path.join(os.path.dirname(__file__), r"..\img\angle.png")
            self.image_help = ctk.CTkImage(Image.open(image_path), size=(265, 202))
        except:
            self.image_help = None

        self.advanced_button_help = ctk.CTkButton(self.frame, text="?", width=20, height=20, font=font,
                                                  command=lambda: self.help_window.create_help_box(
                                                      self.advanced_text_help, self.image_help))
        self.advanced_button_help.grid(row=0, column=0, padx=30, pady=7, sticky='w')

        self.label_dist_stop_pair = ctk.CTkLabel(self.frame, font=font,
                                                 text="Distance from the aperture stop to the first lens of pair.\n"
                                                      "(The entering field rotate at the aperture position).")
        self.label_dist_stop_pair.grid(row=1, column=0, columnspan=4, padx=(5, 0), pady=7, sticky='w')

        self.checkbox_dist_stop_pair = ctk.CTkCheckBox(self.frame, font=font,
                                                       text="distance is -front focal length\n"
                                                            "(remote refocus case)",
                                                       command=self.showhide_entry_stop_pair)
        self.checkbox_dist_stop_pair.grid(row=2, column=0, padx=10, pady=7, sticky='w')
        self.checkbox_dist_stop_pair.select()  # default ON

        self.label_entry_stop_pair = ctk.CTkLabel(self.frame, font=font,
                                                  text="Distance [mm] : ")
        self.label_entry_stop_pair.grid(row=2, column=1, columnspan=1, padx=(5, 0), pady=7, sticky='e')
        self.label_entry_stop_pair.grid_remove()

        self.entry_stop_pair = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=70)
        self.entry_stop_pair.grid(row=2, column=2, columnspan=1, padx=0, pady=7, sticky='w')
        self.entry_stop_pair.grid_remove()  # hide the entry

    def showhide_entry_stop_pair(self):
        # show or hide the frame with advanced parameters
        state = self.checkbox_dist_stop_pair.get()
        if state == 0:  # OFF
            self.label_entry_stop_pair.grid()
            self.entry_stop_pair.grid()  # show the entry
        else:  # ON
            self.label_entry_stop_pair.grid_remove()
            self.entry_stop_pair.grid_remove()  # hide the entry

    def get_values(self):
        # initialisation
        values = {}
        everything_correct = True
        error_txt = ''

        # check distance from stop aperture to pair first lens
        if self.checkbox_dist_stop_pair.get():
            values['dist_pupil_pair'] = None
        else:
            try:
                values['dist_pupil_pair'] = float(self.entry_stop_pair.get())
                self.entry_stop_pair.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
            except:
                values['dist_pupil_pair'] = ''
                everything_correct = False
                error_txt = error_txt + "The distance from the stop aperture to the pair should be a float.\n"
                self.entry_stop_pair.configure(border_color='red', border_width=4)

        return [everything_correct, error_txt, values]



class PairSaveFrame(ctk.CTkFrame):
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

        # label for main indication
        self.title_label = ctk.CTkLabel(self.frame, font=font,
                                        text="Save results parameters.")
        self.title_label.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=7, sticky='w')

        # help window
        self.text_help = (
            "Define here the output parameters of the analysis. The path to the parent directory in which analysis "
            "results should be saved needs to be given. A folder with the analysis name will be created in this folder in"
            " order to group results. In the case where no analysis name is defined, the analysis name will be "
            "PyRFTL_year_month_day_hourhminute. Results are exported in a csv file. They can also be exported in more"
            " details in others files.")

        self.button_help = ctk.CTkButton(self.frame, text="?", width=20, height=20,font=font,
                                         command=lambda: self.help_window.create_help_box(self.text_help))
        self.button_help.grid(row=0, column=3, padx=(0, 30), pady=7)

        # button, help and textbox Lens import
        self.button_folder = ctk.CTkButton(self.frame, text="Select save directory", command=self.askdir, font=font)
        self.button_folder.grid(row=1, column=0, padx=5, pady=7)
        self.entry_folder = ctk.CTkEntry(self.frame, font=font, width=700, height=40)
        self.entry_folder.grid(row=1, column=1, columnspan=6, padx=10, pady=(5, 10))

        self.label_name = ctk.CTkLabel(master=self.frame, font=font, text="Analysis name :  ")
        self.label_name.grid(row=2, column=0, padx=(20, 0), pady=7, sticky='e')
        self.entry_name = ctk.CTkEntry(self.frame, placeholder_text="PyRFTL_date_time", font=font, width=400)
        self.entry_name.grid(row=2, column=1, columnspan=3, padx=10, sticky='w')

        # advanced parameters
        self.switch_advanced_param = ctk.CTkSwitch(self.frame, text="Advanced export parameters", font=font,
                                                   command=self.showhide_advanced_frame)
        self.switch_advanced_param.grid(row=3, column=0, padx=5, columnspan=2, pady=7, sticky="w")
        self.switch_advanced_param.deselect()  # default : OFF

        self.advanced_param_frame = ctk.CTkFrame(self.frame)
        self.advanced_param_frame.grid(row=4, column=0, columnspan=6, padx=5, pady=7, sticky="w")
        self.advanced_param_frame.grid_remove()  # hide the frame by default

        self.advanced_text_help = (
            "It is possible to define here exported parameters for the CSV file :\n"
            "Separators between columns, rows and for decimal numbers can be defined for the result CSV file.\n"
            "It is possible to hide base paths in the csv file (warning : only for this file, not in other ones !). "
            "Example : if C:\\Users\\User1\\PyRFTL\\Lenses is the folder which contain lenses, "
            "C:\\Users\\User1\\PyRFTL\\Lenses\\manufacturer\\lens1.zmx will be shown as manufacturer\\lens1.zmx."
            "\n\n"
            "More details can be exported for some pairs. 'best pairs' are defined in computing advanced parameters. "
            "They are the pairs with the best RMS wavefront error.\n"
            "It is possible to export details of the sequential model of pairs : one text file per pair, with details"
            " about each surfaces and gaps of the model describing the system. It is recommended to check its accuracy"
            " for the pair you select after the analysis.\n"
            "It is possible to export pairs in rayoptics optical model, in order to analyse them in rayoptics.")

        self.advanced_button_help = ctk.CTkButton(self.advanced_param_frame, text="?", width=20, height=20, font=font,
                                                  command=lambda: self.help_window.create_help_box(self.advanced_text_help))
        self.advanced_button_help.grid(row=0, column=0, padx=(0, 30), pady=7)

        #### CSV ADVANCED EXPORT SETTINGS ####
        self.csv_frame = ctk.CTkFrame(self.advanced_param_frame)
        self.csv_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=7, sticky="w")

        self.csv_frame_main_label = ctk.CTkLabel(master=self.csv_frame, font=font,
                                                 text="CSV file settings : ")
        self.csv_frame_main_label.grid(row=0, column=0, columnspan=3, padx=(20, 0), pady=7, sticky='e')

        self.csv_separator_frame = ctk.CTkFrame(self.csv_frame)
        self.csv_separator_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=7, sticky="w")
        self.csv_separator_main_label = ctk.CTkLabel(master=self.csv_separator_frame, font=font,
                                                     text="Separators for CSV file : ")
        self.csv_separator_main_label.grid(row=0, column=0, columnspan=3, padx=(20, 0), pady=7, sticky='e')

        self.label_csv_sep_column = ctk.CTkLabel(master=self.csv_separator_frame, font=font, text="Column :  ")
        self.label_csv_sep_column.grid(row=1, column=0, padx=(5, 0), pady=7, sticky='e')
        self.entry_csv_sep_column = ctk.CTkEntry(self.csv_separator_frame, placeholder_text=";", font=font, width=50)
        self.entry_csv_sep_column.grid(row=1, column=1, columnspan=1, padx=0)

        self.label_csv_sep_row = ctk.CTkLabel(master=self.csv_separator_frame, font=font, text="Row :  ")
        self.label_csv_sep_row.grid(row=1, column=2, padx=(20, 0), pady=7, sticky='e')
        self.entry_csv_sep_row = ctk.CTkEntry(self.csv_separator_frame, placeholder_text="\\n", font=font, width=50)
        self.entry_csv_sep_row.grid(row=1, column=3, columnspan=1, padx=0)

        self.label_csv_sep_decimal = ctk.CTkLabel(master=self.csv_separator_frame, font=font, text="Decimal :  ")
        self.label_csv_sep_decimal.grid(row=1, column=4, padx=(20, 0), pady=7, sticky='e')
        self.entry_csv_sep_decimal = ctk.CTkEntry(self.csv_separator_frame, placeholder_text=".", font=font, width=50)
        self.entry_csv_sep_decimal.grid(row=1, column=5, columnspan=1, padx=(0,10))

        self.checkbox_hide_path_in_csv = ctk.CTkCheckBox(self.csv_frame, text="Hide paths in CSV file",
                                                         font=font)
        self.checkbox_hide_path_in_csv.grid(row=1, column=3, padx=10, pady=7)

        #### OTHERS ADVANCED EXPORT SETTINGS ####
        self.label_save_seqtxt = ctk.CTkLabel(master=self.advanced_param_frame, font=font, text="Export sequential "
                                                                                                "\nmodel details :")
        self.label_save_seqtxt.grid(row=2, column=0, padx=(20, 0), pady=7, sticky='e')
        self.optionmenu_save_seqtxt = ctk.optionmenu = ctk.CTkOptionMenu(self.advanced_param_frame,
                                                                         values=["No", "Best pairs", "All pairs"],
                                                                         font=font)
        self.optionmenu_save_seqtxt.grid(row=2, column=1, padx=10, pady=7, sticky='w')
        self.optionmenu_save_seqtxt.set("Best pairs")

        self.label_save_roa = ctk.CTkLabel(master=self.advanced_param_frame, font=font, text="Save pairs RayOptics"
                                                                                             "\noptical models :")
        self.label_save_roa.grid(row=2, column=2, padx=(20, 0), pady=7, sticky='e')
        self.optionmenu_save_roa = ctk.CTkOptionMenu(self.advanced_param_frame, font=font,
                                                                      values=["No", "Best pairs", "All pairs"])
        self.optionmenu_save_roa.grid(row=2, column=3, padx=10, pady=7, sticky='w')
        self.optionmenu_save_roa.set("No")


    def askdir(self):
        dirpath = tkinter.filedialog.askdirectory()
        self.entry_folder.delete(0, "end")  # delete all text
        self.entry_folder.insert(0, dirpath)  # add text

    def showhide_advanced_frame(self):
        # show or hide the frame with advanced parameters
        # get the switch state
        state = self.switch_advanced_param.get()
        if state == 0:  # OFF
            self.advanced_param_frame.grid_remove()  # hide the frame
        else:  # ON
            self.advanced_param_frame.grid()  # show the frame

    def get_values(self):
        values = {'save_folder_path': self.entry_folder.get(),
                  'analysis_name' : self.entry_name.get(),
                  'output_csv' : {'output_csv_column_separator': self.entry_csv_sep_column.get(),
                                  'output_csv_row_separator': self.entry_csv_sep_row.get(),
                                  'output_csv_decimal_separator': self.entry_csv_sep_decimal.get(),
                                  'hide_path_in_csv': self.checkbox_hide_path_in_csv.get()},
                  'save_seq_detail' : self.optionmenu_save_seqtxt.get(),
                  'save_roa' : self.optionmenu_save_roa.get()
                  }

        everything_correct = True
        error_txt = ''

        # check and convert input
        if not os.path.isdir(values['save_folder_path']):
            everything_correct = False
            error_txt = error_txt + "Saving directory is not a directory or path do not exist.\n"
            self.entry_folder.configure(border_color='red', border_width=4)
        else:
            self.entry_folder.configure(border_color=['#979DA2', '#565B5E'], border_width=0)

        if values['analysis_name'] == '':
            values['analysis_name'] = None

        if values['output_csv']['output_csv_column_separator'] == '':
            values['output_csv']['output_csv_column_separator'] = ';'

        if values['output_csv']['output_csv_row_separator'] == '':
            values['output_csv']['output_csv_row_separator'] = '\n'

        if values['output_csv']['output_csv_decimal_separator'] == '':
            values['output_csv']['output_csv_decimal_separator'] = '.'

        match values['save_seq_detail']:
            case "Best pairs":
                values['save_seq_detail'] = 'best'
            case "All pairs":
                values['save_seq_detail'] = 'all'
            case "No" :
                values['save_seq_detail'] = 'no'

        match values['save_roa']:
            case "Best pairs":
                values['save_roa'] = 'best'
            case "All pairs":
                values['save_roa'] = 'all'
            case "No" :
                values['save_roa'] = 'no'

        return [everything_correct, error_txt, values]


class AdvancedComputingSettings(ctk.CTkFrame):
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
        self.text_help = ("Here are some advanced computing settings :\n\n"
                          "It is possible to choose how many subprocesses to use in multiprocessing. "
                          "Using more subprocesses generally reduce computing time (if use at most one subprocess per "
                          "cpu thread) but increase RAM usage and can prevent the "
                          "use of the computer at the same time, by taking all resources."
                          " By default, the number of subprocesses to use is the number of logical cores in the CPU. "
                          "Numpy can cause some trouble with multiprocessing, forcing all subprocesses to execute on "
                          "same cores, reducing multiprocessing efficiency. An option (activated by default) can be "
                          "used to avoid this behavior."
                          "\n\n"
                          "The selection of tube lens use a thin lens analysis to prepare tube lenses. It is possible "
                          "to use it to pre-filter pairs given their principal distances, to reduce computing time. "
                          "Some pairs can be missed by thin lens analysis."
                          " The pre-filtering by thin lens analysis is enabled by default."
                          " After thin lens analysis, the raytracing analysis is done and pairs are filtered by "
                          "distances."
                          "\n\n"
                          "Cut-off angle is determined for each pair. (It is the maximum field angle which will be able"
                          " to be transmitted by the pair). By default, the cut-off angle determination stop when the"
                          " entering angle is higher than 45° if cut_off_angle_needed_for_the_tube_lens < 35°, and "
                          "2*cut-off_angle_needed_for_the_pair in other cases. "
                          "That mean if the cut-off angle is higher than this value, it will"
                          " be shown as this value. It is possible to change the maximum value to determine for the "
                          "cut-off angle. In all case, it should be higher than the cut-off angle needed for the pair, "
                          "defined before. It is possible to change the precision of the cut-off angle determination "
                          "(better precision will increase computing time). Notice that the cut-off angle would be "
                          "rounded down in exported results."
                          "\n\n"
                          "For wavefront analysis, the RMS will be determined for the field at cut-off angle. "
                          # "If best focus wavefront is ON, the image plane position is at the position which "
                          # "minimize the 0° field RMS wavefront error. If it is OFF, the image distance is the pair back"
                          # " focal length. "
                          "In the case of several wavelengths, rms use for best focus can be the rms "
                          "wavefront error at the reference wavelength, or the rms of each rms wavefront error of each "
                          "wavelengths.\n"
                          "'Polychromatic RMS formula' is the metric used to compare pairs in the case of a "
                          "multi-wavelengths analysis. 'rms' is the root mean square of each rms wavefront error of"
                          " wavelengths"#, and 'worst' is the worst rms wavefront error of each wavelengths. "
                          #"Notice that in all case, if several wavelengths are used, every wavelength wavefront error "
                          "Notice that if several wavelengths are used, every wavelength wavefront error "
                          "maps are computed on the reference sphere of the reference wavelength chief ray."
                          "\n\n"
                          "A first RMS is done on all pairs with a first small ray grid, to be as fast as possible. "
                          "A number of pairs with the best RMS is selected. The best pairs which have a better RMS than"
                          " 1/14 waves are kept to do a second wavefront RMS error analysis, but with more"
                          " rays. An small error in the RMS compared to 1/14 is still accepted to pass from "
                          "first to second RMS determination. The indicated number of rays is the side of the ray grid "
                          "(example: 16 rays => 16x16 ray grid)."
                          )
        self.help = ctk.CTkButton(self.frame, text="?", width=20, height=20, font=font,
                                  command=lambda: self.help_window.create_help_box(self.text_help))
        self.help.grid(row=0, column=0, padx=(0, 10), pady=7)

        try:
            nbcores = str(psutil.cpu_count())
        except:
            nbcores = "int>0"

        self.label_nbsubprocess = ctk.CTkLabel(master=self.frame, font=font, text="Number of subprocesses :  ")
        self.label_nbsubprocess.grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=7, sticky='e')
        self.entry_nbsubprocess = ctk.CTkEntry(self.frame, placeholder_text=nbcores, font=font, width=60)
        self.entry_nbsubprocess.grid(row=1, column=3, columnspan=1, padx=0, sticky='w')
        self.checkbox_affinity_cores = ctk.CTkCheckBox(self.frame, text="Force subprocesses to\n"
                                                                        "execute on different cores", font=font)
        self.checkbox_affinity_cores.grid(row=1, column=4, columnspan=2, padx=20, pady=20)
        self.checkbox_affinity_cores.select()  # default ON

        # thin lens analysis
        self.checkbox_thin_lens_analysis = ctk.CTkCheckBox(self.frame, font=font,
                                                           text="Start geometrical analysis\n"
                                                                "with a thin lens analysis",
                                                           command=self.showhide_entry_error_thin_lens)
        self.checkbox_thin_lens_analysis.grid(row=2, column=0, padx=10, pady=(7,20))
        self.checkbox_thin_lens_analysis.select()  # default ON
        self.label_error_thin_lens = ctk.CTkLabel(master=self.frame, font=font, text="Accepted error in thin\n"
                                                                                     "lens analysis distances [%]:  ")
        self.label_error_thin_lens.grid(row=2, column=1, columnspan=2, padx=(20, 0), pady=7, sticky='e')
        self.entry_error_thin_lens = ctk.CTkEntry(self.frame, placeholder_text="0", font=font, width=60)
        self.entry_error_thin_lens.grid(row=2, column=3, columnspan=1, padx=0, sticky='w')
        #self.label_error_thin_lens.grid_remove()  # default hidden
        #self.entry_error_thin_lens.grid_remove()  # default hidden

        # wavefront analysis
        self.label_wvf_poly_rms_formula = ctk.CTkLabel(master=self.frame, font=font, text="Polychromatic RMS formula")
        self.label_wvf_poly_rms_formula.grid(row=3, column=0, padx=(20, 0), pady=30, sticky='e')

        self.optionmenu_wvf_poly_rms_formula = ctk.CTkOptionMenu(self.frame, font=font,
                                                                 values=["rms"])#, "worst"])
        self.optionmenu_wvf_poly_rms_formula.grid(row=3, column=1, columnspan=2, padx=10, pady=7, sticky='w')
        self.optionmenu_wvf_poly_rms_formula.set("rms")
        # self.checkbox_best_focus_wvf = ctk.CTkCheckBox(self.frame, font=font,
        #                                                command=self.activate_deactivate_focuspoly,
        #                                                text="Best focus wavefront 0°")
        # self.checkbox_best_focus_wvf.grid(row=4, column=0, columnspan=2, padx=10, pady=7)
        # self.checkbox_best_focus_wvf.select()  # default ON

        self.label_wvf_focuspoly = ctk.CTkLabel(master=self.frame, font=font, text="Best focus polychromatic")
        self.label_wvf_focuspoly.grid(row=4, column=2, padx=(20, 0), pady=30, sticky='e')

        self.optionmenu_wvf_focuspoly = ctk.CTkOptionMenu(self.frame, font=font,
                                                          values=["reference wavelength", "rms"])
        self.optionmenu_wvf_focuspoly.grid(row=4, column=3, columnspan=2, padx=10, pady=7, sticky='w')
        self.optionmenu_wvf_focuspoly.set("reference wavelength")
        # focus_polychromatic

        # wavefront analysis - best pairs
        self.label_nb_best_pairs = ctk.CTkLabel(master=self.frame, font=font, text="Max number of pairs selected\n"
                                                                                   "for second RMS comparison :  ")
        self.label_nb_best_pairs.grid(row=5, column=0, padx=(10, 0), pady=7, sticky='e')
        self.entry_nb_best_pairs = ctk.CTkEntry(self.frame, placeholder_text="10", font=font, width=60)
        self.entry_nb_best_pairs.grid(row=5, column=1, columnspan=1, padx=0, sticky='w')

        self.label_error_best_pairs = ctk.CTkLabel(master=self.frame, font=font, text="Accepted RMS error with diffraction\n"
                                                                                      "limit for second comparison [%] :  ")
        self.label_error_best_pairs.grid(row=5, column=3, columnspan=2, padx=(10, 0), pady=20, sticky='e')
        self.entry_error_best_pairs_RMS = ctk.CTkEntry(self.frame, placeholder_text="5", font=font, width=60)
        self.entry_error_best_pairs_RMS.grid(row=5, column=5, columnspan=1, padx=0, sticky='w')


        # wavefront analysis - nb rays
        self.label_nbrays1 = ctk.CTkLabel(master=self.frame, font=font, text="Number of rays used in\n"
                                                                             "RMS for first comparison :")
        self.label_nbrays1.grid(row=6, column=0, padx=(10, 0), pady=7, sticky='e')
        self.entry_nbrays1 = ctk.CTkEntry(self.frame, placeholder_text="16", font=font, width=60)
        self.entry_nbrays1.grid(row=6, column=1, columnspan=1, padx=0, sticky='w')

        self.label_nbrays2 = ctk.CTkLabel(master=self.frame, font=font, text="Number of rays used in\n"
                                                                             "RMS for second comparison :")
        self.label_nbrays2.grid(row=6, column=3, columnspan=2, padx=(10, 0), pady=20, sticky='e')
        self.entry_nbrays2 = ctk.CTkEntry(self.frame, placeholder_text="64", font=font, width=60)
        self.entry_nbrays2.grid(row=6, column=5, columnspan=1, padx=0, sticky='w')


        # cut-off angle
        self.label_cutoff_end = ctk.CTkLabel(master=self.frame, font=font, text="Cut-off angle test end [°] :")
        self.label_cutoff_end.grid(row=7, column=0, padx=(10, 0), pady=7, sticky='e')
        self.entry_cutoff_end = ctk.CTkEntry(self.frame, placeholder_text="float", font=font, width=60)
        self.entry_cutoff_end.grid(row=7, column=1, columnspan=1, padx=0, sticky='w')

        self.label_cutoff_precision = ctk.CTkLabel(master=self.frame, font=font, text="Cut-off angle precision [°] :")
        self.label_cutoff_precision.grid(row=7, column=3, columnspan=2, padx=(10, 0), pady=20, sticky='e')
        self.entry_cutoff_precision = ctk.CTkEntry(self.frame, placeholder_text="0.1", font=font, width=60)
        self.entry_cutoff_precision.grid(row=7, column=5, columnspan=1, padx=0, sticky='w')


        # ram settings
        self.label_save_ram = ctk.CTkLabel(master=self.frame, font=font, text="Save computer RAM")
        self.label_save_ram.grid(row=8, column=0, padx=(20, 0), pady=20, sticky='e')
        self.optionmenu_save_ram = ctk.CTkOptionMenu(self.frame, font=font,
                                                     values=["max"])
                                                     # values=["no", "medium", "max"])
        self.optionmenu_save_ram.grid(row=8, column=1, columnspan=2, padx=10, pady=7, sticky='w')
        self.optionmenu_save_ram.set("max")

    def get_values(self):
        # this function check if all fields have the right type of values (int is int etc)
        # and return [everything_correct, error_txt, values]

        # obtain all fields
        values = {'nb_subprocesses': self.entry_nbsubprocess.get(),
                  'force_affinity_core': self.checkbox_affinity_cores.get(),
                  'thin_lens_first_analysis': self.checkbox_thin_lens_analysis.get(),
                  'tolerance_prcent': self.entry_error_thin_lens.get(),
                  'polychromatic': self.optionmenu_wvf_poly_rms_formula.get(),
                  'focus_polychromatic': self.optionmenu_wvf_focuspoly.get(),
                  'best_focus_fast': True,#self.checkbox_best_focus_wvf.get(),
                  'nbRays_first_comparison': self.entry_nbrays1.get(),
                  'nbRays_high_comparison': self.entry_nbrays2.get(),
                  'number_best_pair_high_comparison': self.entry_nb_best_pairs.get(),
                  'tolerance_wavefront_RMS_high_percent': self.entry_error_best_pairs_RMS.get(),
                  'cut_off_angle_test_end': self.entry_cutoff_end.get(),
                  'cut_off_angle_precision': self.entry_cutoff_precision.get(),
                  'save_ram' : self.optionmenu_save_ram.get()}

        # initialisation
        everything_correct = True
        error_txt = ''

        # put back all borders well (see below)
        self.entry_nbsubprocess.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_error_thin_lens.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_nbrays1.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_nbrays2.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_nb_best_pairs.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_error_best_pairs_RMS.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_cutoff_end.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        self.entry_cutoff_precision.configure(border_color=['#979DA2', '#565B5E'], border_width=2)

        # check if everything is correct (and change wrong field appearance)
        if values['nb_subprocesses'] == '':
            values['nb_subprocesses'] = psutil.cpu_count()
        else:
            try:
                values['nb_subprocesses'] = int(values['nb_subprocesses'])
            except:
                everything_correct = False
                error_txt = error_txt + "The subprocess number should be an int or nothing.\n"
                self.entry_nbsubprocess.configure(border_color='red', border_width=4)

        if values['thin_lens_first_analysis']:
            if values['tolerance_prcent'] == '':
                values['tolerance_prcent'] = 0
            else:
                try:
                    values['tolerance_prcent'] = float(values['tolerance_prcent'])
                except:
                    everything_correct = False
                    error_txt = error_txt + "The tolerance in thin lens distances should be a float or nothing.\n"
                    self.entry_error_thin_lens.configure(border_color='red', border_width=4)

        if values['nbRays_first_comparison'] == '':
            values['nbRays_first_comparison'] = 16
        else:
            try:
                values['nbRays_first_comparison'] = int(values['nbRays_first_comparison'])
            except:
                everything_correct = False
                error_txt = error_txt + "The ray grid size for RMS wavefront error should be an int or nothing.\n"
                self.entry_nbrays1.configure(border_color='red', border_width=4)

        if values['nbRays_high_comparison'] == '':
            values['nbRays_high_comparison'] = 64
        else:
            try:
                values['nbRays_high_comparison'] = int(values['nbRays_high_comparison'])
            except:
                everything_correct = False
                error_txt = error_txt + "The ray grid size for RMS wavefront error should be an int or nothing.\n"
                self.entry_nbrays2.configure(border_color='red', border_width=4)

        if values['number_best_pair_high_comparison'] == '':
            values['number_best_pair_high_comparison'] = 10
        else:
            try:
                values['number_best_pair_high_comparison'] = int(values['number_best_pair_high_comparison'])
            except:
                everything_correct = False
                error_txt = error_txt + "The number of best pairs for RMS wavefront error should be an int or nothing.\n"
                self.entry_nb_best_pairs.configure(border_color='red', border_width=4)

        if values['tolerance_wavefront_RMS_high_percent'] == '':
            values['tolerance_wavefront_RMS_high_percent'] = 10
        else:
            try:
                values['tolerance_wavefront_RMS_high_percent'] = float(values['tolerance_wavefront_RMS_high_percent'])
            except:
                everything_correct = False
                error_txt = error_txt + "The error in RMS wavefront error for best pairs should be a float or nothing.\n"
                self.entry_error_best_pairs_RMS.configure(border_color='red', border_width=4)

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
            case "worst":
                values['polychromatic'] = 'worst'
            case "rms":
                values['polychromatic'] = 'rmse_rms'
            case _ :
                pass

        return [everything_correct, error_txt, values]

    def showhide_entry_error_thin_lens(self):
        # show or hide the frame with advanced parameters
        state = self.checkbox_thin_lens_analysis.get()
        if state == 0:  # OFF
            self.label_error_thin_lens.grid_remove()
            self.entry_error_thin_lens.grid_remove()  # hide the frame
        else:  # ON
            self.label_error_thin_lens.grid()
            self.entry_error_thin_lens.grid()  # show the frame

    def activate_deactivate_focuspoly(self):
        if self.checkbox_best_focus_wvf.get() :
            self.optionmenu_wvf_focuspoly.configure(state="normal")
        else:
            self.optionmenu_wvf_focuspoly.configure(state="disabled")


def check_entry_type (entry, constructor_type=float, error_txt_type='',
                      sup=None, error_txt_sup='', inf=None, error_txt_inf=''):
    error_txt = ''
    everything_correct = True
    try:
        value = constructor_type(entry.get())
        entry.configure(border_color=['#979DA2', '#565B5E'], border_width=2)

        if (sup is not None) and (value>sup):
            error_txt = error_txt + error_txt_sup
            everything_correct = False
            entry.configure(border_color='red', border_width=4)
        if (inf is not None) and (value<inf):
            error_txt = error_txt + error_txt_inf
            everything_correct = False
            entry.configure(border_color='red', border_width=4)
    except:
        everything_correct = False
        error_txt = error_txt + error_txt_type
        entry.configure(border_color='red', border_width=4)
        value = ''
    return everything_correct, error_txt, value


def check_entry_min_max(entry_min, entry_max, default_value_min=None, default_value_max=None, default_values=False,
                        values_type_constructor=float, error_txt_min='', error_txt_max='', error_txt_min_sup_max='') :
    # This function took two fields which should be float or int and min <= max
    # It extract values from customtkinter entries min and max and check them. Boarders of entries are modified if an
    # error occurred.

    error_txt=''
    everything_correct = True

    entry_min_input = entry_min.get()
    entry_max_input = entry_max.get()

    # get min value
    if default_values and entry_min_input == '':
        # if nothing in the field : get default value
        entry_min_out = default_value_min
    else:
        try:
            # check if value can be of type values_type_constructor, and put the gui entry field to the normal color
            entry_min_out = values_type_constructor(entry_min_input)
            entry_min.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
        except:
            # if value is not of type values_type_constructor, highlight in red its gui entry field + error text
            entry_min_out = ''
            everything_correct = False
            error_txt = error_txt + error_txt_min
            entry_min.configure(border_color='red', border_width=4)

    # get max value
    if default_values and entry_max_input == '':
        entry_max_out = default_value_max
    else:
        try:
            entry_max_out = values_type_constructor(entry_max_input)
            entry_max.configure(border_color=['#979DA2', '#565B5E'], border_width=2)
            get_max_value = True
        except:
            entry_max_out = ''
            everything_correct = False
            error_txt = error_txt + error_txt_max
            entry_max.configure(border_color='red', border_width=4)

    # check min <= max
    if (entry_min_out is float or entry_min_out is int) and (entry_max_out is float or entry_max_out is int):
        if not is_between(entry_max_out, entry_min_out):
            everything_correct = False
            error_txt = error_txt + error_txt_min_sup_max
            entry_min.configure(border_color='red', border_width=4)
            entry_max.configure(border_color='red', border_width=4)

    return [everything_correct, error_txt, entry_min_out, entry_max_out]

