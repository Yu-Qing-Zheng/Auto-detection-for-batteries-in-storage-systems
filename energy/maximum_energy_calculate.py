from mongodb.query_request import query_request
from clock.get_current_time import get_current_time
from settings import fmt1, filter_for_energy_calculation, day_interval
from energy.current_parameter import current_parameter
import pandas as pd
import numpy as np
import datetime


def maximum_energy_calculate(plc):
    ts = get_current_time()[0]
    start_time = datetime.datetime.strptime(ts,fmt1) - datetime.timedelta(days=day_interval)
    end_time = datetime.datetime.strptime(ts,fmt1)
    data = query_request.datalog_query(start_time, end_time, plc, filter_for_energy_calculation)
    current_factor = current_parameter(plc)[0]
    current_threshold = current_parameter(plc)[1]
    max_results = []
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
                max_forward = round(abs(data_df_static['forward'].diff()).max(), 2)
                max_reverse = round(abs(data_df_static['reverse'].diff()).max(), 2)
                max_results = [max_forward, max_reverse]
    return max_results
                # return data_df_static#[(data_df_static['forward'].diff()!=0)|(data_df_static['reverse'].diff()!=0)]

# def status_flag1(plc):
#     ts = get_current_time()[0]
#     start_time = datetime.datetime.strptime(ts,fmt1) - datetime.timedelta(days=day_interval)
#     end_time = datetime.datetime.strptime(ts,fmt1)
#     data = query_request(start_time, end_time, plc, filter_for_energy_calculation)
#     time_set = []
#     I_set = []
#     forward = []
#     reverse = []
#     for i in range(0, len(data)):
#         time_set.append(data[i]['time'])
#         I_set.append(np.int16(data[i]['data']['PCS电池电流']))
#         forward.append(round(data[i]['data']['正向有功总电能']*655.35 + data[i]['data']['正向有功总电能2']/100, 2))
#         reverse.append(round(data[i]['data']['反向总有功电能']*655.35 + data[i]['data']['反向总有功电能2']/100, 2))
#     data_df = pd.DataFrame()
#     data_df['time'] = time_set
#     data_df['current'] = I_set
#     data_df['forward'] = forward
#     data_df['reverse'] = reverse
#     I_index = data_df.columns.get_loc('current')
#     f_index = data_df.columns.get_loc('forward')
#     r_index = data_df.columns.get_loc('reverse')
#     data_df_static = data_df[abs(data_df['current'])<=10]
#     for i in range(0, data_df.shape[0]-1):
#         if data_df.iloc[i, I_index]*data_df.iloc[i+1, I_index] != 0:
#             if (data_df.iloc[i, I_index]/abs(data_df.iloc[i, I_index]))*\
#                 (data_df.iloc[i+1, I_index]/abs(data_df.iloc[i+1, I_index])) < 0:
#                 data_df_static = data_df_static.append(data_df.iloc[i, :])
#     data_df_static = data_df_static.sort_values(by='time', ascending=False)
#     data_df_static['forward.diff'] = data_df_static['forward'].diff()
#     data_df_static['reverse.diff'] = data_df_static['reverse'].diff()
#     #for i in range(0, len(data)):
        
#     max_forward = abs(data_df_static['forward'].diff()).max()
#     max_reverse = abs(data_df_static['reverse'].diff()).max()
#     #return data_df_static#[(data_df_static['forward'].diff()!=0)|(data_df_static['reverse'].diff()!=0)]
