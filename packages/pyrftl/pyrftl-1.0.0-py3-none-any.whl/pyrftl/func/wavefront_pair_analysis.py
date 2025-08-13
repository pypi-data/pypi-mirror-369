# import from general libraries
from rayoptics.environment import *  # to import RayOptics
import numpy as np
import time  # time
import logging
import multiprocess as mp
from functools import partial  # to be able to use multiple arguments function in multiprocess call
import psutil  # force a process to execute on a specific core

# import from PyRFTL
from pyrftl.func.multiprocessing_tools import create_proc_idx_queue, log_process

logger = logging.getLogger('PyRFTL')
# log level
LOG_DEBUG = 10
LOG_INFO = 20
LOG_WARNING = 30
LOG_ERROR = 40
LOG_CRITICAL = 50


def init_subprocess (count=None, q=None, queue_for_log=None) :
    # initialize subprocess :
    #
    # took a global variable and initialize it to the counter
    #
    # initialize subprocess to force it to execute on a specific core
    # q = multiprocessing queue with core number to use for each subprocess
    # q = None if no need to force subprocess on a specific core
    #
    # numpy can sometimes force the process to execute on only one core, in multiprocessing it does that several process
    # want to execute on only the same core. Forcing them to execute on different cores can thus be necessary.

    if count is not None :
        global counter_
        counter_ = count

    if q is not None :
        i_proc = q.get()
        psutil.Process().cpu_affinity([i_proc])

    global queue_log
    queue_log = queue_for_log


def wavefront_analysis_fast(pair_list, param, nb_rays):
    if not pair_list:  # empty
        return []

    # initialise
    pairs_rms = np.ones(len(pair_list))
    pairs_rms[:] = np.nan
    nb_pairs = len(pair_list)

    logger.info('Starting compution of RMS in max field mode for ' + str(nb_pairs) + ' pairs with ' +
                str(nb_rays) + ' rays grid.')
    print('\nStarting compution of RMS in max field mode for ' + str(nb_pairs) + ' pairs with ' +
          str(nb_rays) + ' rays grid.')

    if param['multiprocessing'] :
        counter = mp.Value('i', 0)  # initiate a counter that will be share between processes
        queue_log = mp.Queue()  # each element of the queue is an array of two elements : [message, log level]

        q = create_proc_idx_queue(param)

        # start process to collect logs and send write them into a log file
        process_log = mp.Process(target=log_process, args=(queue_log, param))
        process_log.start()

        # start processes to do calculations
        with mp.Pool(param['nb_subprocesses'], initializer=init_subprocess, initargs=(counter, q, queue_log)) as pool:
            pair_list = pool.map(partial(wvf_fast_one_pair, param=param, nb_rays=nb_rays, nb_pairs=nb_pairs,
                                         pair_index=None), pair_list)
        print()

        # When the multiprocessing workers from pool are finished, put None in log_queue to ask process_log to stop
        queue_log.put(None)
        process_log.join()

    else :
        for i, pair in enumerate(pair_list):
            wvf_fast_one_pair(pair, param, nb_rays, nb_pairs, i)
        print()

    # output multi-wavelength rms
    rms_pairs = np.array([pair.rms_detail[0]['RMS'] for pair in pair_list])
    return pair_list, rms_pairs


def wvf_fast_one_pair(pair, param, nb_rays, best_focus_angle=0, focus_dist=0, queue_log=None) :
    # best_focus_angle : if param['best_focus_fast'] is True, it is the angle at which done the best focus RMS
    # focus_dist : if param['best_focus_fast'] is False, it is the distance to put as focus

    t0 = time.time()

    #### BEST FOCUS ####
    if param['best_focus_fast']:
        # get best focus

        # we want best focus for field 0°
        pair.osp['fov'] = FieldSpec(pair.osp, key=['object', 'angle'], flds=[best_focus_angle], is_relative=False)
        pair.opm.update_model()

        # precalculate the wavefront
        pair.preprocess_wvf(fld_list=None, wvl_list=None, foc=0,
                            NbRays=nb_rays)  # for all fields (only field 0° here, for all wavelengths)
        # best focus
        foc_opti = pair.best_rms_focus(focus_polychromatic=param['focus_polychromatic'])

        if (not foc_opti.success) and (queue_log is not None) :
            # if fail to found the optimal focus
            queue_log.put(['impossible to find the best focus for RMS wavefront measurement for pair : ' +
                          pair.name() + '\nbfl + foc distance to image will be used instead\n',
                          LOG_ERROR])

    #### RMS WAVEFRONT ####
    # we want RMS for field fldAngleMin
    if param['best_focus_fast'] and pair.foc_opti.success:
        foc_tmp = pair.foc_opti.x
    else:
        # if not possible to find best focus (or don't want to use best focus), use focus_dist as focus distance
        # when foc_tmp = 0, we are at bfl if the image is at bfl (normal use case when used with Pair class)
        foc_tmp = focus_dist

    # put field to max angle needed
    pair.osp['fov'] = FieldSpec(pair.osp, key=['object', 'angle'], flds=[param['cut_off_angle_min']],
                                is_relative=False)
    pair.opm.update_model()
    # precalculate the wavefront
    pair.preprocess_wvf(fld_list=None, wvl_list=None, foc=foc_tmp,
                        NbRays=nb_rays)  # for all fields (only field fldAngleMin° here, for all wavelengths)
    # get the wavefront field
    pair.refocus_wvf_number(fld_number_list=None, wvl_number_list=None, foc=foc_tmp)
    # get the RMS
    rms_i, _, _, _ = pair.compute_rms_wvf_no_weight(fld_number_list=None, wvl_number_list=None,
                                                    polychromatic=param['polychromatic'])

    # compute rms for each wvl
    for i_wvl in range(len(pair.wvf_preprocessed[0]['wvl_and_data'])):  # wvl
        pair.compute_rms_wvf_no_weight(fld_number_list=[0], wvl_number_list=[i_wvl], add_rms_entry=True)
        # the wavefront with index i in pair.rms_detail will be :
        # i = i_wvl + 1 (+ 1 because index 0 is multi wavelengths RMS)

    if param['save_ram'] != "no":
        # free memory used to store the wavefront grid
        pair.delete_wvf()

