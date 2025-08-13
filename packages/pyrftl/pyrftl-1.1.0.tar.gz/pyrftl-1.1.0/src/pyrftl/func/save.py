import contextlib, io  # to be able to capture stdout entry, so what is print(...) by a module
import time
from datetime import datetime  # time
import os  # to get filename from path
import numpy as np  # for matrix math with numpy
import logging
import dill  # to save and load a class object in a binary file

from pyrftl.func.various_stuff import opm_dist_idx1_idx2
logger = logging.getLogger('PyRFTL')


def create_save_folder(save_folder_path, analysis_name=None, t0=None) :
    # if no name for the current analysis, create one
    if analysis_name is None :
        if t0 is None :
            t0 = time.time()
        analysis_name = 'PyRFTL_' + datetime.fromtimestamp(t0).strftime("%Y_%m_%d_%Hh%M")

    # check if the parent save directory exist
    if not os.path.exists(save_folder_path) :
        print('Save folder does not exist')
        raise ValueError ('No folder at path : ' + str(save_folder_path))

    # check if the directory name for the current analysis is free, change the analysis name if not
    i = 0
    analysis_name_tmp = analysis_name
    while os.path.exists(os.path.join(save_folder_path, analysis_name_tmp)) :
        analysis_name_tmp = analysis_name+'_'+str(i)
        i = i+1

    # create the analysis directory
    os.mkdir(os.path.join(save_folder_path, analysis_name_tmp))
    logger.info('create folder : ' + str(os.path.join(save_folder_path, analysis_name_tmp)))

    return os.path.join(save_folder_path, analysis_name_tmp), analysis_name_tmp, t0


def data_list_to_str(list_data, data_separator=';', end_separator='\n', decimal_separator=None):
    # take a list of data in input, and create a str with them :
    # data[0] data_separator data[1] data_separator ... data[-1] end_separator
    output = ''

    for data in list_data:
        try:
            if data is not None:
                str_data = str(data)

                if decimal_separator is not None and decimal_separator != '.' :
                    try :
                        float(data)  # test if we have a decimal number (float, np.float, ...)
                        # if not a decimal, we will have an error so exit the try statement
                        str_data = str_data.replace('.', decimal_separator)
                    except :
                        pass  # do nothing, not a float, no need to change the decimal separator

                output = output + str_data + data_separator
            else:
                output = output + '' + data_separator
        except:
            output = output + '' + data_separator

    output = output + end_separator
    return output


