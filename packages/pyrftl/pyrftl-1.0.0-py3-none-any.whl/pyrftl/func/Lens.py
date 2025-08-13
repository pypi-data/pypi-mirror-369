# import from general libraries
from rayoptics.environment import *  # to import RayOptics
import numpy as np


class Lens:
    # This class is intended to be composed of one lens element. Its unit should be in [mm]
    # Typically, it will be used to open file that contain a lens : Zemax .zmx, CodeV .seq or RayOptics .roa
    # zmx, seq and roa can be in mm, cm or inch unit.
    #
    # Some of its attributes could be :
    # the path of the file lens : filepath and its original system units : original_unit
    # Optical model : opm, sm, osp, pm, em, pt, ar
    # idx = [index of the first surface of the lens, index of the last surface of the lens]
    # air_gaps => True/False if some air layers exist before/after the lens in the original file
    #            None if it was not tested
    # delete_air_gap => True/False if it was ask the air gaps to be deleted.
    #               If air_gaps is false, delete_air_gap is nonsense. If delete_air_gap is None, air_gaps was not tested
    # efl = effective focal length of the lens
    # diameter_minmax = [min diameter of the lens, max diameter of the lens] (diameter = 2*semi-diameter)
    # curv = [curvature of the first surface of the lens, curvature of the last surface of the lens]
    # curv_state = "first_curv" "last_curv" "same" => respectively first and last surface of the lens is the more curved
    #              "same" is when curve of both surface is equal

    def __init__(self, filepath, check_air_gap=True, delete_air_gap=False, id_lens=None, info=None):
        # filepath : path of the Lens file
        # check_air_gap : check if there is air gap before or after the lens, and if delete_air_gap : delete them
        self.filepath = filepath
        self.id = id_lens
        self.info = info

        if filepath is not None:
            # open the lens and get its optical model
            self.opm = open_model(filepath, post_process_imports=False)  # function of rayoptics

            # some useful variables
            self.sm = self.opm['seq_model']
            self.osp = self.opm['optical_spec']
            self.pm = self.opm['parax_model']
            self.em = self.opm['ele_model']
            self.pt = self.opm['part_tree']
            self.ar = self.opm['analysis_results']

            # unit of the lens file ([mm], [cm], [inches])
            self.original_unit = self.opm.system_spec.dimensions

            # convert to mm
            if self.original_unit == "inches":
                self.sm.apply_scale_factor(1 / 25.4)
                self.opm.system_spec.dimensions = "mm"
                self.opm.udpate_model()

            elif self.original_unit == "cm":
                self.sm.apply_scale_factor(0.1)
                self.opm.system_spec.dimensions = "mm"
                self.opm.udpate_model()

            elif self.original_unit != "mm":
                raise ValueError('Error : unknown file unit. Possible file units are inches, mm and cm.')

            # lens interface index
            # [first lens interface, last lens interface]
            if self.sm.get_num_surfaces() > 2:
                self.idx = [1, self.sm.get_num_surfaces() - 2]
                # -2 because python index start at 0, not 1, and last surface is the image
            else:
                raise Exception('No lens in file ')

            # check if there is air gap before or after the lens
            if check_air_gap:
                self.air_gaps = self.check_for_air(delete_air_gap, self.idx)
                self.delete_air_gap = delete_air_gap
            else:
                self.air_gaps = None
                self.delete_air_gap = None

            self.opm.update_model()

            # get the effective focal length
            self.efl = self.opm['parax_model'].opt_model['analysis_results']['parax_data'].fod.efl

            # get the lens min and max diameters
            self.diameter_minmax = self.get_diameter()

            # get lens extremities curvatures
            self.opm.radius_mode = False  # go for curvature mode
            self.opm.update_model()
            self.curv = [self.sm.ifcs[self.idx[0]].profile_cv,
                         self.sm.ifcs[self.idx[1]].profile_cv]  # get curvature of first and last lens interfaces

            # check which lens side is the more curved.
            # "first_curv" = first surface is more curved than last one, "last_curv" = last surface more curved
            # "same" = radius of curvature of both extremum sides of the lens are the same
            if np.abs(self.curv[0]) > np.abs(self.curv[1]):
                self.curv_state = "first_curv"
            elif np.abs(self.curv[0]) < np.abs(self.curv[1]):
                self.curv_state = "last_curv"
            else:  # curvature before and after lens are same
                self.curv_state = "same"

        else:  # filepath is None
            self.efl = None
            self.curv_state = None
            self.diameter_minmax = self.curv = [None, None]
            self.opm = None

    def check_for_air(self, suppress_air_gap=False, idx=None):
        # check if there is air gap before or after the lens
        # can suppress air gap if required (but will delete diaphragm if the air gap exist for a good reason)
        # idx => lens interface id [first interface, last interface]
        if idx is None:
            # idx=self.idx
            idx = [1, self.sm.get_num_surfaces() - 2]

        i = idx[0]
        idx_no_air = idx.copy()
        air_gap = False
        layers_to_delete_before = []
        layers_to_delete_after = []

        # look for air part BEFORE the lens
        # so from the first interface after the object, to the last lens interface
        # look all index from first surface to last one until a layer is not air (has not a refractive index of 1
        # (for tested wavelengths : the ones of the system))
        while i < idx[1] and (np.array(self.sm.rndx[i]) == 1.0).all():
            if suppress_air_gap:
                layers_to_delete_before.append(i)
            air_gap = True
            idx_no_air[0] = i
            i = i + 1

        # look for air part AFTER the lens
        # so from the last interface before the image, to the first lens interface
        j = j0 = idx_no_air[1]

        while j > idx_no_air[0] and (np.array(self.sm.rndx[j]) == 1.0).all():
            if suppress_air_gap:
                layers_to_delete_after.append(j)
            if j != j0:
                # if just before image is the only air_gap, it is not considered as an airgap,
                # as it is necessary to have a last lens interface curvature)
                # (but will still remove air distance with image if suppress_air_gap is True)
                air_gap = True
            idx_no_air[1] = j
            j = j - 1

        if suppress_air_gap:
            if len(layers_to_delete_after) > 0:  # if is not empty
                # to not confuse index, start by the last one to the first one
                for i in range(len(layers_to_delete_after) - 1, 0, -1):
                    self.sm.set_cur_surface(layers_to_delete_after[i])
                    self.sm.remove()
                self.sm.gaps[layers_to_delete_after[0]].thi = 0  # distance to the image !

            for i in range(len(layers_to_delete_before) - 1, -1, -1):
                self.sm.set_cur_surface(layers_to_delete_before[i])
                self.sm.remove()

            self.opm.update_model()
            idx_no_air = [1, self.sm.get_num_surfaces() - 2]

        self.idx = idx_no_air
        return air_gap

    def get_diameter(self):
        # this function return the min and max semi-diameters of all surfaces of the lens

        # get an array with all surface semi diamter (except object and image)
        sd_np = np.ones(self.sm.get_num_surfaces())  # preallocating

        for i, ifcs in enumerate(self.sm.ifcs):
            sd = ifcs.surface_od()  # get semi diameter of surface index i
            if sd is not None:
                sd_np[i] = sd
            else:
                sd_np[i] = np.nan

        # get min and max semi diameter of all surfaces of the lens
        sd_min = np.nanmin(sd_np[1:len(sd_np) - 1])
        sd_max = np.nanmax(sd_np[1:len(sd_np) - 1])

        # diameter = 2*semi-diameter
        dia_min = sd_min * 2
        dia_max = sd_max * 2

        return [dia_min, dia_max]

    def flip(self):
        # this function flip the orientation of the lens along the optical axis

        # flip opm model
        self.opm.flip()
        self.opm.update_model()

        # flip orientation dependant parameters
        # surface index of the lens
        idxtps = self.idx.copy()
        self.idx[0] = self.sm.get_num_surfaces() - 1 - idxtps[1]
        self.idx[1] = self.sm.get_num_surfaces() - 1 - idxtps[0]

        # curvature of lens
        self.curv = [self.curv[1], self.curv[0]]

        if self.curv_state == "first_curv":
            self.curv_state = "last_curv"
        elif self.curv_state == "last_curv":
            self.curv_state = "first_curv"

    def schematic_raytracing_plt(self, do_draw_rays=True, do_paraxial_layout=False):
        # Draw ray trace for the user
        layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=self.opm,
                                do_draw_rays=do_draw_rays, do_paraxial_layout=do_paraxial_layout).plot()
        return layout_plt
