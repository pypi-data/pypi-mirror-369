# import from general libraries
from glob import glob  # to get all files path from a folder path
import os  # to get filename form path
import logging

import numpy as np

from configparser import ConfigParser  # import txt file *.ini to import lens folder metadata

# import from PyRFTL
from pyrftl.func.Lens import Lens
logger = logging.getLogger('PyRFTL')


def open_lenses (lenses_param, recursive=True) :
    # this function return a lenses list from lenses opened in lenses_param['LensesFolderPath']

    list_zmx_files = glob(lenses_param['LensesFolderPath'] + "/**/*.zmx", recursive=recursive)
    list_codev_files = glob(lenses_param['LensesFolderPath'] + "/**/*.seq", recursive=recursive)
    list_ray_optics_files = glob(lenses_param['LensesFolderPath'] + "/**/*.roa", recursive=recursive)

    lenses_filepath_list = [*list_zmx_files, *list_codev_files, *list_ray_optics_files]  # concatenate
    lenses_list = []

    logger.info("Start to import lenses...\n")
    print("Try to open lens 1/" + str(len(lenses_filepath_list)), end='')
    j = 0

    # try to open each lens in the folder, and to get main properties
    for i, lensFilePath in enumerate(lenses_filepath_list):
        print("\rTry to open lens " + str(i + 1) + "/" + str(len(lenses_filepath_list)), end='')
        try:
            try:  # get lens folder metadata
                metadata_path = os.path.join(os.path.dirname(lensFilePath), 'lens_dir_metadata.txt')

                if os.path.exists(metadata_path):
                    # if there is a metadata file in the lens folder, extract its data
                    metadata = ConfigParser()
                    metadata.read(metadata_path)
                    info = metadata._sections.copy()  # extract the dictionary
                else:
                    info = None
            except:
                info = None

            # open lenses
            lens = Lens(lensFilePath, lenses_param['check_air_gap'], lenses_param['delete_air_gap'], None, info)

            # check if lens mets users parameters
            add_lens = True

            # check diameter
            if not lenses_param['lens_diameter_min'] is None:
                if lens.diameter_minmax[0] < lenses_param['lens_diameter_min'] :  # min diameter too small
                    add_lens = False
                    why_not_add_lens = ('This lens is rejected because its diameter is too small, change lens_diameter_min'
                                        + ' if you want to keep it \nThis lens has a min diameter of :  ' +
                                        str(lens.diameter_minmax[0]) + ' mm')

            if (not lenses_param['lens_diameter_max'] is None) and add_lens:
                if lens.diameter_minmax[1] > lenses_param['lens_diameter_max']:  # max diameter too huge
                    add_lens = False
                    why_not_add_lens = ('This lens is rejected because its diameter is too large, change lens_diameter_max'
                                        + ' if you want to keep it \nThis lens has a max diameter of :  '
                                        + str(lens.diameter_minmax[1]) + ' mm')

            # check effective focal length
            if (not lenses_param['lens_efl_min'] is None) and add_lens:
                if lens.efl < lenses_param['lens_efl_min']:  # too small efl
                    add_lens = False
                    why_not_add_lens = ('This lens is rejected because its effective focal length is too short, change'
                                        + ' lens_efl_min if you want to keep it \nThis lens efl is :  '
                                        + str(lens.efl) + ' mm')

            if (not lenses_param['lens_efl_max'] is None) and add_lens:
                if lens.efl > lenses_param['lens_efl_max']:  # too huge efl
                    add_lens = False
                    why_not_add_lens = ('This lens is rejected because its effective focal length is too long, change '
                                        + 'lens_efl_max if you want to keep it \nThis lens efl is :  '
                                        + str(lens.efl) + ' mm')

            # keep the lens if it is ok
            if add_lens:
                lens.id = j
                j = j + 1
                lenses_list.append(lens)
                logger.info("Lens selected for generation of pairs : " + os.path.basename(lens.filepath) + "\n")
            else:
                logger.info("Lens is rejected :\n" + lensFilePath + "\n" + why_not_add_lens + "\n")

        except Exception as exception:
            logger.error("Error while trying to open file : " + lensFilePath + "\n" +
                         "Error is : " + str(exception))
            logger.info("Software is still running, opening next lens\n")
            raise

    print()
    return lenses_list