def save_results_csv(param, pair_list, pair_first_rms, pair_second_rms=None, index_min_rms_tolerance=[]):
    logger.info('saving results in csv ...')
    print('saving results in csv ...')

    # create the file
    file_path = os.path.join(param['save_folder_path'], param['analysis_name'])
    try:
        file = open(file_path + ".csv", "x")
    except:  # this should never happen due to precedent code, but if it is, we want to be sure we can create a new file
        i = 0
        while i < 100:
            i = i + 1
            try:
                file = open(file_path + "_" + str(i) + ".csv", "x")
                file_path = file_path + "_" + str(i)
                break
            except:
                pass

    sep_row = param['output_csv']['output_csv_row_separator']
    sep_column = param['output_csv']['output_csv_column_separator']
    sep_dec = param['output_csv']['output_csv_decimal_separator']

    ######## HEADER ########
    # header
    file.write("Analysis of lens pairs for optical remote focusing." + sep_row)
    file.write(sep_row)
    file.write("Analysis name : " + param['analysis_name'] + sep_row)
    file.write("File save time : " + str(datetime.now()) + sep_row)
    file.write("All distances are in mm (except wavelenghts : in nm), angles are in degrees,"
               " RMS wavefront error is in waves" + sep_row)
    file.write(sep_row)
    file.write("parameters :" + sep_row)
    for pa in param:
        if pa == 'save_folder_path' and param['output_csv']['hide_path_in_csv']:
            file.write(str(pa) + sep_column + 'hidden' + sep_row)
        elif pa == 'lenses_param':
            lenses_param_tmp = param[pa].copy()
            lenses_param_tmp['LensesFolderPath'] = 'hidden'
            file.write(str(pa) + sep_column + str(lenses_param_tmp) + sep_row)
        else:
            file.write(str(pa) + sep_column + str(param[pa]) + sep_row)

    file.write(sep_row)
    file.write("WARNING : if your lenses files don't take into account the reduction of lens diameter due to their"
               " mounting, the cut-off angle can be overestimated !" + sep_row)
    file.write("WARNING : Coating is not taken into account, please check if your lenses are designed for the "
               "right wavelengths !" + sep_row)
    file.write(sep_row)

    ######## DATA ########
    # data
    file.write("pairs :" + sep_row)
    file.write(data_list_to_str(['id', 'lens1 filename', 'lens2 filename', 'config', 'pair short name',
                                 'lens1 id', 'lens2 id',
                                 'lens1 EFL', 'lens2 EFL',
                                 'first analysis RMS wavefront error',
                                 'second analysis RMS wavefront error', '<lambda/14', 'cut-off angle', 'ffl',
                                 'distance between lenses',
                                 'bfl', 'optimum bfl for RMS wavefront', 'efl', "distance F to F'",
                                 "distance first to last surface of pair lenses",
                                 "lens1 total path", "lens2 total path", 'lens1 min diameter', 'lens1 max diameter',
                                 'lens2 min diameter', 'lens2 max diameter', 'image radius',
                                 'lens1 info', 'lens2 info', '', '']
                                , sep_column, ""))

    if param['RMS_for_each_fld_wvl']:
        nb_wvl = len(pair_list[0].wvf_preprocessed[0]['wvl_and_data'])
        nb_fld = len(pair_list[0].wvf_preprocessed)
        file.write(data_list_to_str(['fld', 'wvl', 'RMS'] * nb_fld * nb_wvl, sep_column, ""))

    file.write(sep_row)

    pair_second_rms_sorted_index, sorted_rms_index_all = sort_pair_rms(pair_first_rms, pair_second_rms,
                                                                       index_min_rms_tolerance)

    # print pair infos line in the file
    for i_enum, i_pair in enumerate(sorted_rms_index_all):
        i_pair = int(i_pair)
        pair = pair_list[i_pair]

        if i_enum < len(pair_second_rms_sorted_index):  # if there is a second analysis RMS for this pair
            second_rms = pair_second_rms[pair_second_rms_sorted_index[i_enum]]
            # best RMS is the first element of sorted_rms_index_all, and beginning of sorted_rms_index_all
            # is just sorted_RMS_index_best

            if second_rms < 1 / 14:
                lambda14 = True
            else:
                lambda14 = False

        else:
            second_rms = None
            if pair_first_rms[i_pair] < 1 / 14:
                lambda14 = True
            else:
                lambda14 = False

        if hasattr(pair, 'foc_opti') and pair.foc_opti.success:
            bfl_opti = pair.bfl + pair.foc_opti.x[0]
        else:
            bfl_opti = ''  # None

        dist_first_last_surface_lens = opm_dist_idx1_idx2(pair.opm, pair.lens1surf[0], pair.lens2surf[1])
        dist_FFi = dist_first_last_surface_lens - pair.ffl + pair.bfl  # distance from object focal plane to image focal plane

        efl = pair.pm.opt_model['analysis_results']['parax_data'].fod.efl

        # if want anonymity of lenses path or not
        if param['output_csv']['hide_path_in_csv'] :
            tmp_path_lens1 = os.path.relpath(pair.lens1.filepath, param['lenses_param']['LensesFolderPath'])
            tmp_path_lens2 = os.path.relpath(pair.lens2.filepath, param['lenses_param']['LensesFolderPath'])
        else:
            tmp_path_lens1 = pair.lens1.filepath
            tmp_path_lens2 = pair.lens2.filepath

        if pair.lens1.filepath is None:
            tmp_filename_lens1 = None
        else:
            tmp_filename_lens1 = os.path.basename(pair.lens1.filepath)

        if pair.lens2.filepath is None:
            tmp_filename_lens2 = None
        else:
            tmp_filename_lens2 = os.path.basename(pair.lens2.filepath)

        if ('image_size' in param) and param['image_size']:
            img_radius_tmp = pair.img_radius['radius']
        else:
            img_radius_tmp = None

        file.write(
            data_list_to_str([tmp_filename_lens1, tmp_filename_lens2,
                              str(pair.config), pair.short_name, str(pair.lens1.id), str(pair.lens2.id),
                              pair.lens1.efl, pair.lens2.efl, pair_first_rms[i_pair],
                              second_rms, lambda14, pair.cutoffangle['value'], pair.ffl, pair.lenses_gap,
                              pair.bfl, bfl_opti, efl, dist_FFi, dist_first_last_surface_lens, tmp_path_lens1,
                              tmp_path_lens2,
                              pair.lens1.diameter_minmax[0], pair.lens1.diameter_minmax[1],
                              pair.lens2.diameter_minmax[0],
                              pair.lens2.diameter_minmax[1], img_radius_tmp, pair.lens1.info, pair.lens2.info,
                              i_pair, pair.rms_detail[0]['RMS']]
                             , sep_column, "", sep_dec))

        if param['RMS_for_each_fld_wvl']:
            nb_wvl = len(pair.wvf_preprocessed[0]['wvl_and_data'])
            for i_fld in range(len(pair.wvf_preprocessed)):  # fld
                for i_wvl in range(nb_wvl):  # wvl
                    tmp_fld = pair.rms_detail[i_fld * nb_wvl + i_wvl + 1]['used_fld']
                    tmp_wvl = pair.rms_detail[i_fld * nb_wvl + i_wvl + 1]['used_wvl']
                    tmp_rms = pair.rms_detail[i_fld * nb_wvl + i_wvl + 1]['RMS']

                    file.write(data_list_to_str([tmp_fld, tmp_wvl, tmp_rms], sep_column, "", sep_dec))

        file.write(sep_row)

    file.close()
    logger.info('results exported in : ' + file_path + '.csv')
    print('results exported in : ' + file_path + '.csv')


