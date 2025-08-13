# select_pair create pair array, then for each pair check distances and determine RMS, in multiprocessing
# some information are keep in a pandas dataframe and which is returned by each core
# best pairs are created again to check their RMS wavefront error with a better precision

# import from general libraries

# optical materials information, to initialize subprocess well
from opticalglass.schott import SchottGlass
from opticalglass.ohara import OharaGlass
from opticalglass.cdgm import CDGMGlass
from opticalglass.hikari import HikariGlass
from opticalglass.hoya import HoyaGlass
from opticalglass.sumita import SumitaGlass

from rayoptics.environment import *  # to import RayOptics
from copy import deepcopy  # to copy an object
import logging
import multiprocess as mp
import os.path  # to get filename form path
import sys
from functools import partial  # create function of one variable from function of several variables
from itertools import chain
import time
from datetime import datetime
import psutil  # force a subprocess to execute on a specific core
from ctypes import c_int  # to be able to create a safe counter for multiprocessing
import numpy as np
import pandas as pd

# import from PyRFTL
from pyrftl.func.various_stuff import is_between, time_str_hms_from_s, set_log, description_pair_list, pair_df_2_lens_config
from pyrftl.func.pairs import Pair
from pyrftl.func.wavefront_pair_analysis import wvf_fast_one_pair
from pyrftl.func.distances_pair_analysis import check_pair_thin_lens, check_pair_ray_tracing
from pyrftl.func.lens_selection import open_lenses
import pyrftl.func.save as save
from pyrftl.func.multiprocessing_tools import create_proc_idx_queue, log_process

logger = logging.getLogger('PyRFTL')
# log level
LOG_DEBUG = 10
LOG_INFO = 20
LOG_WARNING = 30
LOG_ERROR = 40
LOG_CRITICAL = 50


def select_pair(param) :
    # select pairs of lenses which correspond to good distance, and determine their wavefront RMS error
    # first open lenses files, then for each pair of lenses (and configurations, so lenses directions), check for
    # distances and if it is ok, determine the RMS. Save values in a pandas dataframe

    t00 = time.time()

    if hasattr(param, 'start_time'):
        start_date = datetime.fromtimestamp(param['start_time']).strftime("%Y_%m_%d_%Hh%M")
    else:
        start_date = datetime.fromtimestamp(t00).strftime("%Y_%m_%d_%Hh%M")
    print('Start analysis time : ' + start_date)

    # set logger
    set_log(param['save_folder_path'], False)

    logger = logging.getLogger('PyRFTL')  # log

    logger.info('Start analysis : ' + param['analysis_name'])
    logger.info('date and time at log start: ' + start_date)

    logger.info('Parameters for analysis : ' + str(param))

    if param['dist_criteria']['O1O2_min'] is None or param['dist_criteria']['O1O2_min']<0 :
        param['dist_criteria']['O1O2_min'] = 0
        # lenses cannot be nearest than 0 mm, it is physically impossible

    # create a list of lenses to use
    lenses_list = open_lenses(param['lenses_param'])

    # create folders to save seq model and roa
    if param['save_seq_detail'] != 'no':
        dir_path = os.path.join(param['save_folder_path'], 'Pairs_Sequential_Model_detail')
        os.mkdir(dir_path)
    if param['save_roa'] != 'no':
        dir_path = os.path.join(param['save_folder_path'], 'RayOptics models')
        os.mkdir(dir_path)

    # create pairs of lenses and select good ones
    # config should be a list
    if not isinstance(param['config'], list):
        param['config'] = [param['config']]

    # select lenses
    # first selection
    pair_data_list, pair_dict = which_pair_to_add_successive(lenses_list, param)

    # check if at least one pair was selected
    if len(pair_data_list) <= 1 :  # only column label
        logger.info("No pair have been selected !\nYou should add more lenses or change your criteria.")
        print("No pair have been selected !\nYou should add more lenses or change your criteria.")
        tff = time.time()
        logger.info('Total time : ' + time_str_hms_from_s(tff - t00))
        print(time_str_hms_from_s(tff - t00))
        return None, pair_dict, None

    # determine pairs with best rms
    pair_dataframe = pd.DataFrame(pair_data_list[1:], columns=pair_data_list[0])
    pair_dataframe.sort_values(by='first analysis RMS wavefront error', inplace=True)  # sort by RMS
    pair_dataframe.set_index('pair short name', inplace=True)  # use pair short name as row index
    # (pair short name should be unique, it is lens1id_lens2id_config)

    # get RMS better resolution
    if param['nbRays_high_comparison'] > param['nbRays_first_comparison']:

        # get rms for best pairs
        rms_best_pairs(pair_dataframe, pair_dict, param, lenses_list)

        # sort dataframe by rms
        pair_dataframe.sort_values(by=['second analysis RMS wavefront error', 'first analysis RMS wavefront error'],
                                   inplace=True)

    # check if at least one pair as a better rms than diffraction
    if not pair_dataframe.iloc[0].at['<lambda/14'] :
        logger.info('No pair is good enough. All have more wavefront aberrations than the diffraction limit '
                    '(RMS error > lambda/14).\nYou should try to add more lenses.\n')
    else:
        logger.info('best pair is : ' + str(pair_dataframe.index[0]) + '\n')

    # export data
    save.save_results_csv_df(param, pair_dataframe)

    tff = time.time()
    logger.info('Total time : ' + time_str_hms_from_s(tff-t00))
    print(time_str_hms_from_s(tff - t00))

    if param['save_ram'] == 'no':
        # no need to keep lenses if all pairs model are exported and do not need to be recreated from lenses
        lenses_list_export = None
    else:
        lenses_list_export = lenses_list

    return pair_dataframe, pair_dict, lenses_list_export


