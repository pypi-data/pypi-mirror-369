import logging
import sys  # system, to set logging to file and stdout
import os.path

# import from PyRFTL
logger = logging.getLogger('PyRFTL')



#### LOG ####
def set_log(folder_name=None,log_stdout=True) :
    # if folder_name exist, a log file would be put in the folder
    # if log_stdout is True, log would also be output to stdout
    # it should not be folder_name=None and log_stdout=True at the same time. (if it is, standard basic config would be used)

    handlers = []
    if folder_name is not None :
        handlers.append(logging.FileHandler(os.path.join(folder_name, "log.txt")))
    if log_stdout :
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(handlers=handlers, encoding='utf-8', level=logging.INFO)


#### DISTANCES ####
def lens_distance_to_efl(distance, opm, gap_index):
    # change the distance between the two lenses and return the new effective focal length
    opm['seq_model'].gaps[gap_index].thi = distance
    opm.update_model()
    efl = opm['parax_model'].opt_model['analysis_results']['parax_data'].fod.efl
    return efl


def safe_lens_distance_to_efl(distance, opm, gap_index):
    try:
        efl = lens_distance_to_efl(distance, opm, gap_index)
    except:
        efl = None
    return efl


def lens_distance_to_efl_zero(distance, opm, gap_index, expected_focal_length):
    # to be used by obtainDistanceToCrossAZero for optimization
    return lens_distance_to_efl(distance, opm, gap_index) - expected_focal_length


def obtain_distance_to_cross_a_zero(opm, gap_index, expected_fl, actual_dist):
    # search for an interval [a,b] of distances between the two lenses, for which the expected efl for the pair is between the pair efl when distance between lenses is a and when distance is b
    # actual_dist is the initialize distance, which is expected to be the optimal distance. It should be >= 0 (physically impossible if <0)
    if actual_dist < 0:
        raise ValueError("initialize distance of obtainDistanceToCrossAZero cannot be < 0")

    epsilon = 0.5
    a = actual_dist - epsilon
    b = actual_dist

    if a < 0:
        a = 0

    nbboucle = 0
    efl_zero_for_separation_a = lens_distance_to_efl_zero(a, opm, gap_index, expected_fl)
    efl_zero_for_separation_b = lens_distance_to_efl_zero(b, opm, gap_index, expected_fl)

    should_continue = efl_zero_for_separation_a * efl_zero_for_separation_b > 0

    while should_continue:
        # change distance b
        b = actual_dist + epsilon
        efl_zero_for_separation_b = lens_distance_to_efl_zero(b, opm, gap_index,
                                                              expected_fl)  # determine the efl (rather efl - expected_efl) of the pair when both lenses are separated of distance a
        should_continue = efl_zero_for_separation_a * efl_zero_for_separation_b > 0  # check if expected_efl is between efl_with_distance_a and efl_with_distance_b

        epsilon = epsilon * 2  # have already changed a, so epsilon change between change of a and b

        # check the loop number, and increase it
        if nbboucle > 8:  # avoid infinity loop. At loop 8, a is initial-128 and b is initial+128 !
            logger.error(
                'impossible to define an interval of lenses separation distances that permit to find the effective focal length')
            logger.error("a " + str(a) + " " + str(lens_distance_to_efl_zero(a, opm, gap_index, expected_fl)) + "\nb " + str(
                b) + " " + str(lens_distance_to_efl_zero(b, opm, gap_index, expected_fl)))
            should_continue = False
        else:
            nbboucle = nbboucle + 1

        # change distance a
        if a > 0 and should_continue:
            a = actual_dist - epsilon  # change distance a
            if a < 0:
                a = 0  # distance between lenses cannot be < 0
            efl_zero_for_separation_a = lens_distance_to_efl_zero(a, opm, gap_index,
                                                                  expected_fl)  # determine the efl (rather efl - expected_efl) of the pair when both lenses are separated of distance a
            should_continue = efl_zero_for_separation_a * efl_zero_for_separation_b > 0  # check if expected_efl is between efl_with_distance_a and efl_with_distance_b

    return [a, b, nbboucle]


#### FLOAT COMPARISON ####

def is_between(number_to_test, inf=None, sup=None):
    # said if inf <= number_to_test <= sup
    # inf and sup can be None (so no inf and no sup values)
    if (not inf is None) and number_to_test < inf:
        return False

    if (not sup is None) and number_to_test > sup:
        return False

    return True


#### OPTICAL MODEL ####

def opm_dist_idx1_idx2(opm, idx1, idx2):
    # return the distance between idx1 and idx2 in optical model opm
    # gaps of layer idx2 is not get, as it is between idx2 and idx2+1
    dist = 0
    for i in range(idx1, idx2):
        dist = dist + opm['seq_model'].gaps[i].thi
    return dist


#### OTHERS ####

def time_str_hms_from_s(t_total):
    hours = t_total // 3600
    minutes = (t_total - hours * 3600) // 60
    seconds = round(t_total - hours * 3600 - minutes * 60)
    return str(hours) + "h " + str(minutes) + "min " + str(seconds) + 's'


def check_param(param):
    if param['thin_lens_first_analysis'] and (not is_between(param['tolerance_prcent'], 0, 100)):
        raise ValueError('tolerance_prcent should be between 0 and 100 (or None)')

    if not isinstance(param['best_focus_fast'], bool):
        raise ValueError('best_focus_fast should be a boolean')

    if not param['cut_off_angle_min'] < param['cut_off_angle_test_end']:
        raise ValueError('cut_off_angle_min > cut_off_angle_test_end, it should be the opposite')

    if not (param['wavefront_analysis'] == "fast" or param['wavefront_analysis'] == "mean"):
        raise ValueError('wavefront_analysis should be "fast" or "mean"')