def save_results_csv_df(param, pair_dataframe):
    logger.info('saving results in csv ...')
    print('saving results in csv ...')

    # create the file
    file_path = os.path.join(param['save_folder_path'], param['analysis_name'])
    try:
        file = open(file_path + ".csv", "x")
    except:  # this should never happen due to precedent code, but if it is, we want to be sure we can create a new file
        i = 0
        while i < 100:
            i = i + 1
            try:
                file = open(file_path + "_" + str(i) + ".csv", "x")
                file_path = file_path + "_" + str(i)
                break
            except Exception as exception:
                raise ValueError('Impossible to create the csv result file. Error is : ' + str(exception))

    sep_row = param['output_csv']['output_csv_row_separator']
    sep_column = param['output_csv']['output_csv_column_separator']
    sep_dec = param['output_csv']['output_csv_decimal_separator']

    ######## HEADER ########
    # header
    file.write("Analysis of lens pairs for optical remote focusing." + sep_row)
    file.write(sep_row)
    file.write("Analysis name : " + param['analysis_name'] + sep_row)
    file.write("File save time : " + str(datetime.now()) + sep_row)
    file.write("All distances are in mm (except wavelengths : in nm), angles are in degrees,"
               " RMS wavefront error is in waves" + sep_row)
    file.write(sep_row)
    file.write("parameters :" + sep_row)
    for pa in param:
        if pa == 'save_folder_path' and param['output_csv']['hide_path_in_csv']:
            file.write(str(pa) + sep_column + 'hidden' + sep_row)
        elif pa == 'lenses_param' and param['output_csv']['hide_path_in_csv']:
            lenses_param_tmp = param[pa].copy()
            lenses_param_tmp['LensesFolderPath'] = 'hidden'
            file.write(str(pa) + sep_column + str(lenses_param_tmp) + sep_row)
        else:
            file.write(str(pa) + sep_column + str(param[pa]) + sep_row)

    file.write(sep_row)
    file.write("WARNING : if your lenses files don't take into account the reduction of lens diameter due to their"
               " mounting, the cut-off angle can be overestimated !" + sep_row)
    file.write("WARNING : Coating is not taken into account, please check if your lenses are designed for the "
               "right wavelengths !" + sep_row)
    file.write("WARNING : Always check if lenses were imported with correct materials, and if raytracing diagram "
               "and wavefront seems correct ! (especially when pair have negative ffl and/or bfl)" + sep_row)
    file.write(sep_row)

    ######## DATA ########
    # data
    file.write("pairs :" + sep_row)

    # column names
    file.write(data_list_to_str([pair_dataframe.index.name] + [col_name for col_name in pair_dataframe]
                                , sep_column, sep_row, sep_dec))

    # data
    for i_line in range(len(pair_dataframe.index)):
        file.write(data_list_to_str([pair_dataframe.index[i_line]] + pair_dataframe.iloc[i_line].to_list()
                                    , sep_column, sep_row, sep_dec))

    file.close()
    logger.info('results exported in : ' + file_path + '.csv')
    print('results exported in : ' + file_path + '.csv')


