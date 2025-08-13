import tkinter
import customtkinter as ctk
import numpy as np

# from rayoptics.environment import FieldSpec
import matplotlib.pyplot as plt

from pyrftl.gui.helpbox import HelpWindowMain, create_help_box
from pyrftl.func.save import sort_pair_rms, detail_seq_model_str
from pyrftl.func.pairs import Pair
from pyrftl.func.various_stuff import pair_df_2_lens_config
from pyrftl.gui.wavefront_box import WavefrontConfigMain


class PairDfDetail(ctk.CTkFrame):
    def __init__(self, master, pair_dataframe, pair_dic, lenses_list, param=None,
                 help_window=None, **kwargs):
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

        self.pair_df = pair_dataframe
        self.pair_dic = pair_dic
        self.lenses_list = lenses_list
        self.param = param

        if param is not None :
            try:
                self.label_result_directory = ctk.CTkLabel(self.main_frame, font=font,
                                                           text= "Results are exported in : \n" + param['save_folder_path'])
                self.label_result_directory.grid(row=0, column=0, padx=5, pady=1, columnspan=3, sticky="w")
            except Exception as exception:
                pass

        self.textbox_pair_short_info = ctk.CTkTextbox(self.main_frame, wrap="word", font=font, width=500,
                                                      height=80)
        self.textbox_pair_short_info.grid(row=1, column=0, padx=5, pady=(0,10), columnspan=2, sticky="w")
        self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only

        self.button_change_pair = ctk.CTkButton(self.main_frame, text="Change pair", command=self.change_pair_menu,
                                                font=font)
        self.button_change_pair.grid(row=1, column=2, padx=10, pady=(10,30), sticky='n')

        if pair_dataframe is None :
            self.button_change_pair.configure(state="disabled")
            self.textbox_pair_short_info.configure(state="normal")  # configure textbox to be modifiable
            self.textbox_pair_short_info.insert("0.0", 'No pair has been selected !\n'
                                                       'Please change your criteria')  # add text
            self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only

        else:
            # some pairs have been selected. Detect the best one and display it
            self.pair_detail_frame = ctk.CTkFrame(self.main_frame)
            self.pair_detail_frame.grid(row=2, column=0, columnspan=3)
            self.pair_detail_obj = PairDetail(self.pair_detail_frame, param=param, help_window=help_window)

            # get best pair
            if self.pair_df.iloc[0].at['<lambda/14'] :  # better rms than diffraction
                self.change_pair(self.pair_df.index[0])
                self.best_pair_sn = self.pair_df.index[0]
            else :  # lower rms than diffraction
                self.best_pair_sn = None
                self.textbox_pair_short_info.configure(state="normal")  # configure textbox to be modifiable
                self.textbox_pair_short_info.insert("0.0", 'No pair has a better rms than 1/14 !\n'
                                                           'Please change your criteria\n')  # add text
                self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only

    def change_pair_menu(self):
        dialog_box = ctk.CTkInputDialog(text="Enter pair short name:", title="Change displayed pair")
        pair_sn = dialog_box.get_input()

        if pair_sn in self.pair_df.index :
            self.change_pair(pair_sn)
        else:
            txt = ('Please select a correct pair short name\n'
                   'see csv file for the list of them. Please respect letter case.'
                   '   best (if exist) is : ' + str(self.best_pair_sn))
            self.change_txt_short_info_box(txt)

            self.pair_detail_obj.pair = None
            self.pair_detail_obj.update_textbox()

    def change_pair(self, pair_short_name):
        # change the displayed pair in PairDetail
        if pair_short_name not in self.pair_df.index :
            txt = 'Error, no pair named : ' + pair_short_name
            self.change_txt_short_info_box(txt)
            self.pair_detail_obj.pair = None
            self.pair_detail_obj.update_textbox()

        else:
            # change information in the short info box
            txt = ('pair : ' + pair_short_name + '  : ' +
                   self.pair_df.at[pair_short_name, 'lens1 filename'] + ' --> ' +
                   self.pair_df.at[pair_short_name, 'lens2 filename'] + ' config ' +
                   self.pair_df.at[pair_short_name, 'config'])
            txt = txt + '\ncut-off angle : ' + str(self.pair_df.at[pair_short_name, 'cut-off angle']) + '°   '

            if self.pair_df.at[pair_short_name, 'second analysis RMS wavefront error'] is None:
                rms = self.pair_df.at[pair_short_name, 'first analysis RMS wavefront error']
                grid = str(self.param['nbRays_first_comparison'])
            else:
                rms = self.pair_df.at[pair_short_name, 'second analysis RMS wavefront error']
                grid = str(self.param['nbRays_high_comparison'])
            txt = txt + 'rms grid ' + grid + ' : ' + f'{rms:.3g}' + ' waves'

            self.change_txt_short_info_box(txt)

            # change the displayed pair in pair_detail_obj (big info box + response to buttons with ray tracing etc)
            if hasattr(self.pair_dic, pair_short_name):
                # pair already exist in the dictionary
                self.pair_detail_obj.pair = pair = self.pair_dic[pair_short_name]
            else:
                # pair not in the dictionary, need to (re)create it from the dataframe indications (to have more info
                # than just the ones in the dataframe, else can just use the csv file if dataframe infos are enough...)
                self.pair_detail_obj.update_textbox("Computing...")

                # took infos from the dataframe to be able to create the pair
                config, lens1, lens2 = pair_df_2_lens_config(self.pair_df, pair_short_name, self.lenses_list)

                # create the pair
                pair = Pair(lens1, lens2, self.param['expected_focal_length'], None,
                            {'lens1 id :', lens1.id, 'lens2 id :', lens2.id})
                pair.create_optical_model(config=config, wvl_and_weight=self.param['wvl_and_weight'],
                                          pupil=self.param['pupil'], fld=[0],
                                          dist_pupil_pair=self.param['dist_pupil_pair'])

                self.pair_detail_obj.pair = self.pair_dic[pair_short_name] = pair
            self.pair_detail_obj.update_textbox()

    def change_txt_short_info_box(self, txt):
        self.textbox_pair_short_info.configure(state="normal")  # configure textbox to be modifiable
        self.textbox_pair_short_info.delete("0.0", "end")
        self.textbox_pair_short_info.insert("0.0", txt)  # add text
        self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only