def init_subprocess (q=None, queue_for_log=None, counter_safe=None, log_mute=True) :
    # initialize subprocess to force to execute it on a specific core. Also initialize other stuff
    # q = multiprocessing queue with core number to use for each subprocess
    # q = None if no need to force subprocess on a specific core

    # mute logging in the subprocess. In the future, should redirect it in queue_log as a handler. For now, just mute
    # others logs than mine
    if log_mute :
        logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)],level=60)

    # force the subprocess to execute on a specific core. The core number is taken from queue q
    if q is not None :
        i_proc = q.get()
        psutil.Process().cpu_affinity([i_proc])

    # initiate the queue in which logs will be sent
    global queue_log
    queue_log = queue_for_log

    # initiate the shared variable (between subprocesses) to observe/count how many pairs have been processed
    global counter
    counter = counter_safe

    # initialize glass catalogs
    # if not, medium instances of glass type will have None as catalog attribute in subprocesses
    SchottGlass.initialize_catalog(None)
    SumitaGlass.initialize_catalog(None)
    OharaGlass.initialize_catalog(None)
    HikariGlass.initialize_catalog(None)
    HoyaGlass.initialize_catalog(None)
    CDGMGlass.initialize_catalog(None)


def which_pair_to_add_successive(lenses_list, param):
    # return a dataframe with data of pairs which succeed in distance test.
    # Can return also a list of pair instances (optional)

    nb_lenses = len(lenses_list)

    # initialization of multiprocessing
    # create list of possible lenses combinations to evaluate each one separately via multiprocessing
    lenses_possible_pairs = []
    if ('pair_of_one_lens' in param) and param['pair_of_one_lens']:  # if 'pair_of_one_lens' exist and is True
        lenses_possible_pairs = [(lens, None) for lens in lenses_list]
    else:
        for i in range(nb_lenses):
            for j in range(nb_lenses):
                lenses_possible_pairs.append((lenses_list[i], lenses_list[j]))

    # create queue used to initialize processor cores
    q = create_proc_idx_queue(param)

    queue_log = mp.Queue()  # each element of the queue is an array of two elements : [message, log level]
    counter = mp.Value(c_int)

    # start process to collect logs and write them into a log file
    process_log = mp.Process(target=log_process, args=(queue_log, param))
    process_log.start()

    # start processes to do calculations
    with mp.Pool(param['nb_subprocesses'], initializer=init_subprocess, initargs=(q, queue_log, counter)) as pool:
        t0 = time.time()

        # get list of valid pairs with multiprocessing.
        output = pool.map(partial(which_config_to_add_lens_successive, param=param,
                                  nb_without_config=nb_lenses**2), lenses_possible_pairs)

        print()

        # extract list of data and list of pairs (pair list is empty if in other save ram mode than 'no')
        pair_data_list = description_pair_list(param)  # get columns names
        pair_dict = {}  # keys are pairs short names
        for elt in output:
            pair_data_list = pair_data_list + elt[0]  # concatenate list
            pair_dict = {**pair_dict, **elt[1]}  # concatenate dictionary

    # When multiprocessing workers from pool are finished, put None in log_queue to ask process_log to stop
    queue_log.put(None)
    process_log.join()

    return pair_data_list, pair_dict


