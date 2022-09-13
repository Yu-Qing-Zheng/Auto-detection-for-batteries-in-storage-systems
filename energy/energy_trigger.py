from difflib import restore
from clock.get_current_time import get_current_time
from clock.time_count import time_count
from energy.maximum_energy_calculate import maximum_energy_calculate
from energy.energy_threshold import energy_threshold
from mongodb.query_request import query_request
from settings import day_threshold, threshold_factor, \
                     filter_for_energy_threshold, fmt1, plc_csv_path, plc_csv_file
from mongodb.mongo_insert import mongo_insert
import datetime
import pandas as pd

def energy_trigger(plc):
    df_plc_list = pd.read_csv(plc_csv_path+plc_csv_file)
    start_time = str(df_plc_list[df_plc_list['plc']==plc[0]]['time'].values[0])
    print('start_time:', start_time)
    start_time_ts = datetime.datetime.strptime(start_time, fmt1)
    now_time = get_current_time()
    now_time_ts = datetime.datetime.strptime(now_time[0], fmt1)
    days_count = time_count(start_time, now_time[0])
    print('days_count', round(days_count, 2))
    restore_flag = df_plc_list[df_plc_list['plc']==plc[0]]['restored_flag'].values[0]
    energy_flag = 0
    if days_count < day_threshold or restore_flag != 0:
        list_threshold = energy_threshold(start_time, plc)
        if list_threshold[2] == 1:
            median_max_f = list_threshold[0]
            median_max_r = list_threshold[1]
        else:
            median_max_f = -1
            median_max_r = -1
        energy_flag = 1
        mongo_insert.energy_threshold_insert(plc=plc[0], 
                                             time=now_time_ts, 
                                             median_max_forward=median_max_f, 
                                             median_max_reverse=median_max_r)
    else:
        max_e_list = maximum_energy_calculate(plc)
        thres_parameter = query_request.threshold_query(start_time_ts, now_time_ts, plc, \
                              filter_for_energy_threshold)
        print('max_e_list:', max_e_list)
        if len(max_e_list) > 0:
            forward_now = max_e_list[0]
            reverse_now = max_e_list[1]
            print(start_time_ts, now_time_ts)
            if len(thres_parameter) > 0:
                median_max_f = thres_parameter[0]["median_max_forward"]
                median_max_r = thres_parameter[0]["median_max_reverse"]
                print('thres_list:', median_max_f, median_max_r)
                if median_max_f > 0 and median_max_r > 0:
                    if forward_now < threshold_factor*median_max_f or \
                        reverse_now < threshold_factor*median_max_r:
                        energy_flag = 1
                    else:
                        print('no need for a diagnose!')
                else:
                    print('no validated threshold!')
                    index_to_modify = df_plc_list[df_plc_list['plc']==plc[0]].index.values[0]
                    col_restored_flag = df_plc_list.columns.get_loc('restored_flag')
                    df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                    df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                    df_plc_list.to_csv(plc_csv_path+plc_csv_file)

            else:
                print('no threshold found!')
                index_to_modify = df_plc_list[df_plc_list['plc']==plc[0]].index.values[0]
                col_restored_flag = df_plc_list.columns.get_loc('restored_flag')
                df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                df_plc_list.to_csv(plc_csv_path+plc_csv_file)
        else:
            if len(thres_parameter) > 0:
                median_max_f = thres_parameter[0]["median_max_forward"]
                median_max_r = thres_parameter[0]["median_max_reverse"]
                print('thres_list:', median_max_f, median_max_r)
                if ~(median_max_f < 0 and median_max_r > 0):
                    print('no validated threshold and no maximum forward/reverse calculated!')
                    index_to_modify = df_plc_list[df_plc_list['plc']==plc[0]].index.values[0]
                    col_restored_flag = df_plc_list.columns.get_loc('restored_flag')
                    df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                    df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                    df_plc_list.to_csv(plc_csv_path+plc_csv_file)

            else:
                print('no threshold found and no maximum forward/reverse calculated!')
                index_to_modify = df_plc_list[df_plc_list['plc']==plc[0]].index.values[0]
                col_restored_flag = df_plc_list.columns.get_loc('restored_flag')
                df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                df_plc_list.to_csv(plc_csv_path+plc_csv_file)
            

    mongo_insert.energy_trigger_insert(plc=plc[0], 
                                       time=now_time[0], 
                                       energy_flag=energy_flag)
    print('energy_flag:', energy_flag)
    return energy_flag

       