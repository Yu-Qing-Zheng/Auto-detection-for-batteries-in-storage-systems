import pandas as pd
import datetime
import sys 
sys.path.append("..")
from mongodb.query_request import query_request
from settings import plc_csv_file, plc_csv_path, filter_for_energy_threshold, fmt1
from clock.get_current_time import get_current_time

df_plc_list = pd.read_csv('.'+plc_csv_path+plc_csv_file)
plcset = df_plc_list['plc'].values
df_thres = pd.DataFrame()
for i in range(0, len(plcset)):
    plc = [int(plcset[i])]
    print(plc)
    start_time = str(df_plc_list[df_plc_list['plc']==plc[0]]['time'].values[0])
    start_time_ts = datetime.datetime.strptime(start_time, fmt1)
    now_time = get_current_time()
    now_time_ts = datetime.datetime.strptime(now_time[0], fmt1)
    data = query_request.threshold_query(start_time_ts, now_time_ts, plc, filter_for_energy_threshold)
    if len(data) > 0:
        thres_f = data[0]['median_max_forward']
        thres_r = data[0]['median_max_reverse']
        if thres_f >= 0 and thres_r >= 0:
            print(start_time_ts)
            thres_end_time_ts = start_time_ts + datetime.timedelta(days=7)
            print(thres_end_time_ts)
            to_append = pd.DataFrame({'plc': [plc[0]], '开始时间': [start_time_ts], '结束时间': [thres_end_time_ts], \
                                      '最大单次充电量': [thres_f], '最大单次放电量': [thres_r]})
            df_thres = df_thres.append(to_append)
df_thres = df_thres.sort_values(by = 'plc', ascending=True)
df_thres = df_thres.reset_index(drop=True)
df_thres = df_thres.loc[:, ~df_thres.columns.str.contains("^Unnamed")]
df_thres.to_csv('./有效最大单次充放电量.csv')