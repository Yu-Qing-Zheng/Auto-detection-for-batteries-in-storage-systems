from mongodb.query_request import query_request
from settings import fmt1, filter_for_energy_calculation
from energy.current_parameter import current_parameter
import pandas as pd
import numpy as np
import datetime


def median_energy_calculate(start_time, end_time, plc):
    start_time = datetime.datetime.strptime(start_time,fmt1)
    end_time = datetime.datetime.strptime(end_time, fmt1)
    data = query_request.datalog_query(start_time, end_time, plc, filter_for_energy_calculation)
    current_factor = current_parameter(plc)[0]
    current_threshold = current_parameter(plc)[1]
    med_results = []
    if len(data) > 0:
        time_set = []
        I_set = []
        forward = []
        reverse = []
        for i in range(0, len(data)):
            time_set.append(data[i]['time'])
            I_set.append(np.int16(data[i]['data']['PCS电池电流'])/current_factor)
            forward.append(round(data[i]['data']['正向有功总电能']*655.35 + data[i]['data']['正向有功总电能2']/100, 2))
            reverse.append(round(data[i]['data']['反向总有功电能']*655.35 + data[i]['data']['反向总有功电能2']/100, 2))
        data_df = pd.DataFrame()
        data_df['time'] = time_set
        data_df['current'] = I_set
        data_df['forward'] = forward
        data_df['reverse'] = reverse
        if data_df[abs(data_df['current'])>=current_threshold].shape[0] > 0:
            I_index = data_df.columns.get_loc('current')
            t_index = data_df.columns.get_loc('time')
            # f_index = data_df.columns.get_loc('forward')
            # r_index = data_df.columns.get_loc('reverse')
            I_flag = 0
            former_I_flag = 0
            static_flag_changing = 1
            I_static_flag = 0
            data_df_static = pd.DataFrame()
            # data_df = data_df.sort_values(by='time', ascending=True)
            data_df = data_df.reset_index(drop=True)
            start = data_df[abs(data_df['current'])>=current_threshold].index.values[0]
            end = data_df.shape[0]

            for i in range(start, end):
                if abs(data_df.iloc[i, I_index]) < current_threshold:
                    data_df.iloc[i, I_index] = 0
                if data_df.iloc[i, I_index] < 0:
                    former_I_flag = I_flag
                    I_flag = -1
                    if static_flag_changing == 1:
                        I_static_flag = -1
                if data_df.iloc[i, I_index] > 0:
                    former_I_flag = I_flag
                    I_flag = 1
                    if static_flag_changing == 1:
                        I_static_flag = 1
                if data_df.iloc[i, I_index] == 0:
                    former_I_flag = I_flag
                    I_flag = 0
                    static_flag_changing = 0
                    I_static_flag = I_static_flag
                # print(data_df.iloc[i, t_index], data_df.iloc[i, I_index], I_static_flag, I_flag)
                if I_static_flag*I_flag == -1 or former_I_flag*I_flag == -1 or i == (end-1):
                    data_df_static = data_df_static.append(data_df.iloc[i, :])
                    static_flag_changing = 1
            data_df_static = data_df_static.drop_duplicates()
            if data_df_static.shape[0] > 1:
                data_df_static['forward.diff'] = data_df_static['forward'].diff()
                data_df_static['reverse.diff'] = data_df_static['reverse'].diff()
                ts = start_time
                data_df_static['time'] = pd.to_datetime(data_df_static['time'])
                df_results = pd.DataFrame()
                while ts <= end_time:
                    st = ts + datetime.timedelta(days=1)
                    data_df_one_day = data_df_static[(data_df_static['time']>=str(ts))&\
                                                    (data_df_static['time']<str(st))]
                    max_E_f = data_df_one_day['forward.diff'].max()
                    max_E_r = data_df_one_day['reverse.diff'].max()
                    to_append = pd.DataFrame({'time': [str(ts)], 'max_forward': [max_E_f], 'max_reverse': [max_E_r]})
                    df_results = df_results.append(to_append)
                    ts = st
                med_max_f = round(df_results['max_forward'].median(), 2)
                med_max_r = round(df_results['max_reverse'].median(), 2)
                med_results = [med_max_f, med_max_r]
    return med_results
            
            
            
