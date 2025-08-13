# import from general libraries
from rayoptics.environment import *  # to import RayOptics. Import also matplotlib.pyplot as plt

from scipy import optimize  # optimization functions
import numpy as np

import os  # to get filename form path

from copy import deepcopy  # to copy an object
import gc  # to free memory

import logging

import contextlib, io  # to be able to capture stdout entry, so what is print(...) by a module

from decimal import Decimal, ROUND_DOWN  # to round down cut-off angle to desire precision, avoid 30 nonsense digits...

# import matplotlib.pyplot as plt

# import from PyRFTL
from pyrftl.rayopt.copy_opm import copy_opm_internal, set_clear_apertures
from pyrftl.func.various_stuff import obtain_distance_to_cross_a_zero, lens_distance_to_efl_zero, safe_lens_distance_to_efl
from pyrftl.func.Lens import Lens
from pyrftl.rayopt import analyses_test as ta

logger = logging.getLogger('PyRFTL')


class ThinlensPairAnalysis:
    # this class is intended to give the distance between the two lenses of the pair in the case these lenses are thin lens

    def __init__(self, lens1_fl, lens2_fl, expected_fl):
        # lens1_fl and lens2_fl are respectively the focal length of lens 1 and 2
        # expected_fl is the combine focal length of both lenses
        self.lens1_fl = lens1_fl
        self.lens2_fl = lens2_fl
        self.expectedFL = expected_fl

        if lens2_fl is not None:
            [d, FO1, O2Fi, FFi] = self.thin_lens_pair_dist(lens1_fl, lens2_fl, expected_fl)
        else:
            [d, FO1, O2Fi, FFi] = [lens1_fl, lens1_fl, lens1_fl, 2 * lens1_fl]
        self.O1O2 = d
        self.FO1 = FO1
        self.O2Fi = O2Fi
        self.FFi = FFi

    @staticmethod
    def thin_lens_pair_dist(fi1, fi2, fitot):
        # use two lens L1 and L2 as an equivalent lens Ltot
        # this script return the distance from O1 to Ftot and O2 to F'tot, also distance
        # O1O2 between the two lenses
        #
        # input : focal lens first lens fi1
        # focal lens second lens fi2
        # desired focal lens of combination : fitot
        #
        # output : Separation between lenses O1O2 : d
        # distance focal to first lens FO1
        # distance last lens to focal O2F' (O2Fi)
        # distance between two focal FF'

        d = fi1 + fi2 - fi1 * fi2 / fitot
        O1F = fi1 * ((fi2 - d) / (d - fi1 - fi2))
        O2Fi = fi2 * ((d - fi1) / (d - fi1 - fi2))
        FO1 = -O1F
        FFi = d - O1F + O2Fi

        return [d, FO1, O2Fi, FFi]

    def list_attributes_str(self):
        list_attributes = ("Lens 1 FL = " + str(self.lens1_fl) + " mm\nLens 2 FL = " + str(self.lens2_fl) +
                           " mm\nexpected FL = " + str(self.expectedFL) + " mm\nO1O2 = " + str(self.O1O2) +
                           " mm\nFO1 = " + str(self.FO1) + " mm\nO2Fi = " + str(self.O2Fi) + " mm\nFFi = " + str(
                    self.FFi) + " mm")
        return list_attributes


