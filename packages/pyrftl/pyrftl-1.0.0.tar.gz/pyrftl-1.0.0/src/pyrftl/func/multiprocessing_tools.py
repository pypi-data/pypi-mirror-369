import logging
import time
import psutil
import multiprocess as mp

from pyrftl.func.various_stuff import set_log


def log_process(queue_log, param):
    # process to create logs from the log queue. Process stop when queue_log.get() return None

    logger = logging.getLogger('PyRFTL')

    set_log(param['save_folder_path'], False)

    while True :
        # if there is an element in log queue, create the log, if not wait and check again. When element None is in the
        # queue, that mean the end of logging messages so the process should stop
        if not queue_log.empty() :
            element = queue_log.get()

            if element is None :
                # Stop
                break
            else:
                try :
                    [text, level] = element
                    logger.log(level, text)

                except Exception as exception:
                    logger.error("Error while logging, unable to create the log.\n"
                                 + "Error is :\n"
                                 + str(exception) + "\n")
        else :
            time.sleep(0.05)


def init_global_pair_id (count) :
    global pair_id_
    pair_id_ = count


def create_proc_idx_queue (param) :
    if param['force_affinity_core']:  # if one want to force each subprocess to execute on a separated core
        # create a multiprocessing queue with core index to execute for each process
        q = mp.Queue()
        nb_cores = psutil.cpu_count()
        for i_proc in range(param['nb_subprocesses']):
            i_proc_mod = i_proc % nb_cores  # get the modulo to have always a number between 0 and nb_cores-1
            core_id = psutil.Process().cpu_affinity()[i_proc_mod]
            q.put(core_id)
    else:
        q = None

    return q
