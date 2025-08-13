import tkinter
import customtkinter as ctk
import numpy as np
import contextlib, io  # to be able to capture stdout entry, so what is print(...) by a module

from rayoptics.environment import *
import matplotlib.pyplot as plt

from pyrftl.gui.helpbox import HelpWindowMain, create_help_box
from pyrftl.func.save import detail_seq_model_str
from pyrftl.gui.frame import Frame

from opticalglass.schott import SchottGlass
from opticalglass.ohara import OharaGlass
from opticalglass.cdgm import CDGMGlass
from opticalglass.hikari import HikariGlass
from opticalglass.hoya import HoyaGlass
from opticalglass.sumita import SumitaGlass


class RoaFileSelect(ctk.CTkFrame):
    def __init__(self, master, help_window=None, **kwargs):
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

        self.textbox_pair_short_info = ctk.CTkTextbox(self.main_frame, wrap="word", font=font, width=500,
                                                      height=60)
        self.textbox_pair_short_info.grid(row=1, column=0, padx=5, pady=(0,10), columnspan=2, sticky="w")
        self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only

        self.button_open_file = ctk.CTkButton(self.main_frame, text="Open roa file", command=self.open_roa_file,
                                                font=font)
        self.button_open_file.grid(row=1, column=2, padx=10, pady=(10,30), sticky='n')

        self.textbox_pair_short_info.configure(state="normal")  # configure textbox to be modifiable
        self.textbox_pair_short_info.insert("0.0", 'Please select a .roa file to be displayed.')  # add text
        self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only

        # frame to show the model
        self.opm_detail_frame = ctk.CTkFrame(self.main_frame)
        self.opm_detail_frame.grid(row=2, column=0, columnspan=3)
        self.opm_detail_frame.grid_remove()  # hide frame
        self.opm_detail_obj = OPMDetail(self.opm_detail_frame, opm=None, help_window=self.help_window)


    def open_roa_file(self):
        # get the filepath of the model file to open
        filepath = tkinter.filedialog.askopenfilename(filetypes=[("RayOptics", ".roa")])
        print(filepath)

        try:
            if filepath == '' :
                # cancel the selection of a file
                pass
            else :
                self.filepath = filepath
                # open the optical model
                opm = open_model(self.filepath)
                print(opm)

                # change the displayed informations
                self.opm_detail_obj.change_opm(opm)

                # show the frame if it was hidden
                self.opm_detail_frame.grid()

                # change information in the short info box
                txt = self.filepath

        except Exception as exception:
            txt = 'Error when try to open ' + filepath + '\nError is : ' + str(exception)

            # hide the optical model frame
            self.opm_detail_frame.grid_remove()
            self.opm_detail_obj.change_opm(None)

        if not filepath == '':
            self.textbox_pair_short_info.configure(state="normal")  # configure textbox to be modifiable
            self.textbox_pair_short_info.delete("0.0", "end")
            self.textbox_pair_short_info.insert("0.0", txt)  # add text
            self.textbox_pair_short_info.configure(state="disabled")  # configure textbox to be read-only