class PairOneDetail(ctk.CTkFrame):
    def __init__(self, master, pair, param_one, help_window=None, **kwargs):
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

        self.pair = pair
        rms = pair.rms_detail[0]['RMS']
        grid = pair.rms_detail[0]['grid size']
        cut_off = pair.cutoffangle['value']
        self.param_one = param_one

        self.textbox_pair_short_info = ctk.CTkTextbox(self.main_frame, wrap="word", font=font, width=700,
                                                      height=80)
        self.textbox_pair_short_info.grid(row=1, column=0, padx=5, pady=(0,10), columnspan=2, sticky="w")
        txt = ("pair : " + pair.name() +
               "\nCut-Off angle [°]: " + str(cut_off) + "\nRMS grid " + str(grid) + " : " +
               "{0:.3g}".format(rms) + " waves")

        self.change_txt_short_info_box(txt)

        self.pair_detail_frame = ctk.CTkFrame(self.main_frame)
        self.pair_detail_frame.grid(row=2, column=0, columnspan=3)
        self.pair_detail_obj = PairDetail(self.pair_detail_frame, pair=pair, param=param_one, help_window=help_window)

    def change_txt_short_info_box(self, txt):
        self.textbox_pair_short_info.configure(state="normal")  # configure textbox to be modifiable
        self.textbox_pair_short_info.delete("0.0", "end")
        self.textbox_pair_short_info.insert("0.0", txt)  # add text
        self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only


class PairDetail(ctk.CTkFrame):
    # frame with a textbox which show some details of the pair, and with buttons to disp the wavefront, the ray diagram,
    # to save it etc
    def __init__(self, master, pair=None, new_frame=False, param=None, help_window=None, **kwargs):
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

        self.font=font

        if help_window is not None:
            self.help_window = help_window
        else:
            self.help_window = HelpWindowMain(font)

        self.wavefront_box = WavefrontConfigMain(pair_detail_obj=self, font=font)

        self.label_details_text = ctk.CTkLabel(self.frame, font=font, text="Pair details :")
        self.label_details_text.grid(row=0, column=0, padx=5, pady=1, columnspan=2, sticky="w")

        self.textbox_details = ctk.CTkTextbox(self.frame, wrap="word", width=700, height=400,
                                              font=ctk.CTkFont(family="Lucida Console", size=14))
                                              # font with same space for all characters
        self.textbox_details.grid(row=0, column=0, padx=5, pady=(0,10), columnspan=5, sticky="w")
        self.textbox_details.configure(state="disabled")  # configure textbox to be read-only

        self.pair = pair
        self.param = param

        self.update_textbox()

        self.button_ray = ctk.CTkButton(self.frame, text="Ray diagram", command=self.raydiagram, font=font)
        self.button_ray.grid(row=1, column=0, padx=10, pady=(10,30), sticky='n')

        self.button_wvf = ctk.CTkButton(self.frame, text="Wavefront", command=self.wavefront, font=font)
        self.button_wvf.grid(row=1, column=1, padx=10, pady=(10,30), sticky='n')

        self.button_wvf = ctk.CTkButton(self.frame, text="Save pair .roa", command=self.save_roa, font=font)
        self.button_wvf.grid(row=1, column=2, padx=10, pady=(10,30), sticky='n')

    def update_textbox(self, txt=None):
        if type(txt) is not str :
            if self.pair is None :
                detail_txt = ('No pair selected, nothing to display !\n'
                              'Please use the "Change pair" button to select a pair.')
            else:
                detail_txt = detail_seq_model_str(self.pair)
        else:
            detail_txt = txt

        self.textbox_details.configure(state="normal")  # configure textbox to be modifiable
        self.textbox_details.delete("0.0", "end")  # delete all text
        self.textbox_details.insert("0.0", detail_txt)  # add text
        self.textbox_details.configure(state="disabled")  # configure textbox to be read-only

    def change_pair(self, new_pair):
        self.pair = new_pair
        self.update_textbox()

    def raydiagram(self):
        # display the pair ray tracing diagram
        if self.pair is not None:
            try :
                dialog_box = ctk.CTkInputDialog(text="Enter field angle (°):",
                                                title="Ray diagram")
                angle = dialog_box.get_input()

                try:
                    angle_float = float(angle)
                except:
                    if self.param is not None:
                        angle_float = self.param['cut_off_angle_min']
                    else:
                        angle_float = 0

                self.pair.change_field_angle(angle_float)

                self.pair.disp_raytracing()
            except Exception as exception:
                print('Impossible to display the ray diagram because of this error :\n'
                      + str(exception))

    def wavefront(self):
        if self.pair is not None:
            try :
                self.wavefront_box.create_wavefrontconfig(font=self.font)
            except Exception as exception :
                print('oups')
                print(exception)

    def save_roa(self):
        try:
            filepath = tkinter.filedialog.asksaveasfilename(defaultextension='.roa')
            self.pair.opm.save_model(filepath)
        except:
            pass



