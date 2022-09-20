import pandas as pd
import datetime
import importlib
from clock.get_current_time import get_current_time
from mongodb.mongo_connect import mongo_connect
from mongodb.query_request import query_request

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
            for j in range(1, settings.battery_num+1):
                volt_col_name = str(i)+'组'+str(j)+'号电池电压'
                temp_col_names.append(volt_col_name)
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
        mongo_connect()
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



