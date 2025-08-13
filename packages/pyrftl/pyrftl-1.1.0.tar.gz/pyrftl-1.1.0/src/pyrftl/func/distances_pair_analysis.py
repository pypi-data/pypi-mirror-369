# import from general libraries
import logging
from decimal import Decimal

# import from PyRFTL
from pyrftl.func.various_stuff import is_between

logger = logging.getLogger('PyRFTL')
# log level
LOG_DEBUG = 10
LOG_INFO = 20
LOG_WARNING = 30
LOG_ERROR = 40
LOG_CRITICAL = 50

# which pair to add is the main function to decide which pairs met geometrical distances criteria
# it took two lenses and call which_config_to_add to decide which config of this pair can be used
# this call check_pair_thin_lens to check if the pair met thin lenses distances
# call then check_pair_ray_tracing which check distances with check_pair_dist_ray and then
# check cut-off angle


def check_pair_thin_lens(pair, dist_criteria):
    # this function check if the pair met distances criteria based on thin lens analysis
    # it returns a boolean that said if pair is ok with parameters

    # get a % higher than 0
    if (dist_criteria['tolerance_prcent'] is None) or (
            dist_criteria['tolerance_prcent'] < 0):  # "is None" SHOULD BE before "or ... <0"
        tolerance_prcent = 0
    else:
        tolerance_prcent = dist_criteria['tolerance_prcent']

    # convert the % in multiplying factor
    acc_error_add_mult = 1 + 0.01 * tolerance_prcent
    acc_error_remove_mult = 1 - 0.01 * tolerance_prcent

    # change the min and max distances depending on tolerances
    if dist_criteria['O1O2_min'] is None:
        o1_o2_min = None
    elif dist_criteria['O1O2_min'] < 0:
        o1_o2_min = dist_criteria['O1O2_min'] * acc_error_add_mult
    else:
        o1_o2_min = dist_criteria['O1O2_min'] * acc_error_remove_mult

    if dist_criteria['O1O2_max'] is None:
        o1_o2_max = None
    elif dist_criteria['O1O2_max'] < 0:
        o1_o2_max = dist_criteria['O1O2_max'] * acc_error_remove_mult
    else:
        o1_o2_max = dist_criteria['O1O2_max'] * acc_error_add_mult

    if dist_criteria['ffl_min'] is None:
        ffl_min = None
    elif dist_criteria['ffl_min'] < 0:
        ffl_min = dist_criteria['ffl_min'] * acc_error_add_mult
    else:
        ffl_min = dist_criteria['ffl_min'] * acc_error_remove_mult

    if dist_criteria['ffl_max'] is None:
        ffl_max = None
    elif dist_criteria['ffl_max'] < 0:
        ffl_max = dist_criteria['ffl_max'] * acc_error_remove_mult
    else:
        ffl_max = dist_criteria['ffl_max'] * acc_error_add_mult

    if dist_criteria['bfl_min'] is None:
        bfl_min = None
    elif dist_criteria['bfl_min'] < 0:
        bfl_min = dist_criteria['bfl_min'] * acc_error_add_mult
    else:
        bfl_min = dist_criteria['bfl_min'] * acc_error_remove_mult

    if dist_criteria['bfl_max'] is None:
        bfl_max = None
    elif dist_criteria['bfl_max'] < 0:
        bfl_max = dist_criteria['bfl_max'] * acc_error_remove_mult
    else:
        bfl_max = dist_criteria['bfl_max'] * acc_error_add_mult

    # check criteria

    if ffl_min is None :
        fo1_max = None
    else :
        fo1_max = -ffl_min

    if ffl_max is None:
        fo1_min = None
    else:
        fo1_min = -ffl_max

    good_o1_o2 = is_between(pair.thin_lens_analysis.O1O2, o1_o2_min, o1_o2_max)
    good_fo1 = is_between(pair.thin_lens_analysis.FO1, fo1_min, fo1_max)
    good_o2_fi = is_between(pair.thin_lens_analysis.O2Fi, bfl_min, bfl_max)

    if good_o1_o2 and good_fo1 and good_o2_fi:
        return True
    else:
        return False


def check_pair_dist_ray(pair, dist_criteria):
    # this function check if the pair met distances criteria based on RayOptics analysis
    # it returns a boolean that said if pair is ok with parameters

    # opp_ffl = -pair.ffl
    
    good_ffl = is_between(pair.ffl, dist_criteria['ffl_min'], dist_criteria['ffl_max'])
    good_bfl = is_between(pair.bfl, dist_criteria['bfl_min'], dist_criteria['bfl_max'])
    good_distance_mid = is_between(pair.lenses_gap, dist_criteria['O1O2_min'],
                                   dist_criteria['O1O2_max'])  # distance between two lenses of the pair

    if good_ffl and good_bfl and good_distance_mid:
        return True
    else:
        return False


def check_pair_ray_tracing(pair, param):
    # check with geometrical ray tracing if the pair check distances and cut-off angle criteria

    ####### DISTANCES #######
    # check if distances met criteria
    if not check_pair_dist_ray(pair, param['dist_criteria']):
        why_not_add_pair = ("Pair is rejected by first order ray tracing analysis, it does not meet distances "
                            "criteria. You can change them if needed.")
        return False, why_not_add_pair

    ####### CUT-OFF ANGLE #######
    # check if cut-off angle is wide enough
    # initialisation
    if param['cut_off_angle_test_end'] is None:
        if param['cut_off_angle_min'] < 35 :
            angle_end = 45
        else :
            angle_end = 2 * param['cut_off_angle_min']
    elif param['cut_off_angle_test_end'] < param['cut_off_angle_min']:
        angle_end = param['cut_off_angle_min'] + 2 * param['cut_off_angle_precision']
    else:
        angle_end = param['cut_off_angle_test_end']

    # get cut-off angle of pair
    pair.determine_cutoffangle_dichotomy(param['cut_off_angle_min'], angle_end, param['cut_off_angle_precision'])
    cut_off_angle = pair.cutoffangle['value']

    # check cut-off angle
    if cut_off_angle is None:
        why_not_add_pair = ('Cut-off angle is too small (lower than ' + str(param['cut_off_angle_min']) + ' degrees)')
        return False, why_not_add_pair

    elif cut_off_angle < Decimal(str(param['cut_off_angle_min'])):
        why_not_add_pair = 'Cut-off angle is too small : ' + str(cut_off_angle) + ' degrees'
        return False, why_not_add_pair

    else:  # cut-off angle <= cut_off_angle_min
        return True, ' '