def rms_best_pairs(pair_dataframe, pair_dict, param, lenses_list):
    # determine rms wavefront error for best pairs (given first rms determination criteria)
    # pair_dataframe should already be sorted with first row = best pairs

    # get first rows of the dataframe
    pair_dataframe_best = pair_dataframe.head(param['number_best_pair_high_comparison'])

    # remove rows with RMS lower than criteria (with tolerance in %)
    pair_dataframe_best = pair_dataframe_best[pair_dataframe_best['first analysis RMS wavefront error'] <
                                              1 / 14 * (1 + param['tolerance_wavefront_RMS_high_percent'] * 0.01)]

    # create list of lenses pairs to use
    lenses_pairs_best = []
    for linekey in pair_dataframe_best.index:
        # for each line of dataframe, took lens combination of the pair, or the pair
        if param['save_ram'] != 'no':
            config, lens1, lens2 = pair_df_2_lens_config(pair_dataframe_best, linekey, lenses_list)
            lenses_pairs_best.append([config, lens1, lens2])
        else:
            lenses_pairs_best.append(pair_dict[linekey])  # linekey is pair short name

    nb_pairs = len(lenses_pairs_best)

    # create queue used to initialize processor cores
    q = create_proc_idx_queue(param)

    queue_log = mp.Queue()  # each element of the queue is an array of two elements : [message, log level]
    counter = mp.Value(c_int)

    # start process to collect logs and write them into a log file
    process_log = mp.Process(target=log_process, args=(queue_log, param))
    process_log.start()

    # start processes to do calculations
    with mp.Pool(param['nb_subprocesses'], initializer=init_subprocess,
                 initargs=(q, queue_log, counter)) as pool:
        t0 = time.time()

        print("Start computing RMS for best pairs\n"
              "Processed 0/" + str(nb_pairs) + " pairs", end="")

        # get list of valid pairs with multiprocessing. Use not blocking function.
        output = pool.map(partial(wavefront_rms_pair_or_lenses, param=param, nb_pairs=nb_pairs), lenses_pairs_best)

        print()

    # When multiprocessing workers from pool are finished, put None in log_queue to ask process_log to stop
    queue_log.put(None)
    process_log.join()

    # save results
    for i in range(len(output)):
        [short_name, rms, bfl_opti, pair] = output[i]

        if pair is not None :
            pair_dict[short_name] = pair

        try :
            if pair_dataframe.index[i] != short_name:
                # check if we modify the right line
                raise ValueError('Pair has changed its position in the dataframe, pair name : ' + short_name +
                                 ' index at its position : ' + str(pair_dataframe.index[i]))

            pair_dataframe.at[short_name, 'optimum bfl for RMS wavefront'] = bfl_opti
            pair_dataframe.at[short_name, 'second analysis RMS wavefront error'] = rms
            pair_dataframe.at[short_name, '<lambda/14'] = rms < 1/14

        except Exception as exception:
            logger.error(exception)


