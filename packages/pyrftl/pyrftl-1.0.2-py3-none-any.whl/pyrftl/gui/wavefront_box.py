import tkinter
import customtkinter as ctk

from pyrftl.func.wavefront_pair_analysis import wvf_fast_one_pair


class WavefrontConfig(ctk.CTkToplevel):
    # window to display help
    def __init__(self, pair_detail_obj, *args, **kwargs):
        super().__init__()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title('WavefrontConfig')
        self.geometry("400x300")

        self.pair_detail_obj = pair_detail_obj  # to be able to know current pair

        if "font" in kwargs and kwargs['font'] is not None:
            font = kwargs["font"]
        else:
            font = ctk.CTkFont(size=15)

        # create a frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        # self.main_frame.pack(fill=tkinter.BOTH, expand=True)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.main_label = ctk.CTkLabel(self.main_frame, font=font, text="Please select parameters for wavefront.")
        self.main_label.grid(row=0, column=0, padx=5, pady=1, columnspan=3, sticky="w")

        self.label_angle = ctk.CTkLabel(self.main_frame, font=font, text="Field angle [°]")
        self.label_angle.grid(row=2, column=0, padx=5, pady=1, sticky="w")
        cut_off_angle = str(self.pair_detail_obj.param['cut_off_angle_min'])
        self.entry_angle = ctk.CTkEntry(self.main_frame, placeholder_text=cut_off_angle, font=font, width=70)
        self.entry_angle.grid(row=2, column=1, columnspan=1, padx=0, pady=1, sticky="w")

        self.label_grid = ctk.CTkLabel(self.main_frame, font=font, text="Grid side size")
        self.label_grid.grid(row=3, column=0, padx=5, pady=1, sticky="w")
        grid = str(max(self.pair_detail_obj.param['nbRays_first_comparison'],
                       self.pair_detail_obj.param['nbRays_high_comparison']))
        self.entry_grid = ctk.CTkEntry(self.main_frame, placeholder_text=grid, font=font, width=70)
        self.entry_grid.grid(row=3, column=1, columnspan=1, padx=0, pady=1, sticky="w")

        self.checkbox_cyclic = ctk.CTkCheckBox(self.main_frame, text="Display cyclic 1 wave", font=font)
        self.checkbox_cyclic.grid(row=4, column=0, padx=10, pady=1)
        self.checkbox_cyclic.select()  # default ON

        self.checkbox_bestfocus = ctk.CTkCheckBox(self.main_frame, text="Best RMS focus for angle [°]", font=font,
                                                  command=self.checkbox_bestfocus_command)
        self.checkbox_bestfocus.grid(row=5, column=0, padx=0, pady=1)
        self.checkbox_bestfocus.select()  # default ON
        self.entry_bestfocus = ctk.CTkEntry(self.main_frame, placeholder_text="0", font=font, width=70)
        self.entry_bestfocus.grid(row=5, column=1, columnspan=1, padx=0, pady=1, sticky="w")

        self.label_wvf_poly_rms_formula = ctk.CTkLabel(master=self.main_frame, font=font, text="Polychromatic RMS formula")
        self.label_wvf_poly_rms_formula.grid(row=7, column=0, padx=0, pady=1, sticky='e')

        self.optionmenu_wvf_poly_rms_formula = ctk.CTkOptionMenu(self.main_frame, font=font,
                                                                 values=["rms", "worst"])
        self.optionmenu_wvf_poly_rms_formula.grid(row=7, column=1, columnspan=2, padx=0, pady=1, sticky='w')
        self.optionmenu_wvf_poly_rms_formula.set("rms")

        self.label_wvf_focuspoly = ctk.CTkLabel(master=self.main_frame, font=font, text="Best focus polychromatic")
        self.label_wvf_focuspoly.grid(row=6, column=0, padx=0, pady=1, sticky='e')

        self.optionmenu_wvf_focuspoly = ctk.CTkOptionMenu(self.main_frame, font=font,
                                                          values=["reference wavelength", "rms"])
        self.optionmenu_wvf_focuspoly.grid(row=6, column=1, columnspan=2, padx=0, pady=1, sticky='w')
        self.optionmenu_wvf_focuspoly.set("reference wavelength")

        self.label_focus = ctk.CTkLabel(self.main_frame, font=font, text="Focus [mm]")
        self.label_focus.grid(row=8, column=0, padx=5, pady=1, sticky="w")
        self.entry_focus = ctk.CTkEntry(self.main_frame, placeholder_text="0", font=font, width=70)
        self.entry_focus.grid(row=8, column=1, columnspan=1, padx=0, pady=1, sticky="w")
        self.label_focus.grid_remove()
        self.entry_focus.grid_remove()

        self.button_start = ctk.CTkButton(self.main_frame, text="Start", width=20, height=20, font=font,
                                          command=self.start)
        self.button_start.grid(row=9, column=0, columnspan=1, padx=0, pady=1, sticky="w")

        self.error_textbox = ctk.CTkTextbox(self.main_frame, wrap="word", font=font, width=200, height=71,
                                            fg_color="transparent", text_color="red")
        self.error_textbox.grid(row=9, column=1, padx=0, pady=5, columnspan=2, sticky="w")
        self.error_textbox.configure(state="disabled")

    def checkbox_bestfocus_command(self):
        # hide or display label and entry
        state = self.checkbox_bestfocus.get()
        if state == 0:  # OFF
            self.entry_bestfocus.grid_remove()  # hide the frame
            self.label_wvf_focuspoly.grid_remove()
            self.optionmenu_wvf_focuspoly.grid_remove()
            self.label_focus.grid()
            self.entry_focus.grid()
        else:  # ON
            self.entry_bestfocus.grid()  # show the frame
            self.label_wvf_focuspoly.grid()
            self.optionmenu_wvf_focuspoly.grid()
            self.label_focus.grid_remove()
            self.entry_focus.grid_remove()

    def check_entry(self):
        everything_correct = True
        error_txt = ''

        best_focus = self.checkbox_bestfocus.get()
        cyclic = self.checkbox_cyclic.get()

        wvf_angle_entry = self.entry_angle.get()
        if wvf_angle_entry == '':
            wvf_angle = self.pair_detail_obj.param['cut_off_angle_min']
        else :
            try:
                wvf_angle = float(self.entry_angle.get())
            except:
                wvf_angle = None
                everything_correct = False
                error_txt = error_txt + 'Wavefront angle should be a float or nothing. '

        if best_focus:
            focus_dist = None
            focus_angle_entry = self.entry_bestfocus.get()
            if focus_angle_entry == '':
                focus_angle = 0
            else:
                try:
                    focus_angle = float(self.entry_bestfocus.get())
                except:
                    focus_angle = None
                    everything_correct = False
                    error_txt = error_txt + 'Focus angle should be a float or nothing. '
        else :
            focus_angle = None
            focus_dist_entry = self.entry_focus.get()
            if focus_dist_entry == '':
                focus_dist = 0
            else :
                try :
                    focus_dist = float(self.entry_focus.get())
                except:
                    focus_dist = None
                    everything_correct = False
                    error_txt = error_txt + 'Focus distance should be a float or nothing. '

        entry_grid = self.entry_grid.get()
        if entry_grid == '':
            grid = max(self.pair_detail_obj.param['nbRays_first_comparison'],
                       self.pair_detail_obj.param['nbRays_high_comparison'])
        else :
            try:
                grid = int(entry_grid)
            except:
                grid = None
                everything_correct = False
                error_txt = error_txt + 'Grid side size should be an integer or nothing. '

        focus_polychromatic = self.optionmenu_wvf_focuspoly.get()
        match focus_polychromatic :
            case 'reference wavelength' :
                focus_polychromatic = 'ref_wvl_i'
            case "rms":
                focus_polychromatic = 'rmse_rms'
            case _ :
                pass

        polychromatic = self.optionmenu_wvf_poly_rms_formula.get()
        match polychromatic :
            case "rms":
                polychromatic = 'rmse_rms'
            case _ :
                pass

        dic_entry = {'wvf_angle':wvf_angle, 'focus_dist':focus_dist, 'focus_angle':focus_angle, 'grid':grid,
                     'best_focus': best_focus, 'cyclic': cyclic, 'polychromatic':polychromatic,
                     'focus_polychromatic':focus_polychromatic}

        # show error text
        self.change_text(error_txt)

        return [everything_correct, error_txt, dic_entry]

    def change_text(self, text):
        # show error text
        self.error_textbox.configure(state="normal")  # configure textbox to be modifiable
        self.error_textbox.delete("0.0", "end")  # delete all text
        self.error_textbox.insert("0.0", text)  # add text
        self.error_textbox.configure(state="disabled")  # configure textbox to be read-only

    def start(self):
        everything_correct, error_txt, dic_entry = self.check_entry()

        try :
            if everything_correct :
                # check if need to recompute wavefront or just change the focus
                pair = self.pair_detail_obj.pair

                # compute the wavefront
                param = {'best_focus_fast':dic_entry['best_focus'],
                         'cut_off_angle_min':dic_entry['wvf_angle'], 'save_ram':'no',
                         'focus_polychromatic':dic_entry['focus_polychromatic'],
                         'polychromatic':dic_entry['polychromatic']}

                self.change_text('Processing, please wait...')
                self.update()
                wvf_fast_one_pair(pair, param, nb_rays=dic_entry['grid'], best_focus_angle=dic_entry['focus_angle'],
                                  focus_dist=dic_entry['focus_dist'])
                self.change_text("")

                # print RMS
                print('______________RMS WAVEFRONT ERROR______________')
                print('Pair : ' + pair.short_name)
                print()

                if dic_entry['best_focus']:
                    print('Best focus RMS at angle (°) : ' + str(dic_entry['focus_angle']))
                    print('Focus [mm] : ' + str(pair.rms_detail[0]['foc']))
                    print('Wavefront RMS displayed at angle (°) : ' + str(dic_entry['wvf_angle']))
                    print('Grid side size : ' + str(dic_entry['grid']))
                else :
                    print('Focus [mm] : ' + str(dic_entry['focus_dist']))
                    print('Wavefront RMS displayed at angle (°) : ' + str(dic_entry['wvf_angle']))
                    print('Grid side size : ' + str(dic_entry['grid']))
                print()

                for rms_data in pair.rms_detail :
                    print('Field : ' + str(rms_data['used_fld']))
                    print('Wavelength : ' + str(rms_data['used_wvl']))
                    print('Grid : ' + str(rms_data['grid size']))
                    print('RMS : ' + str(rms_data['RMS']))
                    print('P-V : ' + str(rms_data['P-V']))
                    if rms_data['polychromatic'] is not None :
                        print('RMS polychromatic formula : ' + rms_data['polychromatic'])
                    print()

                print('_______________________________________________')

                # open matplotlib windows with wavefront
                pair.disp_wavefront(cyclic=dic_entry['cyclic'])
        except Exception as exception :
            raise exception
            print('Impossible to display the wavefront, error is :\n' + str(exception))


class WavefrontConfigMain :
    # class that can create a WavefrontConfig windows (a windows to select parameters to display a wavefront)
    def __init__(self, pair_detail_obj, font=None):
        self.wavefrontconfig = None
        self.font = font
        self.last_compute = {'pair_short_name':None, 'fld angle':None, 'foc':None, 'grid':None}
        self.pair = None
        self.pair_detail_obj = pair_detail_obj

    def create_wavefrontconfig(self, font=None):
        if (not hasattr(self, 'wavefrontconfig')) or (self.wavefrontconfig is None) or (not self.wavefrontconfig.winfo_exists()):
            if font is None and self.font is not None :
                font = self.font

            self.wavefrontconfig = WavefrontConfig(self.pair_detail_obj, font=font)  # create window if its None or destroyed
            self.wavefrontconfig.after(100, self.wavefrontconfig.focus)  # Workaround for bug where main window takes focus
        else:
            self.wavefrontconfig.focus()