def description_pair_list(param, pair={}, columns_names=True, first_rms=None):
    # output some data of the pair in a list
    # header specify if output column names also or only the data
    # put pair = None if wants only the column names

    description = []
    if not isinstance(pair, dict):
        pair = {'pair':pair}

    # create column names
    if columns_names:
        columns_names_list = ['lens1 filename', 'lens2 filename', 'config', 'pair short name',
                              'lens1 id', 'lens2 id', 'lens1 EFL', 'lens2 EFL',
                              'first analysis RMS wavefront error',
                              'second analysis RMS wavefront error', '<lambda/14', 'cut-off angle', 'ffl',
                              'distance between lenses',
                              'bfl', 'optimum bfl for RMS wavefront', 'efl', "distance F to F'",
                              "distance first to last surface of pair lenses",
                              "lens1 total path", "lens2 total path", 'lens1 min diameter', 'lens1 max diameter',
                              'lens2 min diameter', 'lens2 max diameter',
                              'lens1 info', 'lens2 info']

        nb_wvl = len(param['wvl_and_weight'])
        nb_fld = 1
        new_columns = ['fld', 'wvl', 'RMS'] * nb_fld * nb_wvl
        columns_names_list = columns_names_list + new_columns  # concatenate

        description.append(columns_names_list)

    # extract the data
    for pair_key in pair :
        pair_tmp = pair[pair_key]

        # if want anonymity of lenses path or not
        if param['output_csv']['hide_path_in_csv'] :
            tmp_path_lens1 = os.path.relpath(pair_tmp.lens1.filepath, param['lenses_param']['LensesFolderPath'])
            tmp_path_lens2 = os.path.relpath(pair_tmp.lens2.filepath, param['lenses_param']['LensesFolderPath'])
        else:
            tmp_path_lens1 = pair_tmp.lens1.filepath
            tmp_path_lens2 = pair_tmp.lens2.filepath

        tmp_filename_lens1 = os.path.basename(pair_tmp.lens1.filepath)
        tmp_filename_lens2 = os.path.basename(pair_tmp.lens2.filepath)

        if first_rms is None:
            rms1 = pair_tmp.rms_detail[0]['RMS']
            rms2 = None
            lambda14 = rms1 < 1/14
        else:
            rms1 = first_rms
            rms2 = pair_tmp.rms_detail[0]['RMS']
            lambda14 = rms2 < 1 / 14

        if hasattr(pair_tmp, 'foc_opti') and pair_tmp.foc_opti.success:
            bfl_opti = pair_tmp.bfl + pair_tmp.foc_opti.x[0]
        else:
            bfl_opti = None

        dist_first_last_surface_lens = opm_dist_idx1_idx2(pair_tmp.opm, pair_tmp.lens1surf[0], pair_tmp.lens2surf[1])
        dist_FFi = dist_first_last_surface_lens - pair_tmp.ffl + pair_tmp.bfl  # distance from object focal plane to image focal plane
        efl = pair_tmp.pm.opt_model['analysis_results']['parax_data'].fod.efl

        data_list = [tmp_filename_lens1, tmp_filename_lens2,
                     str(pair_tmp.config), pair_tmp.short_name, str(pair_tmp.lens1.id), str(pair_tmp.lens2.id),
                     pair_tmp.lens1.efl, pair_tmp.lens2.efl, rms1,
                     rms2, lambda14, pair_tmp.cutoffangle['value'], pair_tmp.ffl, pair_tmp.lenses_gap,
                     pair_tmp.bfl, bfl_opti, efl, dist_FFi, dist_first_last_surface_lens,
                     tmp_path_lens1, tmp_path_lens2,
                     pair_tmp.lens1.diameter_minmax[0], pair_tmp.lens1.diameter_minmax[1],
                     pair_tmp.lens2.diameter_minmax[0], pair_tmp.lens2.diameter_minmax[1],
                     pair_tmp.lens1.info, pair_tmp.lens2.info]

        try :
            if hasattr(pair_tmp, 'wvf_preprocessed'):
                if pair_tmp.wvf_preprocessed :  # not empty
                    nb_wvl = len(pair_tmp.wvf_preprocessed[0]['wvl_and_data'])

                    for i_fld in range(len(pair_tmp.wvf_preprocessed)):  # fld
                        for i_wvl in range(nb_wvl):  # wvl
                            tmp_fld = pair_tmp.rms_detail[i_fld * nb_wvl + i_wvl + 1]['used_fld']
                            tmp_wvl = pair_tmp.rms_detail[i_fld * nb_wvl + i_wvl + 1]['used_wvl']
                            tmp_rms = pair_tmp.rms_detail[i_fld * nb_wvl + i_wvl + 1]['RMS']
                            data_list = data_list + [tmp_fld, tmp_wvl, tmp_rms]
        except:
            pass

        description.append(data_list)

    return description


def pair_df_2_lens_config(pair_dataframe, linekey, lenses_list):
    # export config and original lenses from a pair
    config = pair_dataframe.at[linekey, 'config']
    if str(config) in ['nan', "None", 'none']:
        config = None

    lens1 = lenses_list[int(pair_dataframe.at[linekey, 'lens1 id'])]

    lens2_id = pair_dataframe.at[linekey, 'lens2 id']
    if str(lens2_id) in ['nan', "None", 'none']:
        lens2 = None
    else:
        lens2 = lenses_list[int(lens2_id)]

    return config, lens1, lens2

