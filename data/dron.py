import pandas as pd
import numpy as np
import datetime
import importlib
from clock.get_current_time import get_current_time
from mongodb.mongo_connect import mongo_connect
from mongodb.query_request import query_request
from energy.current_parameter import current_parameter
import importlib
import warnings
warnings.filterwarnings('ignore')

class dron:

    @staticmethod
    def get_col_names():
        settings = importlib.import_module('settings')
        all_col_names = ['time', 'PLC_id']
        current_col_name = 'PCS电池电流'
        for i in range(1, settings.pack_num+1):
            for j in range(1, settings.battery_num+1):
                volt_col_name = str(i)+'组'+str(j)+'号电池电压'
                all_col_names.append(volt_col_name)
            temp_col_name1 = str(i)+'组电池温度1'
            all_col_names.append(temp_col_name1)
            temp_col_name2 = str(i)+'组电池温度2'
            all_col_names.append(temp_col_name2)
        all_col_names.append(current_col_name)
        return all_col_names

    @staticmethod
    def get_volt_col_name():
        volt_col_names = []
        settings = importlib.import_module('settings')
        for i in range(1, settings.pack_num+1):
            for j in range(1, settings.battery_num+1):
                volt_col_name = str(i)+'组'+str(j)+'号电池电压'
                volt_col_names.append(volt_col_name)
        return volt_col_names
        
    @staticmethod
    def get_temp_col_name():
        temp_col_names = []
        settings = importlib.import_module('settings')
        for i in range(1, settings.pack_num+1):
            temp_col_name1 = str(i)+'组电池温度1'
            temp_col_names.append(temp_col_name1)
            temp_col_name2 = str(i)+'组电池温度2'
            temp_col_names.append(temp_col_name2)
        return temp_col_names

    @staticmethod
    def get_data(plc):
        settings = importlib.import_module('settings')
        df_data = pd.DataFrame()
        # importlib.reload(settings)
        now_time = get_current_time()[0]
        now_time_ts = datetime.datetime.strptime(now_time, settings.fmt1)
        start_time_ts = now_time_ts - datetime.timedelta(days=settings.day_interval)
        # mongo_connect()
        data = query_request.datalog_query(start_time_ts, now_time_ts, plc, \
                                           settings.filter_for_data_collection)
        if len(data) > 0:
            for j in range(0, len(data)):
                data_series = {'time': data[j]['time']}
                data_series.update({'PLC_id': data[j]['PLC_id']})
                data_series.update(data[j]['data'])
                to_append_to_data = pd.DataFrame(data_series, index=[0])
                df_data = pd.concat([df_data, to_append_to_data], axis=0)
            df_data = df_data.sort_values(by='time', ascending=True)
            df_data = df_data.reset_index(drop=True)
        return df_data

    @staticmethod
    def dataframe_switch(plc):
        settings = importlib.import_module('settings')
        df_data = dron.get_data(plc)
        df_switched = pd.DataFrame(columns = ['time', 'Voltage.name', 'Voltage', 'Current', 'Temperature'])
        if df_data.shape[0] > 0:
            df_data['time'] = pd.to_datetime(df_data['time'])
            df_data = df_data.sort_values(by='time', ascending=True)
            Temp_cols = dron.get_temp_col_name()
            Volt_cols = dron.get_volt_col_name()
            df_data['median_T'] = np.nan
            mT_index = df_data.columns.get_loc('median_T')
            for i in range(0, df_data.shape[0]):
                T_set = []
                for j in Temp_cols:
                    T_index = df_data.columns.get_loc(j)
                    T_set.append(df_data.iloc[i, T_index])
                T_median = (np.median(T_set) - 2731)/10
                df_data.iloc[i, mT_index] = T_median
            df_temp = df_switched
            for bat in Volt_cols[:]:
                df_temp['time'] = df_data['time']
                df_temp['Voltage.name'] = bat
                df_temp['Voltage'] = df_data[bat]
                df_temp['Current'] = df_data['PCS电池电流']
                df_temp['Temperature'] = df_data['median_T']
                df_switched = df_switched.append(df_temp)
            df_switched = df_switched.sort_values(by='time', ascending=True)
            df_switched['Voltage'] /= settings.voltage_coefficient
            current_coefficient = current_parameter(plc[0])[0]
            df_switched['Current'] = np.int16(df_switched['Current'])/current_coefficient
            df_switched = df_switched.sort_values(by=['time'], ascending=True)
            df_switched = df_switched.reset_index(drop=True)
        return df_switched
        
    @staticmethod
    def find_battery_to_check(plc):
        settings = importlib.import_module('settings')
        bat_to_check = []
        df_data = dron.dataframe_switch(plc)
        df_data['time'] = pd.to_datetime(df_data['time'])
        if df_data.shape[0] > 0:
            time_set = df_data['time'].unique()
            df_ab_bat = pd.DataFrame()
            for i in range(0, len(time_set)):
                thistime = time_set[i]
                df_1t = df_data[df_data['time'] == thistime]
                for j in range(1, settings.pack_num+1):
                    search_str = str(j)+'组'
                    df_1t_1p = df_1t[df_1t['Voltage.name'].str.contains(search_str)]
                    pack_median = df_1t_1p['Voltage'].median()
                    pack_std = df_1t_1p['Voltage'].std()
                    df_1t_1p['dv'] = 0
                    v_index = df_1t_1p.columns.get_loc('Voltage')
                    dv_index = df_1t_1p.columns.get_loc('dv')
                    for k in range(0, df_1t_1p.shape[0]):
                        dv = (df_1t_1p.iloc[k, v_index] - pack_median)/pack_std
                        #dv = df_1t_1p.iloc[k, v_index] - pack_median
                        df_1t_1p.iloc[k, dv_index] = dv
                    df_ab_bat = df_ab_bat.append(df_1t_1p)
                df_ab_bat = df_ab_bat.sort_values(by='time', ascending=True)
                df_ab_bat = df_ab_bat.reset_index(drop=True)
            bat_to_check = df_ab_bat[abs(df_ab_bat['dv'])>settings.threshold_for_rms]['Voltage.name'].unique()
            return df_1t_1p # bat_to_check
        
        
        # if df_data.shape[0] > 0:
        #     time_set = df_data['time'].values[0]
        #     for i in range(0, len(time_set)):
        #         the_time = time_set[i]
        #         df_the_time = df_data[df_data['time']==str(the_time)]
                