def max_fld_angle(fn_O2, M_O2, ftl_O2m, Mtot=None, fn_O1=None, M_O1=None):
    # return the maximum field angle (in degree) after infinity corrected objective.
    # can work with only one objective (Mtot=None, fn_O1=None, M_O1=None) or with a remote refocusing system
    # (see Botcherby et al. paper doi:10.1364/OL.32.002007)
    # (see also Hong et al. https://doi.org/10.1364/OE.450320)
    # In the second case, we give the maximum field angle after O2, with TL2 is the tube lens we want to design
    #
    # fn_O2 field number of O2
    # M_O2 initial magnification of O2
    # ftl_O2m tube lens focal length for which O2 is designed
    #
    # in case of optical remote focusing
    # Mtot is the magnification from the sample (before O1) to the remote sample (after O2), usually n1/n2
    # fn_O1 field number of objective O1
    # M_O1 initial magnification of O1
    # to get max field angle for only one objective, and not in remote refocusing configuration, put
    # Mtot=None, fn_O1=None, M_O1=None

    sample_diam_2 = fn_O2/M_O2

    if not (Mtot is None or fn_O1 is None or M_O1 is None) :
        sample_diam_1 = Mtot * fn_O1/M_O1
        sample_diam = min(sample_diam_1, sample_diam_2)
    else:
        sample_diam = sample_diam_2

    fld_angle_max = np.arctan(sample_diam * M_O2 / (2 * ftl_O2m))
    return fld_angle_max * 180/np.pi  # degree


def pupil_diameter (NA_O2, M_O2, ftl_O2m, Mtot=None, NA_O1=None):
    # return the pupil diameter of the objective infinity corrected objective O2
    # can work with only one objective (Mtot=None, NA_O1=None, M_O1=None) or with a remote refocusing system
    # (see Botcherby et al. paper doi:10.1364/OL.32.002007)
    # (see also Hong et al. https://doi.org/10.1364/OE.450320)
    # In the second case, we give the pupil diameter of O2, with TL2 is the tube lens we want to design
    #
    # NA_O2 numerical aperture of O2
    # M_O2 initial magnification of O2
    # ftl_O2m tube lens focal length for which O2 is designed
    #
    # in case of optical remote focusing
    # Mtot is the magnification from the sample (before O1) to the remote sample (after O2), usually n1/n2
    # NA_O1 numerical aperture of objective O1
    # M_O1 initial magnification of O1
    # to get max field angle for only one objective, and not in remote refocusing configuration, put
    # Mtot=None, NA_O1=None, M_O1=None

    p2 = 2 * NA_O2 * ftl_O2m/M_O2

    if not (Mtot is None or NA_O1 is None):
        p1_M = 2 * NA_O1 * ftl_O2m/(Mtot * M_O2)
        p = min(p2, p1_M)
    else:
        p = p2

    return p


def f_tl2_from_f_tl1 (MO1_m, ftl1_m, ftl1_u, MO2_m, ftl2_m, n1, n2):
    # in case of optical remote focusing system as described in Botcherby paper doi:10.1364/OL.32.002007,
    # in the case TL1 is fixed, and we are looking for the required focal length for TL2
    # this function return the required focal length for TL2
    #
    # MO1_m, MO2_m manufacturer magnification of objectives O1 and O2
    # ftl1_m, ftl2_m manufacturer focal length of tubes lengths required for O1 and O2
    # ftl1_u used focal length for TL1
    # n1, n2 refractive index before O1, after O2 (required magnification for the system will be Mtot = n1/n2)

    ftl2_u = ftl1_u * ftl2_m * MO1_m * n2 / (n1 * MO2_m * ftl1_m)
    return ftl2_u