class Pair:
    def __init__(self, lens1, lens2=None, expected_fl=None, pair_id=None, lens_info=None, copy_lens=True):
        # lens1 & lens2 are of class Lens
        # if lens2 is None and expected_fl is None, it is just one lens system

        if (lens2 is None) ^ (expected_fl is None):  # xor
            try:
                if lens2.filepath is None and type(lens2) is Lens :
                    pass
                else:
                    raise ValueError('lens2 and expected_fl should either both have a value, or both be None.'
                                     'You should not have only one defined as None.')
            except:
                raise ValueError('lens2 and expected_fl should either both have a value, or both be None.'
                                 'You should not have only one defined as None.')

        # lens1 is just a link to lens1 variable. If risk to modify it, it is better to get a copy that will not change,
        # use copy_lens = True for it. This will use more memory.
        if copy_lens:
            self.lens1 = deepcopy(lens1)
            self.lens2 = deepcopy(lens2)
        else:
            self.lens1 = lens1
            self.lens2 = lens2

        if self.lens2 is None:
            self.lens2 = Lens(None)

        self.expected_fl = expected_fl  # expected focal length for the pair

        self.thin_lens_analysis = ThinlensPairAnalysis(self.lens1.efl, self.lens2.efl, expected_fl)

        self.id = pair_id
        self.short_name = str(lens1.id) + '_' + str(self.lens2.id)
        self.lens_info = lens_info

        self.avoid_surface_change_list = []

    ##################################################      OPTICAL MODEL      ##################################################

    def create_optical_model(self, config="None", wvl_and_weight=None, ref_wvl_i=None, pupil=6.86, fld=None,
                             dist_pupil_pair=None):
        # config="None" or None if put lenses without changing their orientation from Lens class
        # config = "A", "B", "C", "D" see https://doi.org/10.1364/OE.450320
        # dist_pupil_pair is the distance between the entrance aperture and the first lens of the pair.
        # if dist_pupil_pair = None, it would be the ffl, else distance in mm
        # ref_wvl_i is the index of the reference wavelength in wvl_and_weight list. Default is 0.

        # wvl_and_weight and fld should be list. if None, default values will be applied
        if wvl_and_weight is None :
            wvl_and_weight = [('F', 1.0), ('d', 1.0), ('C', 1.0)]  # 486.1327 nm, 587.5618 nm, 656.2725 nm
            ref_wvl_i = 1

        if fld is None :
            fld = [0]

        if ref_wvl_i is None:
            ref_wvl_i = 0

        if not isinstance(fld, list):
            fld = [fld]

        self.config = config
        self.short_name = self.short_name + '_' + str(config)

        # create the optical model
        self.opm = OpticalModel()
        self.sm = self.opm['seq_model']
        self.osp = self.opm['optical_spec']
        self.pm = self.opm['parax_model']
        self.em = self.opm['ele_model']
        self.pt = self.opm['part_tree']
        self.ar = self.opm['analysis_results']

        self.opm.radius_mode = True
        self.sm.do_apertures = False
        self.sm.gaps[0].thi = 1e10  # object distance = infinity

        self.osp['wvls'] = WvlSpec(wvl_and_weight, ref_wl=ref_wvl_i)
        self.osp['pupil'] = PupilSpec(self.osp, key=['object', 'epd'], value=pupil)
        self.osp['fov'] = FieldSpec(self.osp, key=['object', 'angle'], flds=fld, is_relative=False)

        self.initial_wvl_and_weight = wvl_and_weight
        self.initial_ref_wvl_index = ref_wvl_i
        self.initial_fld_list = fld

        # add diaphragm pupil
        self.sm.add_surface([0, 0], sd=0.5*pupil)
        self.sm.set_stop()
        self.avoid_surface_change_list = [self.sm.cur_surface]
        self.update_model()

        # add gap before lenses
        self.sm.add_surface([0, 0])
        self.update_model()

        # add lenses
        self.lens1surf = [self.sm.cur_surface + 1]  # ext surface number of lens 1
        self.opm.add_part(copy_opm_internal, self.lens1.opm, t=self.thin_lens_analysis.O1O2)
        self.lens1surf.append(self.sm.cur_surface)

        # avoid to modify the lens 1 when update the optical model.
        self.avoid_surface_change_list = (self.avoid_surface_change_list +
                                          [i for i in range(self.lens1surf[0], self.lens1surf[1]+1)])  # concatenate

        if self.lens2.efl is not None :
            self.lens2surf = [self.sm.cur_surface + 1]
            self.opm.add_part(copy_opm_internal, self.lens2.opm, t=self.thin_lens_analysis.O2Fi)
            self.lens2surf.append(self.sm.cur_surface)

            # avoid to modify the lens 2 when update the optical model
            self.avoid_surface_change_list = (self.avoid_surface_change_list +
                                              [i for i in range(self.lens2surf[0], self.lens2surf[1] + 1)])
        else:
            self.lens2surf = [self.sm.cur_surface, self.sm.cur_surface]

        self.update_model()

        self.elmn = [node.id for node in self.pt.nodes_with_tag(tag='#element')]

        # change lenses direction to match with the desired configuration
        match config:
            case "A" | "a":
                # put lenses with more curved side in the image side
                # Object (infinite) lens1 |) lens 2 |) image
                if self.lens1.curv_state == "first_curv":
                    self.opm.flip(self.lens1surf[0], self.lens1surf[1])
                if self.lens2.curv_state == "first_curv":
                    self.opm.flip(self.lens2surf[0], self.lens2surf[1])

            case "B" | "b":
                # infinity |) (| image
                if self.lens1.curv_state == "first_curv":
                    self.opm.flip(self.lens1surf[0], self.lens1surf[1])
                if self.lens2.curv_state == "last_curv" or self.lens2.curv_state == "same" :
                    self.opm.flip(self.lens2surf[0], self.lens2surf[1])

            case "C" | "c":
                # infinity (| (| image
                if self.lens1.curv_state == "last_curv" or self.lens1.curv_state == "same" :
                    self.opm.flip(self.lens1surf[0], self.lens1surf[1])
                if self.lens2.curv_state == "last_curv" or self.lens2.curv_state == "same" :
                    self.opm.flip(self.lens2surf[0], self.lens2surf[1])

            case "D" | "d":
                # infinity (| |) image
                if self.lens1.curv_state == "last_curv" or self.lens1.curv_state == "same" :
                    self.opm.flip(self.lens1surf[0], self.lens1surf[1])
                if self.lens2.curv_state == "first_curv":
                    self.opm.flip(self.lens2surf[0], self.lens2surf[1])

            case "None" | None | "none":
                pass
            case _:
                raise AttributeError('unknown configuration')

        self.update_model()

        # put the right distance between lenses and with the image
        if self.lens2.efl is not None:
            try:
                self.set_lens_gap_efl_affine()
            except:
                self.set_lens_gap_efl_interval()

        self.set_img_dist_bfl()
        self.put_pupil_to_dist(dist_pupil_pair)  # create also self.ffl and self.bfl variables
        self.lenses_gap = self.sm.gaps[self.lens1surf[1]].thi

    ##################################################      CHANGE DISTANCES TO EFL FFL BFL      ##################################################

    def set_lens_gap_efl_interval(self):
        # optimize distance between lenses so efl is the expected focal length
        [a, b, nbboucles] = obtain_distance_to_cross_a_zero(self.opm, self.lens1surf[1], self.expected_fl,
                                                            self.thin_lens_analysis.O1O2)
        distance_between_lenses = optimize.brentq(lens_distance_to_efl_zero, a, b,
                                                  args=(self.opm, self.lens1surf[1], self.expected_fl))

        self.sm.gaps[self.lens1surf[1]].thi = distance_between_lenses

        self.opm.update_model()

    def set_lens_gap_efl_affine(self):
        # usually, the relation between lenses_distance and pair_efl is a kind of 1/x function (Gullstrand formula)
        # we have a relation : 1/efl = a * distance + b
        # we will try to use this to find the necessary lenses separation to have the expected efl

        # initialize 2 distances
        d1 = self.thin_lens_analysis.O1O2
        d2 = d1 + 10

        # get the pair efl for the two distances
        efl_list = [safe_lens_distance_to_efl(d, self.opm, self.lens1surf[1]) for d in [d1,d2]]

        # avoid the singularity point of 1/x
        if efl_list[0] is None :
            d1 = d1 + 20
            efl_list[0] = safe_lens_distance_to_efl(d1, self.opm, self.lens1surf[1])
        if efl_list[1] is None :
            d2 = d2 + 20
            efl_list[1] = safe_lens_distance_to_efl(d2, self.opm, self.lens1surf[1])
        if None in efl_list :
            raise Exception('Error while try to find distance between lenses. Impossible to determine efl for '
                            'two distances')

        # determine affine function coefficients (1/(1/x) = x) look for y=ax+b with y = 1/efl and x = distance
        y1 = 1 / efl_list[0]
        y2 = 1 / efl_list[1]
        a = (y2-y1)/(d2-d1)
        b = -a*d1 + y1

        # determine the theoretical distance to have the correct efl
        defl = (1/self.expected_fl - b)/a
        efl = safe_lens_distance_to_efl(defl, self.opm, self.lens1surf[1])

        if efl is None or (efl - self.expected_fl > 1e-6):
            # if there is an error when check for the EFL with the determined distance
            # or if the obtained efl is not the expected efl
            raise Exception('Impossible to find the distance between lenses to have the expected EFL.')

    def put_pupil_to_dist(self, dist_pupil_pair):
        self.ffl = self.opm['parax_model'].opt_model['analysis_results']['parax_data'].fod.ffl
        self.bfl = self.opm['parax_model'].opt_model['analysis_results']['parax_data'].fod.bfl

        if dist_pupil_pair is None :
            dist = - self.ffl  # FFL front focal length is from first surface to front focal plane
        else :
            dist = dist_pupil_pair

        self.sm.gaps[2].thi = dist

        self.opm.update_model()

    def set_img_dist_bfl(self):
        # distance after the last lens is set to back focal length
        self.sm.gaps[self.lens2surf[1]].thi = self.pm.opt_model['analysis_results']['parax_data'].fod.bfl

        self.opm.update_model()

    ##################################################      VARIOUS STUFF      ##################################################

    def update_model(self, **kwargs):
        self.opm.update_model(**kwargs)
        set_clear_apertures(self.sm, self.avoid_surface_change_list)
        self.opm.update_model(**kwargs)

    def change_field_angle(self, angle):
        if isinstance(angle, list):
            fld = angle
        else:
            fld = [angle]

        self.opm['optical_spec']['fov'] = FieldSpec(self.osp, key=['object', 'angle'], flds=fld, is_relative=False)
        self.update_model()

    def name(self):
        # return in the same str the name of the two files uses in the pair, to be used for print for user after

        name = ""

        if id is not None:
            name = name + "id : " + str(self.id)

        name = name + "   " + os.path.basename(self.lens1.filepath)

        if self.lens2.filepath is not None :
            name = name + " -> " + os.path.basename(self.lens2.filepath)

        if hasattr(self, 'config'):
            name = name + "  config : " + str(self.config)

        return name

    def disp_raytracing(self, do_draw_rays=True, do_paraxial_layout=False, title=None, window_name=None):
        # Draw ray trace for the user
        # if matplotlib figure stay blank, try to add to the code file where is used the function :
        #           import matplotlib
        #           matplotlib.use('TkAgg') #(can need to use other thing in the use function depending on your system)

        fig = plt.figure(FigureClass=InteractiveLayout, opt_model=self.opm,
                          do_draw_rays=do_draw_rays, do_paraxial_layout=do_paraxial_layout).plot()
        if title is None:
            title = 'Ray tracing YZ diagram of pair ' + str(self.short_name)
        fig.suptitle(title)

        if window_name is None:
            window_name = 'YZ diagram pair ' + str(self.short_name)
        fig.canvas.manager.set_window_title(window_name)
        plt.show()
        return fig

    def compute_seidel(self):
        self.seidel = compute_third_order(self.opm)
        return self.seidel

    def decenter_lens(self, lens_to_decenter=1, distance=0, angle=0):
        # decenter the lens 1 or 2 (given lens_to_decenter) by a distance and an angle to the optical axis
        # distance in y direction, and euler angle alpha

        if lens_to_decenter == 1 :
            [idx1, idx2] = self.lens1surf
        elif lens_to_decenter == 2 :
            [idx1, idx2] = self.lens2surf
        else :
            raise ValueError('lens_to_decenter should be 1 or 2')

        # give possibility to decenter surfaces from idx1 to idx2
        if idx1 == idx2 :
            # should not happen but we never know
            self.sm.ifcs[idx1].decenter = srf.DecenterData('dec and return')
        else :
            # surfaces after index 1 are decentered
            self.sm.ifcs[idx1].decenter = srf.DecenterData('decenter')
            # surfaces after index 2 are putted again to previous direction
            self.sm.ifcs[idx2].decenter = srf.DecenterData('reverse')

        # decenter by the distance (in the y direction : cf. RayOptics doc)
        self.sm.ifcs[idx1].decenter.dec[1] = distance
        self.sm.ifcs[idx2].decenter.dec[1] = distance

        # change lens angle (alpha euler angle, cf. RayOptics doc)
        self.sm.ifcs[idx1].decenter.euler[0] = angle
        self.sm.ifcs[idx2].decenter.euler[0] = angle

    def image_radius_one_wvl(self, fld, wvl, attribute=True):
        # determine the maximum radius of an image for the field fld and wavelength wvl after the system
        # attribute bool if True create/replace self.img_radius with value for this computation

        # trace two extremum rays of the pupil
        ray_1 = trace_base(self.opm, [0., 1.], fld, wvl)
        ray_2 = trace_base(self.opm, [0., -1.], fld, wvl)

        max_semidiameter = max(abs(ray_1[0][-1][0][1]), abs(ray_2[0][-1][0][1]))
        # ray_1[0][index surface image][XYZ][Y]

        if attribute:
            self.img_radius = {'radius': max_semidiameter, 'fld': fld, 'wvl': wvl}

        return max_semidiameter

    def compute_image_radius(self, fld=None):
        # determine the maximum radius of an image for the field fld and all wavelengths
        # in case fld=None, the field use of the optical model is the one with the higher y (in absolute value)

        if fld is None:
            fld_list = self.osp.field_of_view.fields  # get fields in the optical model
            if fld_list :  # not empty
                fld = fld_list[0]
                for i in range (1, len(fld_list)):
                    if abs(fld_list[i].y) > abs(fld.y):  # determine the field with the maximum y
                        fld = fld_list[i]
            else:
                return

        wvl_list = self.osp.spectral_region.wavelengths

        if not wvl_list: # empty
            return
        else:
            img_sd = 0
            for wvl in wvl_list :
                img_sd_tmp = self.image_radius_one_wvl(fld, wvl, attribute=False)
                if img_sd_tmp > img_sd :
                    img_sd = img_sd_tmp

        self.img_radius = {'radius': img_sd, 'fld': fld, 'wvl': wvl_list}

        return img_sd


    ##################################################      CUT-OFF ANGLE      ##################################################

    def fld_passing_system(self, fld, wvls=None):
        # check if all rays pass the system
        # take extreme rays and check if they haven't Y out of semidiameter for all interfaces

        if wvls is None :
            wvls = self.osp.spectral_region.wavelengths
        elif type(wvls) is not list:
            wvls = [wvls]

        for wvl in wvls:
            # trace two extremum rays of the pupil
            try:
                f = io.StringIO()
                with contextlib.redirect_stderr(f):
                    # avoid print error
                    ray_1 = trace_base(self.opm, [0., 1.], fld, wvl)
                    ray_2 = trace_base(self.opm, [0., -1.], fld, wvl)
            except Exception as exception:
                # one of rays can't be trace, in general it is too widely out of the system
                return False

            # check for each interface if rays are inside lenses
            for id_surface in range(self.lens1surf[0], self.lens2surf[1]):  # first to last interface of the system
                semidiameter = self.sm.ifcs[id_surface].surface_od()
                max_yray = max(abs(ray_1[0][id_surface][0][1]), abs(ray_2[0][id_surface][0][1]))
                # ray_1[0][id_surface][XYZ][Y]

                if semidiameter < max_yray or np.isnan(max_yray) :
                    return False
        return True

    def determine_cutoffangle_dichotomy(self, angle_start=0, angle_end=45, angle_precision=0.01):
        # only for centered system

        ######  initialize angles
        a1 = angle_start
        a2 = angle_end

        if not 0 <= a1 <= a2 :
            raise ValueError('It is needed that 0 <= angle_start <= angle_end. Please note that '
                             'determine_cutoffangle_dichotomy is designed for centered systems only.')

        def update_error():
            # check if error with the pair optical model
            f = io.StringIO()
            with contextlib.redirect_stderr(f):
                # avoid print error and capture it
                self.update_model()
            return f.getvalue()

        tmp_err = update_error()

        ###### test max and min angles
        # get fields
        # add the field we want to use
        self.osp.field_of_view.fields.append(FieldSpec(self.osp, key=['object', 'angle'], flds=[a1],
                                                       is_relative=False).fields[0])
        # get its index
        i_fld = len(self.osp.field_of_view.fields) - 1

        # update the optical model to adapt the field to the model
        tmp_err = update_error()
        # get the field
        fld = self.osp.field_of_view.fields[i_fld]

        if not self.fld_passing_system(fld):
            # min angle doesn't pass
            self.cutoffangle = {'value' : None, 'angle_start' : angle_start,
                                'angle_end' : angle_end, 'angle_precision' : angle_precision}
            # remove the field used for determining the cut-off angle
            self.osp.field_of_view.fields.pop(i_fld)
            self.update_model()
            return

        elif a1 == a2:
            self.cutoffangle = {'value': angle_start, 'angle_start': angle_start,
                                'angle_end': angle_end, 'angle_precision': angle_precision}
            # remove the field used for determining the cut-off angle
            self.osp.field_of_view.fields.pop(i_fld)
            self.update_model()
            return

        # modify the field with angle a2
        self.osp.field_of_view.fields[i_fld] = FieldSpec(self.osp, key=['object', 'angle'], flds=[a2],
                                                         is_relative=False).fields[0]

        tmp_err = update_error()
        # get the field
        fld = self.osp.field_of_view.fields[i_fld]

        if self.fld_passing_system(fld):
            # the maximal angle to test pass
            self.cutoffangle = {'value' : angle_end, 'angle_start' : angle_start,
                                'angle_end' : angle_end, 'angle_precision' : angle_precision}
            # remove the field used for determining the cut-off angle
            self.osp.field_of_view.fields.pop(i_fld)
            self.update_model()
            return


        ###### dichotomy
        while abs(a2-a1) > angle_precision*0.01:
            # angle to determine
            c = 0.5*(a1+a2)

            # get the field of angle c
            self.osp.field_of_view.fields[i_fld] = FieldSpec(self.osp, key=['object', 'angle'], flds=[c],
                                                             is_relative=False).fields[0]

            tmp_err = update_error()
            fld = self.osp.field_of_view.fields[i_fld]

            # check if fld c is in or out of the system
            if self.fld_passing_system(fld):
                # cut off between c and a2
                a1 = c
            else:
                # cut off between a1 and c
                a2 = c


        ###### end the function and output results
        # remove the field used for determining the cut-off angle
        self.osp.field_of_view.fields.pop(i_fld)
        self.update_model()

        # output the last angle known to succeed passing the system
        # round down depending on precision, to avoid 30 nonsense digits
        # round down to be sure the given output angle pass the system
        value = Decimal(str(a1)).quantize(Decimal(str(angle_precision)), rounding=ROUND_DOWN)

        self.cutoffangle = {'value': value, 'angle_start': angle_start,
                            'angle_end': angle_end, 'angle_precision': angle_precision}

        return

    ##################################################      WAVEFRONT      ##################################################

    def preprocess_wvf(self, fld_list=None, wvl_list=None, foc=0, NbRays=16):
        # this function trace the rays for the described field and wavelength, at given focus
        # fld_list and wvl_list are of type list, foc is float or int, NbRays is int

        if fld_list is None:
            fld_list = self.osp.field_of_view.fields
        if wvl_list is None:
            wvl_list = self.osp.spectral_region.wavelengths

        nb_fld = len(fld_list)
        nb_wvl = len(wvl_list)

        wvf_preprocessed = []
        wvf_processed = []

        for i, fld in enumerate(fld_list):
            wvl_wvf = []
            wvl_wvf_processed = []

            ref_fld = fld
            ref_wvl = wvl_list[0]

            for j, wvl in enumerate(wvl_list):
                # preprocess the wavefront at field fld, wavelength wvl and focus foc, with NbRays rays
                grid, upd_grid, ray00_pkg, pre_piston = ta.trace_wavefront(self.opm, fld, wvl, foc, ref_fld, ref_wvl,
                                                                           num_rays=NbRays, return_piston=True)

                wvl_wvf.append({'wvl': wvl, 'wvl_number': j, 'foc': foc, 'grid': grid, 'upd_grid': upd_grid,
                                'ray00_pkg': ray00_pkg, 'pre_piston': pre_piston})
                wvl_wvf_processed.append({'wvl': wvl, 'wvl_number': j, 'foc': foc, 'wvf_grid': None})

            wvf_preprocessed.append({'fld': fld, 'fld_number': i, 'wvl_and_data': wvl_wvf})
            wvf_processed.append({'fld': fld, 'fld_number': i, 'wvl_and_data': wvl_wvf_processed})

        self.wvf_preprocessed = wvf_preprocessed
        self.wvf_processed = wvf_processed

    def get_number_list_from_fld_wvl(self, fld_list=None, wvl_list=None):
        if fld_list is None:
            fld_number_list = [i for i in range(len(self.wvf_preprocessed))]
        else:
            fld_number_list = []
            nb_fld_preprocessed = len(self.wvf_preprocessed)

            for fld in fld_list:
                for i in range(nb_fld_preprocessed):
                    if self.wvf_preprocessed[i]['fld'] == fld:
                        fld_number_list.append(i)

        # get the index of every wvl in self.wvf_preprocessed
        if wvl_list is None:
            wvl_number_list = [i for i in range(len(self.wvf_preprocessed[0]['wvl_and_data']))]
        else:
            wvl_number_list = []

            if len(self.wvf_preprocessed) != 0:
                nb_wvl_preprocessed = len(self.wvf_preprocessed[0]['wvl_and_data'])
            else:
                nb_wvl_preprocessed = 0

            for wvl in wvl_list:
                for i in range(nb_wvl_preprocessed):
                    if self.wvf_preprocessed[0]['wvl_and_data'][i] == wvl:
                        wvl_number_list.append(i)

        if not (fld_number_list and wvl_number_list) :
            # if fld list empty and wvl list empty
            raise AttributeError('unknown fld and wvl for wavefront refocusing computation')
        elif not fld_number_list :
            # fld_number_list empty
            raise AttributeError('unknown fld for wavefront refocusing computation')
        elif not wvl_number_list :
            # wvl_number_list empty
            raise AttributeError('unknown wvl for wavefront refocusing computation')

        return [fld_number_list, wvl_number_list]

    def refocus_wvf_fld_wvl(self, fld_list=None, wvl_list=None, foc=0):
        # refocus the wavefront at the desired distance
        # input are the field fld instance and wavelength in nm

        # get the index of every fld in self.wvf_preprocessed
        [fld_number_list, wvl_number_list] = self.get_number_list_from_fld_wvl(fld_list, wvl_list)

        self.refocus_wvf_number(fld_number_list, wvl_number_list, foc)

    def refocus_wvf_number(self, fld_number_list=None, wvl_number_list=None, foc=0):
        # refocus the wavefront at the desired distance

        if fld_number_list is None:
            fld_number_list = [i for i in range(len(self.wvf_preprocessed))]
        if wvl_number_list is None:
            wvl_number_list = [i for i in range(len(self.wvf_preprocessed[0]['wvl_and_data']))]

        for i in fld_number_list:

            ref_fld = self.wvf_preprocessed[i]['fld']
            ref_wvl = self.wvf_preprocessed[i]['wvl_and_data'][0]['wvl']

            for j in wvl_number_list:
                grid_pkg = [self.wvf_preprocessed[i]['wvl_and_data'][j]['grid'],
                            self.wvf_preprocessed[i]['wvl_and_data'][j]['upd_grid']]
                piston_pkg = [self.wvf_preprocessed[i]['wvl_and_data'][j]['ray00_pkg'],
                              self.wvf_preprocessed[i]['wvl_and_data'][j]['pre_piston']]
                fld, wvl = self.wvf_preprocessed[i]['fld'], self.wvf_preprocessed[i]['wvl_and_data'][j]['wvl']

                # refocused grid
                self.wvf_processed[i]['wvl_and_data'][j]['wvf_grid'] = ta.focus_wavefront(self.opm, grid_pkg,
                                                                                          fld, wvl, foc,
                                                                                          ref_fld, ref_wvl,
                                                                                          piston_pkg=piston_pkg,
                                                                                          image_pt_2d=None,
                                                                                          image_delta=None,
                                                                                          value_if_none=np.nan)[:,:, 2]


    def compute_rms_wvf_no_weight(self, fld_number_list=None, wvl_number_list=None, add_rms_entry=False,
                                  polychromatic='rmse_rms'):
        # if add_rms_entry is True, add a variable to rms_detail.
        # If False, erase and replace rms_detail with the new results.

        if fld_number_list is None:
            fld_number_list = [i for i in range(len(self.wvf_preprocessed))]
        if wvl_number_list is None:
            wvl_number_list = [i for i in range(len(self.wvf_preprocessed[0]['wvl_and_data']))]

        # for one field, one wavefront, RMS is defined as the standard deviation of the wavefront error map
        #
        # for several field, several wavefront, took the RMS of RMS wavefront error of each fld, wvl
        #
        # fld and wvl weight are ignored and all considered as equal

        nb_fld = np.max(np.shape(fld_number_list))
        nb_wvl = np.max(np.shape(wvl_number_list))
        nb_px_side_wvf = np.max(
            np.shape(self.wvf_processed[fld_number_list[0]]['wvl_and_data'][wvl_number_list[0]]['wvf_grid']))

        if nb_fld > 1 or nb_wvl > 1 :
            p_v = None
            match polychromatic:
                case 'rmse_rms' | 'worst':
                    rms_individual = []
                    for i_fld in fld_number_list :
                        for i_wvl in wvl_number_list :
                            wvf_tmp = self.wvf_processed[fld_number_list[i_fld]]['wvl_and_data'][wvl_number_list[i_wvl]]['wvf_grid']
                            wvf_tmp_mask = np.logical_not(np.isnan(wvf_tmp))
                            rms_individual.append(wvf_tmp[wvf_tmp_mask].std())

                    wvf_concatenate = None

                    if polychromatic == 'rmse_rms':
                        rms = np.sqrt(np.sum(np.square(rms_individual))/len(rms_individual))
                    elif polychromatic == 'worst':
                        rms = np.max(rms_individual)

                    else :
                        raise ValueError("polychromatic should be 'rmse_rms' or 'worst'")

                case _ :
                    raise ValueError("polychromatic should be 'rmse_rms' or 'worst'")

        else:
            # RMS one field one wavelength
            wvf_concatenate = self.wvf_processed[fld_number_list[0]]['wvl_and_data'][wvl_number_list[0]]['wvf_grid']
            rms = wvf_concatenate[np.logical_not(np.isnan(wvf_concatenate))].std()  # RMSE = standard dev
            try :
                p_v = (wvf_concatenate[np.logical_not(np.isnan(wvf_concatenate))].max() -
                       wvf_concatenate[np.logical_not(np.isnan(wvf_concatenate))].min())
            except :
                p_v = None

        fld_list = [self.wvf_preprocessed[j]['fld'] for j in fld_number_list]
        wvl_list = [self.wvf_preprocessed[0]['wvl_and_data'][j]['wvl'] for j in wvl_number_list]

        if len(fld_number_list)>1 or len(wvl_number_list)>1 :
            polychromatic_tmp = polychromatic
        else :
            polychromatic_tmp = 'none'

        if not (hasattr(self, 'rms_detail') and add_rms_entry):
            self.rms_detail = [{'RMS': rms, 'fld_number_list': fld_number_list, 'wvl_number_list': wvl_number_list,
                                'used_fld': fld_list, 'used_wvl': wvl_list, 'polychromatic': polychromatic_tmp,
                                'P-V': p_v,
                                'foc':self.wvf_processed[fld_number_list[0]]['wvl_and_data'][wvl_number_list[0]]['foc'],
                                'grid size': len(self.wvf_processed[0]['wvl_and_data'][0]['wvf_grid'])}]
        else:
            self.rms_detail.append({'RMS': rms, 'fld_number_list': fld_number_list, 'wvl_number_list': wvl_number_list,
                                    'used_fld': fld_list, 'used_wvl': wvl_list, 'polychromatic': polychromatic_tmp,
                                    'P-V': p_v,
                                    'foc':self.wvf_processed[fld_number_list[0]]['wvl_and_data'][wvl_number_list[0]]['foc'],
                                    'grid size': len(self.wvf_processed[0]['wvl_and_data'][0]['wvf_grid'])})

        return rms, fld_number_list, wvl_number_list, wvf_concatenate

    def delete_wvf(self, delete_preprocessed_wavefront=True, delete_processed_wavefront=True):
        # release memory of wavefront calculations, delete just the grids
        if delete_preprocessed_wavefront:
            for fld in self.wvf_preprocessed:
                for wvl in fld['wvl_and_data']:
                    # suppress the variable
                    del wvl['grid']
                    del wvl['upd_grid']

        if delete_processed_wavefront:
            for fld in self.wvf_processed:
                for wvl in fld['wvl_and_data']:
                    # suppress the variable
                    del wvl['wvf_grid']

        # force to free unreferenced memory
        gc.collect()

    def delete_wvf_total(self, delete_preprocessed_wavefront=True, delete_processed_wavefront=True):
        # release memory of wavefront calculations
        if delete_preprocessed_wavefront:
            # suppress the variable
            del self.wvf_preprocessed
        if delete_processed_wavefront:
            del self.wvf_processed

        # force to free unreferenced memory
        gc.collect()

    def refocus_compute_rms_for_optimize(self, foc, fld_number_list=None, wvl_number_list=None,
                                         polychromatic='rmse_rms'):
        self.refocus_wvf_number(fld_number_list, wvl_number_list, foc)
        rms, _, _, _ = self.compute_rms_wvf_no_weight(fld_number_list, wvl_number_list, polychromatic=polychromatic)
        return rms

    def best_rms_focus(self, fld_number_list=None, wvl_number_list=None, start_foc=0, focus_polychromatic='ref_wvl_i'):
        # this function optimize the focus to have the minimum RMS
        # it is better to have preprocessed the wavefront before, with self.wvf_preprocessed() (in order to have the
        # desire precision, fld, etc)
        # focus_polychromatic = 'ref_wvl_i', 'rmse_rms'

        # if a preprocessed wavefront instance doesn't exist yet, determine it
        if not hasattr(self, 'wvf_preprocessed'):
            self.preprocess_wvf()

            # if no specific fld and wvl is chosen, get them all
            # if no specific fld and wvl is chosen, reference fld, wvl is the fld 0 wvl 0
        if fld_number_list is None:
            fld_number_list = [0]
            # fld_number_list = [i for i in range(len(self.wvf_preprocessed))]
        if wvl_number_list is None:
            if focus_polychromatic == 'ref_wvl_i':
                wvl_number_list = [0]
                # self.reference_wvl
            else:
                wvl_number_list = [i for i in range(len(self.wvf_preprocessed[0]['wvl_and_data']))]

        # optimize the focus to have the minimum RMS
        foc_opti = optimize.minimize(self.refocus_compute_rms_for_optimize, start_foc,
                                     args=(fld_number_list, wvl_number_list, focus_polychromatic),
                                     method="BFGS", options={'gtol': 1e-3})
        # foc_opti.success said if successed to find a minimum
        # foc_opti.x = foc to have the minimum

        self.foc_opti = foc_opti

        return foc_opti

    def disp_wavefront(self, fld_number_list=None, wvl_number_list=None, cyclic=True, subplot=True):
        # plot plt schematics of the wavefront
        # cyclic : the wavefront will be displayed between 0 to 1 wave unit
        # subplot : all wavefront in one single figure

        if fld_number_list is None:
            fld_number_list = [i for i in range(len(self.wvf_preprocessed))]
        if wvl_number_list is None:
            wvl_number_list = [i for i in range(len(self.wvf_preprocessed[0]['wvl_and_data']))]

        nb_fld = len(fld_number_list)
        nb_wvl = len(wvl_number_list)

        if nb_wvl<1 or nb_fld<1:
            # no field, no wavelength
            return

        subplot = subplot and (nb_fld + nb_wvl - 1 > 1)

        if cyclic :
            title_global = "Wavefront error map (modulo 1 wave)"
        else:
            title_global = "Wavefront error map, not cyclic"

        if subplot:
            fig, axs = plt.subplots(nb_fld, nb_wvl)
            fig.suptitle(title_global)
            fig.canvas.manager.set_window_title('Wavefront error map pair ' + str(self.short_name))

        for i_subplot, i in enumerate(fld_number_list):
            for j_subplot, j in enumerate(wvl_number_list):
                # get the wavefront for fld[i] and wavelength[j]
                wvf = self.wvf_processed[i]['wvl_and_data'][j]['wvf_grid']

                # avoid NaN values (which aren't part of the wavefront map)
                wvf_mask = np.ma.masked_where(np.logical_not(np.isnan(wvf)), wvf)

                if cyclic:
                    # modulo 1 wave
                    wvf_mask = np.mod(wvf_mask, 1)

                # get fld and wvl for which the wavefront will be displayed
                fld = self.wvf_preprocessed[i]['fld']
                wvl = self.wvf_preprocessed[i]['wvl_and_data'][j]['wvl']

                # create the figure
                if subplot:
                    if nb_fld>1 and nb_wvl>1:
                        ax = axs[i_subplot, j_subplot]
                    elif nb_fld==1:
                        ax = axs[j_subplot]
                    elif nb_wvl==1:
                        ax = axs[i_subplot]
                    else:
                        raise ValueError('there is no field and no wavelength')
                else:
                    fig = plt.figure()
                    ax = plt.gca()
                    fig.canvas.manager.set_window_title('Wavefront error map pair ' + str(self.short_name))

                if cyclic:
                    im = ax.imshow(wvf_mask.data, cmap='hsv', vmin=0, vmax=1)
                else:
                    im = ax.imshow(wvf_mask.data, cmap='jet')

                if subplot :
                    title_start = ''
                else:
                    title_start = title_global + '\n'

                title = (title_start + "Pair : " + str(self.short_name) + "\nwvl : " + str(wvl) + " nm     fld : " +
                         "{:.1f}".format(fld.x) + " x, " + "{:.1f}".format(fld.y) + " y")
                ax.set_title(title, fontsize=10)
                ax.grid(visible=False)

                if subplot:
                    cbar = plt.colorbar(im, ax=ax)
                    cbar.set_label('waves', rotation=270)
                else:
                    cbar = plt.colorbar(im, ax=ax)
                    cbar.set_label('waves', rotation=270, fontsize=12, labelpad=15)
        plt.show()