def wavefront_rms_pair_or_lenses(pair_indications, param, nb_pairs = None):
    # determine RMS with huge grid, to determine it only with interesting pairs
    # can either work with an already existing pair, or (re)create it from few information

    if isinstance(pair_indications, Pair):
        pair = pair_indications
    else:  # (re)create the pair
        config, lens1, lens2 = pair_indications
        pair = Pair(lens1, lens2, param['expected_focal_length'], None,
                    {'lens1 id :', lens1.id, 'lens2 id :', lens2.id})
        pair.create_optical_model(config=config, wvl_and_weight=param['wvl_and_weight'], pupil=param['pupil'], fld=[0],
                                  dist_pupil_pair=param['dist_pupil_pair'])

    # compute RMS wavefront error
    wvf_fast_one_pair(pair, param, param['nbRays_high_comparison'])
    rms = pair.rms_detail[0]['RMS']  # get the rms
    bfl_opti = pair.bfl + pair.foc_opti.x[0]  # get focus distance to have the better RMS

    # save seq model details in txt file
    if param['save_seq_detail'] != 'no':
        dir_path = os.path.join(param['save_folder_path'], 'Pairs_Sequential_Model_detail')
        try:
            filename = param['analysis_name'] + "__" + pair.short_name + "_SeqMod"
            save.export_detail_pair_seqmod_txt(pair, param, dir_path=dir_path, overwrite_file=True, filename=filename)
        except Exception as exception:
            logger.error('unable to export sequential model details of pair ' + pair.name() +
                         '\nerror is : ' + str(exception))

    # save roa model in file
    if param['save_roa'] != 'no':
        dir_path = os.path.join(param['save_folder_path'], 'RayOptics models')
        try:
            filename = param['analysis_name'] + "__" + pair.short_name + "_RayOpticsModel"
            pair.opm.save_model(os.path.join(dir_path, filename))
        except Exception as exception:
            logger.error('unable to save rayoptics model of pair ' + pair.name() +
                         '\nerror is : ' + str(exception))

    # do not output best pairs if want to save the most memory as possible
    if False :
        pair = None

    with counter.get_lock():
        counter.value = counter.value + 1
        print('\rProcessed ' + str(counter.value) + "/" + str(nb_pairs) + " pairs", end="")

    return [pair.short_name, rms, bfl_opti, pair]