def sort_pair_rms(pair_first_rms, pair_second_rms, index_second_rms):
    # get pairs ordonated by RMS value
    if (not pair_second_rms is None) and pair_second_rms.size != 0:  # not empty
        # pair_second_rms are RMS of pairs of index index_min_rms_tolerance (in the same order)
        pair_second_rms_sorted_index = np.argsort(pair_second_rms)  # index to sort pair_second_rms
        sorted_rms_index_best = index_second_rms[pair_second_rms_sorted_index]  # id of pairs with the best RMS, sort by
                                                                                # the RMS in pair_second_rms
    else:
        index_min_rms_tolerance_sorted = []
        sorted_rms_index_best = np.array([], dtype=np.int64)
        pair_second_rms_sorted_index = np.array([], dtype=np.int64)

    # remove pairs that are in best index to avoid duplication
    pair_first_rms_without_second = np.delete(pair_first_rms, sorted_rms_index_best)
    convertion_table_rms_pairid = np.arange(0, len(pair_first_rms), 1)
    convertion_table_rms_pairid = np.delete(convertion_table_rms_pairid, sorted_rms_index_best)

    # sort by RMS
    sorted_rms_index_only_first = convertion_table_rms_pairid[np.argsort(pair_first_rms_without_second)]
    # id of pairs sorted by their RMS in first analysis

    # all pairs sorted
    if sorted_rms_index_best.size != 0:  # If empty. [] is float64 so issues with concatenate, even when force to int type with astype...
        sorted_rms_index_all = np.concatenate((sorted_rms_index_best, sorted_rms_index_only_first))
    else:
        sorted_rms_index_all = sorted_rms_index_only_first

    return pair_second_rms_sorted_index, sorted_rms_index_all


