from clock.get_current_time import get_current_time
from energy.median_energy_calculate import median_energy_calculate
# from settings import time_fill1, time_fill2
import importlib

def energy_threshold(start_time, plc): 
    settings = importlib.import_module('settings')
    # importlib.reload(settings)
    now_time = get_current_time()
    median_max_forward = -1
    median_max_reverse = -1
    result_flag = 0
    start_date,b,c = start_time.partition(' ')
    median_e_list = median_energy_calculate(start_date+settings.time_fill1, \
                    now_time[2]+settings.time_fill2, plc)
    if len(median_e_list) > 0:
        median_max_forward = median_e_list[0]
        median_max_reverse = median_e_list[1]
        result_flag = 1
    return [median_max_forward, median_max_reverse, result_flag]
