import datetime
import os
import pandas as pd
from clock.get_current_time import get_current_time
from plcid.mysql_model import *
from settings import plc_csv_path, plc_csv_file, plc_query_control_file, fmt1, day_threshold
import warnings
warnings.filterwarnings('ignore')

def query_all_plc():
    today = datetime.datetime.now().day
    if os.path.exists(plc_csv_path+plc_query_control_file):
        last_update = open(plc_csv_path+plc_query_control_file, 'r')
        if last_update.readline() == str(today):
            df_plc_list = pd.read_csv(plc_csv_path+plc_csv_file)
            plc_list = df_plc_list['plc'].values
            return plc_list
    else:
        last_update = open(plc_csv_path+plc_query_control_file, 'w')
        last_update.write(str(today))

    mysql_session = get_session()
    query_result = mysql_session.query(Plc.plc_id).filter(Plc.device_id.isnot(None)).all()
    if not query_result:
        return []
    query_result = list(list(zip(*query_result))[0])
    mysql_session.close()

    df_plc_new_list = pd.DataFrame(columns=['time', 'plc', 'restored_flag'])
    now_time = get_current_time()[0]
    # now_time_ts = datetime.datetime.strptime(now_time, fmt1)
    if os.path.exists(plc_csv_path+plc_csv_file):
        df_plc_list = pd.read_csv(plc_csv_path+plc_csv_file)
        for i in range(0, len(query_result)):
            df_1plc = df_plc_list[df_plc_list['plc']==int(query_result[i])]
            if df_1plc.shape[0] > 0 and df_1plc['restored_flag'].values[0] == 0:
                to_append = pd.DataFrame({'time': df_1plc['time'].values, \
                                          'plc': [query_result[i]], \
                                          'restored_flag': df_1plc['restored_flag'].values})
            else:
                to_append = pd.DataFrame({'time': now_time, 'plc': \
                                          [query_result[i]], 'restored_flag': [0]})
            df_plc_new_list = df_plc_new_list.append(to_append)
            # df_plc_new_list = pd.concat([df_plc_new_list, to_append], axis=0, ignore_index=True)
        df_plc_new_list = df_plc_new_list.loc[:, ~df_plc_new_list.columns.str.contains("^Unnamed")]
        df_plc_new_list.to_csv(plc_csv_path+plc_csv_file)
    else:
        for i in range(0, len(query_result)):
            to_append = pd.DataFrame({'time': now_time, \
                                      'plc': [query_result[i]], 'restored_flag': [0]})
            df_plc_new_list = df_plc_new_list.append(to_append)
            # df_plc_new_list = pd.concat([df_plc_new_list, to_append], axis=0, ignore_index=True)
        df_plc_new_list = df_plc_new_list.loc[:, ~df_plc_new_list.columns.str.contains("^Unnamed")]
        df_plc_new_list.to_csv(plc_csv_path+plc_csv_file)

    last_update = open(plc_csv_path+plc_query_control_file, 'w')
    last_update.write(str(today))
    return df_plc_new_list['plc'].values

