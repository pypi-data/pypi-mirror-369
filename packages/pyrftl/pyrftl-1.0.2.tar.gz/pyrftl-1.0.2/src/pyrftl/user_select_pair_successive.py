import pyrftl.func.lens_selection as fls


if __name__ == '__main__':

    ######### USER PARAMETERS #########
    LensesFolderPath = r"PATH\lenses\Lenses_achromats"

    ######### ADVANCED USER PARAMETERS #########
    check_air_gap = True
    delete_air_gap = False

    lens_diameter_min = None
    lens_diameter_max = None
    lens_efl_min = None
    lens_efl_max = None

    ######### USER PARAMETERS #########
    # expected_focal_length = 162.4
    expectedFocalLength = fls.f_tl2_from_f_tl1(60, 180, 180, 50, 180, 1.33, 1)

    distMinBetweenLenses = None  # mm
    distMinBeforeLenses = None
    distMinAfterLenses = None

    distMaxBetweenLenses = None
    distMaxBeforeLenses = None
    distMaxAfterLenses = None

    wvl = [486, 588, 656]  # in nm, wavelengths : can be one : wvl = [540] or several wvl = [486, 588, 656]
    # pupil = 6.84  # diameter, in mm
    pupil = fls.pupil_diameter(0.95, 50, 180, 1.33, 1.2)  # 6.5
    # cut_off_angle_min = 4.2  # in °, maximum field angle that should be able to pass inside the tube length
    cut_off_angle_min = fls.max_fld_angle(26.5, 50, 180, 1.33, 26.5, 60)  # 4.21

    config = ["A","B","C","D"]
    # config can be only one kind : config = "A", or it is possible to use several configs : config = ["A", "B", "D"]
    # config define what are lenses orientation in the pair. With ( the more curved side of the lens, | the less curved
    # side, and the objective in remote refocus is at the infinite side, we have :
    # "A" : infinity |) |) image    "B" : infinity |) (| image
    # "C" : infinity (| (| image    "D" : infinity (| |) image
    # None : lenses orientations are the ones of the file from where they are obtained

    save_Folder_Path = r'SAVEPATH'  # path of the folder where results should be save
    analysis_name = None  # should be None or a str. If None, will be : PyRFTL_year_month_day_hourhminute

    dist_pupil_pair = None  # in mm, distance between the pupil and the first lens.
    # if None, distance will be pair front focal length
    # for remote focusing and Oblique Plane Microscopy, put None

    ######### ADVANCED USER PARAMETERS #########
    thin_lens_first_analysis = True  # if True, will do a first selection of pairs with a thin lens analysis,
                                     # for distances criterias.
                                     # In any case, will definitively select pairs with ray tracing.
    accepted_error_in_dist_thin_lens_percent = 10  # in percent, between 0 and 100.

    number_best_pair_high_comparison = 10
    # None if keep all with RMS > tolerance * lambda/14, if an integer, keep the given number of pairs that have
    # minimum RMS, and have RMS > tolerance * lambda/14
    # The maximum number of best pairs that are selected for an RMS comparison with more rays
    tolerance_wavefront_RMS_high = 10  # in percent, between 0 and 100

    nb_subprocesses = None  # The number of subprocesses to use in parallel for multiprocessing : int or None
    # if None, it will be equal to the number of cores of the CPU
    force_affinity_core = True  # in some case, the multiprocessing does not use all cpu cores it should.
    # If it is the case on your computer, you can put force_affinity_core to True. It will try to force the use of
    # a different cpu core for each subprocess. Some stuff took time to be loaded by cores, so even with this parameter,
    # your CPU will not be at 100% usage all the time

    output_csv_column_separator = ';'
    output_csv_row_separator = '\n'
    output_csv_decimal_separator = '.'
    hide_path_in_csv = False
    # bool to say if should hide or not the main path of lenses in output csv (should just show the path after
    # folder_lenses_path if True)
    # WARNING !!! even with this parameter, complete path will be output in log file. hide only in csv output file

    save_roa = 'best'  # 'no', 'best', 'all'
    # save rayoptics optical model : 'no' : don't save, 'best' : save only pairs with best rms (rms<1/14, and
    # in the top number_best_pair_high_comparison number of pairs)
    # 'all' : save it for all pairs

    save_seq_detail = 'best'  # 'no', 'best', 'all'
    # save details about sequential model in a txt file : 'no' : don't save, 'best' : save only pairs with best rms (rms
    # <1/14, and in the top number_best_pair_high_comparison number of pairs)
    # 'all' : save it for all pairs
    # it is recommended to manually check if pairs you want to use were well generated, so to use 'best' or 'all'

    ######### REALLY ADVANCED USER PARAMETERS DO NOT MODIFY IF NO GOOD REASON #########
    best_focus_fast = True
    # If True, put the image at RMS lower wavefront error plane for field 0°, if False, put the image at bfl
    nbRays_first_comparison = 16
    nbRays_high_comparison = 64

    cut_off_angle_test_end = None
    # cut-off angle higher than this value will not be calculated and will be considered equal to this value
    # should be higher than fldAngleMin. If cut_off_angle_test_end < fldAngleMin, it will be set :
    # cut_off_angle_test_end = fldAngleMin + 2*cut_off_angle_precision
    # by default, with "cut_off_angle_test_end = None", it is set : cut_off_angle_test_end = 45° if fldAngleMin < 35°,
    # fldAngleMin*2 else

    cut_off_angle_precision = 0.1  # in °

    polychromatic = 'rmse_rms'
    # in the case of multi-wavelengths, formula to use as criteria
    # 'rmse_rms' is the root mean square of the root mean square error of wavelength wavefront aberrations
    # 'worst' is the worst root mean square error of wavefront aberrations

    focus_polychromatic = 'ref_wvl_i'
    # in multi-wavelength case, how to set the image position for the 0° field, before getting the RMSE at max field angle
    # 'ref_wvl_i' align with the reference wavelength
    # 'rmse_rms' align with the RMS of RMSE of wavelengths wavefront errors

    save_ram = "max"
    # "no" "medium" "max"
    # to use less computer memory while running the software. "no" is not recommended if you compute on a lot of lenses.

    wvl_and_weight = None
    # wvl_and_weight : if None, will use wvl, and give a weight of 1 for all wavelengths.
    # weight is currently not implemented, so it is currently useless to put something else than None for wvl_and_weight.
    # to define wvl and weight, it should be on the shape : [(wvl1,weight1),(wvl2,weight2),etc]
    # for example : [(510,1), (560,1), (630,2)]




    ###### NO MORE USER PARAMETERS BELOW THIS LINE DO NOT MODIFY #####
    from pyrftl.select_pair_successive import select_pair
    from pyrftl.func.save import create_save_folder

    if wvl_and_weight is None:
        if not isinstance(wvl, list):
            wvl = [wvl]

        wvl_and_weight = []

        for wvl_i in wvl:
            wvl_and_weight.append((wvl_i, 1))

    if nb_subprocesses is None :
        import multiprocess as mp
        nb_subprocesses = mp.cpu_count()

    complete_save_Folder_Path, analysis_name, start_time = create_save_folder(save_Folder_Path, analysis_name)

    dist_criteria = {'O1O2_min': distMinBetweenLenses, 'O1O2_max': distMaxBetweenLenses, 'ffl_min': distMinBeforeLenses,
                     'ffl_max': distMaxBeforeLenses, 'bfl_min': distMinAfterLenses, 'bfl_max': distMaxAfterLenses,
                     'tolerance_prcent': accepted_error_in_dist_thin_lens_percent}

    lenses_param = {'LensesFolderPath':LensesFolderPath, 'check_air_gap':check_air_gap, 'delete_air_gap':delete_air_gap,
                    'lens_diameter_min':lens_diameter_min, 'lens_diameter_max':lens_diameter_max,
                    'lens_efl_min':lens_efl_min,'lens_efl_max':lens_efl_max}

    output_csv = {'output_csv_column_separator': output_csv_column_separator,
                  'output_csv_row_separator': output_csv_row_separator, 'hide_path_in_csv': hide_path_in_csv,
                  'output_csv_decimal_separator': output_csv_decimal_separator}

    param = {'expected_focal_length': expectedFocalLength, 'dist_criteria': dist_criteria, 'lenses_param' : lenses_param,
             'thin_lens_first_analysis': thin_lens_first_analysis,
             'save_ram': save_ram, 'config': config, 'wvl_and_weight': wvl_and_weight, 'pupil': pupil,
             'dist_pupil_pair' : dist_pupil_pair, 'cut_off_angle_min': cut_off_angle_min,
             'cut_off_angle_test_end': cut_off_angle_test_end, 'cut_off_angle_precision': cut_off_angle_precision,
             'best_focus_fast': best_focus_fast, 'nbRays_first_comparison': nbRays_first_comparison,
             'nbRays_high_comparison': nbRays_high_comparison,
             'number_best_pair_high_comparison': number_best_pair_high_comparison,
             'tolerance_wavefront_RMS_high_percent': tolerance_wavefront_RMS_high,
             'save_folder_path': complete_save_Folder_Path, 'analysis_name': analysis_name,
             'nb_subprocesses' : nb_subprocesses,
             'polychromatic' : polychromatic, 'focus_polychromatic' : focus_polychromatic,
             'force_affinity_core' : force_affinity_core, 'output_csv': output_csv,
             'save_roa': save_roa, 'save_seq_detail': save_seq_detail,
             'start_time':start_time}

    pair_list = select_pair(param)