def export_detail_pair_seqmod_txt(pair, param=None, overwrite_file=False, filename=None, dir_path=None):
    # export details about surfaces and gaps of the pair, write them in a file ".txt"
    # overwrite_file is to say if a file has the same path, should the function overwrite it ?
    # filename : if None, filename will be param['analysis_name']_pair'pair id'_SeqMod
    # dir_path : path of the folder, if None, dir_path = param['save_folder_path']
    # param can be None only if filename and dir_path aren't None

    logger.info('start to save pair surfaces and gaps information : ' + pair.name())

    if (param is None) and (filename is None or dir_path is None):
        logger.error('Error in export_detail_pair_SeqMod_txt for pair' + pair.name() +
                     "\nparam can be None only if filename AND dir_path aren't None")
        return

    # create the file
    if filename is None:
        filename = param['analysis_name'] + "_pair" + str(pair.id) + "_SeqMod"
    if dir_path is None:
        dir_path = param['save_folder_path']

    file_path = os.path.join(dir_path, filename)

    if not overwrite_file:
        try:
            file = open(file_path + ".txt", "x")
        except:  # we want to be sure we can create a new file
            i = 0
            while i < 100:
                try:
                    file = open(file_path + "_" + str(i) + ".txt", "x")
                    file_path = file_path + "_" + str(i)
                    break
                except:
                    i = i + 1

            if i >= 100:
                logger.error('Error in export_detail_pair_SeqMod_txt for pair' + pair.name() +
                             '\nfilename is already taken by another file, and impossible to find a new filename' +
                             '\nconsider running again the function but with a new, free filename')
                return
    else:
        file = open(file_path + ".txt", "w")

    # write in the file
    file.write("Analysis of lens pairs for optical remote focusing.\n\n" +
               "Analysis name : " + param['analysis_name'] + "\n" +
               "File save time : " + str(datetime.now()) + "\n" +
               "All distances are in mm (except wavelengths : in nm)\n\n" +
               "Details about sequential model of pair :\n" + pair.name() + '\n' +
               "Pair short name : " + pair.short_name + "\n\n")

    file.write(detail_seq_model_str(pair))

    logger.info('Save file ' + file_path + '.txt')


def detail_seq_model_str(pair):
    more_info = ''
    more_info = more_info + "List sequential model :\n"

    # capture the output of listing sequential model (which is output with print, not in str)
    # https://stackoverflow.com/questions/22822267/how-to-capture-print-output-of-another-module
    # https://docs.python.org/3/library/contextlib.html
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        pair.sm.list_model()
    list_model_str = f.getvalue()
    more_info = more_info + list_model_str + "\n\n"

    more_info = more_info + "wavelengths information :\n" + pair.osp.spectral_region.listobj_str() + "\n"

    more_info = more_info + "First order properties :\n"

    f2 = io.StringIO()
    with contextlib.redirect_stdout(f2):
        pair.pm.first_order_data()
    first_order_data_str = f2.getvalue()
    more_info = more_info + first_order_data_str + "\n\n"

    more_info = more_info + ("More information about surfaces and gaps (coefficients if some surfaces are asphere, "
                             "refractive index used, and more) :\n")

    for i in range(len(pair.sm.ifcs)):
        if i == pair.lens1surf[0]:
            more_info = more_info + "=========== LENS 1 START ===========\n"
        elif i == pair.lens2surf[0]:
            more_info = more_info + "=========== LENS 2 START ===========\n"

        more_info = (more_info + "INTERFACE " + str(i) + " :\n" +
                     pair.sm.ifcs[i].listobj_str())

        if i == pair.lens1surf[1]:
            more_info = more_info + "=========== LENS 1 END ===========\n\n"
        elif i == pair.lens2surf[1]:
            more_info = more_info + "=========== LENS 2 END ===========\n\n"
        else:
            more_info = more_info + '\n'

        if i < len(pair.sm.ifcs) - 1:
            more_info = (more_info + "GAP " + str(i) + " :" +
                         pair.sm.gaps[i].listobj_str())
            for wvl_weight in pair.initial_wvl_and_weight:
                wvl, weight = wvl_weight
                more_info = more_info + "RI of medium for wvl " + str(wvl) + " nm is : " + str(
                    pair.sm.gaps[i].medium.calc_rindex(wvl)) + "\n"
            more_info = more_info + "\n"
    return more_info