def which_config_to_add_lens_successive(lens12_tuple, param, nb_without_config=None):
    # get both lenses
    (lens1, lens2) = lens12_tuple

    # create a pair
    if param['save_ram'] == "max":
        copy_lens = False
    else:
        copy_lens = True
    pair = Pair(lens1, lens2, param['expected_focal_length'], None, {'lens1 id :', lens1.id, 'lens2 id :', lens2.id},
                copy_lens)

    # initialisation
    add_pair = True
    pair_dict_tmp = {}

    ####### THIN LENS ANALYSIS #######
    # check with thin lens analysis if pair met criteria
    if param['thin_lens_first_analysis']:
        if not check_pair_thin_lens(pair, param['dist_criteria']):
            add_pair = False
            why_not_add_pair = ("Pair is rejected by thin lens analysis, it does not meet distances criteria. You can "
                                "change them if needed.")

    ####### GEOMETRICAL RAY TRACING ANALYSIS #######
    # check with geometrical ray tracing if pair met criteria

    if add_pair:
        # we can have as many pairs to test as configs we wanted to check
        for pair_config in param['config']:
            try:
                pair_copy = deepcopy(pair)

                # create optical model
                fld0 = [0]
                pair_copy.create_optical_model(config=pair_config, wvl_and_weight=param['wvl_and_weight'],
                                               pupil=param['pupil'], fld=fld0,
                                               dist_pupil_pair=param['dist_pupil_pair'])

                # check distance criteria
                add_pair_config, why_not_add_pair = check_pair_ray_tracing(pair_copy, param)

                if add_pair_config:
                    if ('image_size' in param) and param['image_size']:
                        try:
                            pair_copy.osp['fov'] = FieldSpec(pair_copy.osp, key=['object', 'angle'],
                                                             flds=[param['cut_off_angle_min']], is_relative=False)
                            pair_copy.opm.update_model()
                            pair_copy.compute_image_radius()
                            pair_copy.osp['fov'] = FieldSpec(pair_copy.osp, key=['object', 'angle'],
                                                             flds=fld0, is_relative=False)
                            pair_copy.opm.update_model()

                        except Exception as exception:
                            pass

                    pair_dict_tmp[pair_copy.short_name]=pair_copy

                    if queue_log is not None:
                        queue_log.put(["Pair selected for RMS Wavefront comparison : " + pair_copy.name() + "\n",
                                       LOG_INFO])

                else:
                    if queue_log is not None:
                        queue_log.put(["Pair has been rejected :" + pair_copy.name() + "\n" + why_not_add_pair + "\n",
                                       LOG_INFO])

            except Exception as exception:
                if queue_log is not None:
                    queue_log.put(["Error in which_pair_to_add_lens\n" +
                                   "Error while working on pair : " + pair.name() + "\n" +
                                   "Error is : " + str(exception),
                                   LOG_ERROR])

    else:  # pair does not pass thin lens distance analysis
        if queue_log is not None:
            queue_log.put(["Pair has been rejected : " + pair.name() + "\n" + why_not_add_pair + "\n",
                           LOG_INFO])

    ####### RMS ANALYSIS #######
    for pair_key in pair_dict_tmp:
        pair = pair_dict_tmp[pair_key]
        wvf_fast_one_pair(pair, param, param['nbRays_first_comparison'], queue_log=queue_log)

    pair_description_list = description_pair_list(param, pair=pair_dict_tmp, columns_names=False)

    if param['save_ram'] != "no":
        pair_dict_output = {}
    else :
        pair_dict_output = pair_dict_tmp

    # save seq model details in txt file
    if param['save_seq_detail'] == 'all':
        dir_path = os.path.join(param['save_folder_path'], 'Pairs_Sequential_Model_detail')
        filename = param['analysis_name'] + "__" + pair.short_name + "_SeqMod"
        for pair_key in pair_dict_tmp:
            pair = pair_dict_tmp[pair_key]
            try:
                save.export_detail_pair_seqmod_txt(pair, param, dir_path=dir_path, filename=filename)
            except Exception as exception:
                logger.error('unable to export sequential model details of pair ' + pair.name() +
                             '\nerror is : ' + str(exception))

    # save roa model in file
    if param['save_roa'] == 'all':
        dir_path = os.path.join(param['save_folder_path'], 'RayOptics models')
        for pair_key in pair_dict_tmp:
            pair = pair_dict_tmp[pair_key]
            try:
                filename = param['analysis_name'] + "__" + pair.short_name + "_RayOpticsModel"
                pair.opm.save_model(os.path.join(dir_path, filename))
            except Exception as exception:
                logger.error('unable to save rayoptics model of pair ' + pair.name() +
                             '\nerror is : ' + str(exception))

    # inform user
    try:
        with counter.get_lock():
            counter.value = counter.value + 1
            if counter.value == 1:
                print('Selection of pairs in process...\n0', end="")
            elif nb_without_config is not None:
                print('\r ' + str(round(counter.value / nb_without_config * 100)) + ' %', end="")
                if nb_without_config == counter.value :
                    print('\nCollecting data from threads, please wait...', end="")
            else:
                print('\r ' + str(counter.value), end="")
    except:
        pass

    # return results
    return pair_description_list, pair_dict_output


