from clock.get_current_time import get_current_time
from clock.time_count import time_count
from energy.maximum_energy_calculate import maximum_energy_calculate
from energy.energy_threshold import get_energy_threshold
# from mongodb.query_request import query_request
# from settings import day_threshold, threshold_factor, restored_threshold_factor, \
#                      filter_for_energy_threshold, fmt1, plc_csv_path, plc_csv_file
# from mongodb.mongo_insert import mongo_insert
from mysql.mysql_add_modify import mysql_add_modify
from mysql.mysql_model import *
import importlib
import datetime
import pandas as pd

def energy_trigger(plc):
    settings = importlib.import_module('settings')
    # importlib.reload(settings)
    df_plc_list = pd.read_csv(settings.plc_csv_path+settings.plc_csv_file)
    start_time = str(df_plc_list[df_plc_list['plc']==plc[0]]['time'].values[0])
    print('start_time:', start_time)
    start_time_ts = datetime.datetime.strptime(start_time, settings.fmt1)
    now_time = get_current_time()
    now_time_ts = datetime.datetime.strptime(now_time[0], settings.fmt1)
    days_count = time_count(start_time, now_time[0])
    print('days_count', round(days_count, 2))
    restore_flag = df_plc_list[df_plc_list['plc']==plc[0]]['restored_flag'].values[0]
    index_to_modify = df_plc_list[df_plc_list['plc']==plc[0]].index.values[0]
    col_restored_flag = df_plc_list.columns.get_loc('restored_flag')
    energy_flag = settings.flag_for_override
    if days_count < settings.day_threshold or restore_flag != 0:
        print(start_time, plc)
        list_threshold = get_energy_threshold(start_time, plc)
        if list_threshold[2] == 1:
            median_max_f = list_threshold[0]
            median_max_r = list_threshold[1]
        else:
            median_max_f = -1
            median_max_r = -1
        energy_flag = settings.flag_for_threshold_calculating
        # mongo_insert.energy_threshold_insert(plc=plc[0], 
        #                                      time=now_time_ts,
        #                                      median_max_forward=median_max_f, 
        #                                      median_max_reverse=median_max_r)
        mysql_add_modify.threshold(plc[0], median_max_f, median_max_r, now_time_ts)
    else:
        max_e_list = maximum_energy_calculate(plc)
        # thres_parameter = query_request.threshold_query(start_time_ts, now_time_ts, plc, \
        #                       settings.filter_for_energy_threshold)
        mysql_session = get_session()
        thres_parameter = mysql_session.query(energy_threshold).filter(energy_threshold.plc_id==plc).all()
        mysql_session.close()
        print('max_e_list:', max_e_list)
        if len(max_e_list) > 0:
            forward_now = max_e_list[0]
            reverse_now = max_e_list[1]
            print(start_time_ts, now_time_ts)
            if len(thres_parameter) > 0:
                # median_max_f = thres_parameter[0]["median_max_forward"]
                # median_max_r = thres_parameter[0]["median_max_reverse"]
                median_max_f = thres_parameter[0].median_max_forward
                median_max_r = thres_parameter[0].median_max_reverse
                print('thres_list:', median_max_f, median_max_r)
                if median_max_f > 0 and median_max_r > 0: 
                    if forward_now > 0 and reverse_now > 0:
                        if forward_now < settings.threshold_factor*median_max_f or \
                            reverse_now < settings.threshold_factor*median_max_r:
                            energy_flag = settings.flag_for_abnormal
                        else:
                            print('no need for a diagnose!')
                            energy_flag = settings.flag_for_normal
                        if forward_now > settings.restored_threshold_factor*median_max_f \
                            or reverse_now > settings.restored_threshold_factor*median_max_r:
                            print('outdated threshold!')
                            df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                            df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                            df_plc_list.to_csv(settings.plc_csv_path+settings.plc_csv_file)
                    else:
                        print('no charging or discharging in last 48h.')
                else:
                    print('no valid threshold!')
                    df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                    df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                    df_plc_list.to_csv(settings.plc_csv_path+settings.plc_csv_file)
            else:
                print('no threshold found!')
                df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                df_plc_list.to_csv(settings.plc_csv_path+settings.plc_csv_file)
        else:
            if len(thres_parameter) > 0:
                # median_max_f = thres_parameter[0]["median_max_forward"]
                # median_max_r = thres_parameter[0]["median_max_reverse"]
                median_max_f = thres_parameter[0].median_max_forward
                median_max_r = thres_parameter[0].median_max_reverse
                print('thres_list:', median_max_f, median_max_r)
                if median_max_f <= 0 or median_max_r <= 0:
                    print('no valid threshold and no maximum forward/reverse calculated!')
                    df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                    df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                    df_plc_list.to_csv(settings.plc_csv_path+settings.plc_csv_file)

            else:
                print('no threshold found and no maximum forward/reverse calculated!')
                df_plc_list.iloc[index_to_modify, col_restored_flag] = 1
                df_plc_list = df_plc_list.loc[:, ~df_plc_list.columns.str.contains("^Unnamed")]
                df_plc_list.to_csv(settings.plc_csv_path+settings.plc_csv_file)
            

    # mongo_insert.energy_trigger_insert(plc=plc[0], 
    #                                    time=now_time[0], 
    #                                    energy_flag=energy_flag)
    mysql_add_modify.trigger(plc[0], energy_flag, now_time_ts)
    print('energy_flag:', energy_flag)
    return energy_flag

       