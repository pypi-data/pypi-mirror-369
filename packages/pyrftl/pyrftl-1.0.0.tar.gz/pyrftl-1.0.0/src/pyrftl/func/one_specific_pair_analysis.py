from pyrftl.func.Lens import Lens
from pyrftl.func.pairs import Pair
from pyrftl.func.wavefront_pair_analysis import wvf_fast_one_pair


def analyse_one_pair (param_one):
    lens1 = Lens(param_one['LensFile1'], check_air_gap=param_one['check_air_gap'], delete_air_gap=param_one['delete_air_gap'])
    lens2 = Lens(param_one['LensFile2'], check_air_gap=param_one['check_air_gap'], delete_air_gap=param_one['delete_air_gap'])
    pair = Pair(lens1, lens2, param_one['expected_focal_length'])
    pair.create_optical_model(config=param_one['config'][0], wvl_and_weight=param_one['wvl_and_weight'],
                              pupil=param_one['pupil'], fld=[0], dist_pupil_pair=param_one['dist_pupil_pair'])
    if param_one['cut_off_angle_test_end'] is None:
        if param_one['cut_off_angle_min'] < 35 :
            param_one['cut_off_angle_test_end'] = 45
        else :
            param_one['cut_off_angle_test_end'] = param_one['cut_off_angle_min'] * 2
    if param_one['cut_off_angle_test_end'] < param_one['cut_off_angle_min'] :
        param_one['cut_off_angle_test_end'] = param_one['cut_off_angle_min'] + 2*param_one['cut_off_angle_precision']

    pair.determine_cutoffangle_dichotomy(angle_end=param_one['cut_off_angle_test_end'],
                                         angle_precision=param_one['cut_off_angle_precision'])
    cut_off = pair.cutoffangle['value']

    wvf_fast_one_pair(pair, param_one, param_one['grid'])
    rms = pair.rms_detail

    return pair, cut_off, rms