class OPMDetail(Frame):
    # frame with a textbox which show some details of the optical model, and allow to modify it
    def __init__(self, master, opm, new_frame=False, help_window=None, **kwargs):
        # initialize the object
        super().__init__(master, new_frame, help_window, **kwargs)

        self.label_details_text = ctk.CTkLabel(self.frame, font=self.font, text="Optical model details :")
        self.label_details_text.grid(row=0, column=0, padx=5, pady=1, columnspan=2, sticky="w")

        self.textbox_details = ctk.CTkTextbox(self.frame, wrap="word", width=700, height=350,
                                              font=ctk.CTkFont(family="Lucida Console", size=14))  # font with same space for all characters
        self.textbox_details.grid(row=0, column=0, padx=5, pady=(0,10), columnspan=5, sticky="w")
        self.textbox_details.configure(state="disabled")  # configure textbox to be read-only

        self.opm = None
        self.sm = self.osp = self.pm = self.em = self.pt = self.ar = None

        if opm is not None:
            self.change_opm(opm)
        else:
            self.update_textbox()

        self.button_ray = ctk.CTkButton(self.frame, text="Ray diagram", command=self.raydiagram, font=self.font)
        self.button_ray.grid(row=1, column=0, padx=10, pady=(5,10), sticky='n')

        self.button_wvf = ctk.CTkButton(self.frame, text="Wavefront", command=self.wavefront, font=self.font)
        self.button_wvf.grid(row=1, column=1, padx=10, pady=(5,10), sticky='n')

        self.button_wvf = ctk.CTkButton(self.frame, text="Save model .roa", command=self.save_roa, font=self.font)
        self.button_wvf.grid(row=1, column=2, padx=10, pady=(5,10), sticky='n')

        self.modify_label = ctk.CTkLabel(self.frame, text='Modify model :', font=self.font)
        self.modify_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=10, pady=5)

        self.button_wvf = ctk.CTkButton(self.frame, text="Interfaces", command=self.save_roa, font=self.font)
        self.button_wvf.grid(row=3, column=0, padx=10, pady=(0,30), sticky='n')

        self.button_wvf = ctk.CTkButton(self.frame, text="Gaps", command=self.save_roa, font=self.font)
        self.button_wvf.grid(row=3, column=1, padx=10, pady=(0,30), sticky='n')

        self.button_wvf = ctk.CTkButton(self.frame, text="Specs", command=self.save_roa, font=self.font)
        self.button_wvf.grid(row=3, column=2, padx=10, pady=(0,30), sticky='n')

        # initialize glass catalogs
        # if not, medium instances of glass type will have None as catalog attribute
        SchottGlass.initialize_catalog(None)
        SumitaGlass.initialize_catalog(None)
        OharaGlass.initialize_catalog(None)
        HikariGlass.initialize_catalog(None)
        HoyaGlass.initialize_catalog(None)
        CDGMGlass.initialize_catalog(None)


    def update_textbox(self):
        if self.opm is None :
            detail_txt = ('No optical model has been selected, nothing to display !\n'
                          'Please use the "Open roa file" button to select a model.')
        else:
            detail_txt = detail_opm_seq_model_str(self.opm)

        self.textbox_details.configure(state="normal")  # configure textbox to be modifiable
        self.textbox_details.delete("0.0", "end")  # delete all text
        self.textbox_details.insert("0.0", detail_txt)  # add text
        self.textbox_details.configure(state="disabled")  # configure textbox to be read-only

    def change_opm(self, new_opm):
        try:
            if new_opm is not None:
                self.sm = new_opm['seq_model']
                self.osp = new_opm['optical_spec']
                self.pm = new_opm['parax_model']
                self.em = new_opm['ele_model']
                self.pt = new_opm['part_tree']
                self.ar = new_opm['analysis_results']
        except Exception as exception:
            new_opm = None

        if new_opm is None:
            self.sm = self.osp = self.pm = self.em = self.pt = self.ar = None

        self.opm = new_opm

        self.update_textbox()

    def raydiagram(self):
        # display the pair ray tracing diagram
        if self.opm is not None:
            try :
                fig_raydiagram = plt.figure(FigureClass=InteractiveLayout, opt_model=self.opm,
                                            do_draw_rays=True, do_paraxial_layout=True).plot()
                title = 'YZ diagram'
                fig_raydiagram.suptitle(title)
                window_name = 'YZ diagram'
                fig_raydiagram.canvas.manager.set_window_title(window_name)
            except :
                pass

    def wavefront(self):
        plt.figure()


        if self.opm is not None:
            try :
                plt.plot([i for i in range(5)], [i for i in range(5)])
            except:
                pass

    def save_roa(self):
        try:
            filepath = tkinter.filedialog.asksaveasfilename(defaultextension='.roa')
            self.opm.save_model(filepath)
        except:
            pass


def detail_opm_seq_model_str(opm):
    more_info = ''
    more_info = more_info +"List sequential model :\n"

    sm = opm['seq_model']
    osp = opm['optical_spec']
    pm = opm['parax_model']

    # capture the output of listing sequential model (which is output with print, not in str)
    # https://stackoverflow.com/questions/22822267/how-to-capture-print-output-of-another-module
    # https://docs.python.org/3/library/contextlib.html
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        sm.list_model()
    list_model_str = f.getvalue()
    more_info = more_info + list_model_str + "\n\n"

    # pupil and wavelength etc
    more_info = more_info + 'system unit : ' + opm.system_spec.dimensions + '\n\n'
    more_info = more_info + 'wavelengths (nm) : ' + str(osp.spectral_region.wavelengths) + '\n\n'
    more_info = more_info + 'pupil diameter : ' + osp['pupil'].listobj_str() + '\n\n'
    more_info = more_info + 'fields angles : ' + osp['fov'].listobj_str() + '\n\n'

    # first order data of the model => capture string output
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        pm.first_order_data()
    first_order_data_str = f.getvalue()
    more_info = more_info + 'first order data :\n' + first_order_data_str + "\n\n"

    # detailed information about surfaces and gap
    more_info = more_info + ("More information about surfaces and gaps (coefficients if some surfaces are asphere, "
                             "refractive index used, and more) :\n\n")

    for i in range(len(sm.ifcs)):
        more_info = (more_info + "INTERFACE " + str(i) + " :\n" +
                     sm.ifcs[i].listobj_str() + "\n")

        if i < len(sm.ifcs) - 1:
            more_info = (more_info + "GAP " + str(i) + " :\n" +
                         sm.gaps[i].listobj_str())

            for wvl in opm['optical_spec'].spectral_region.wavelengths:
                more_info = (more_info + "RI of medium for wvl " + str(wvl) + " nm is : " +
                             str(sm.gaps[i].medium.calc_rindex(wvl)) + "\n")
            more_info = more_info + "\n"
    return more_info

