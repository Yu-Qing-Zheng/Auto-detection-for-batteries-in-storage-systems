from mysql.mysql_model import *
from mysql.mysql_add_modify import mysql_add_modify
from mysql.mysql_to_df import mysql_to_df
from soc.runEKF import runEKF
from soh.runSOH import runSOH
from data.dron import dron
import pandas as pd
import numpy as np
import importlib

class param_calculate:

    @staticmethod
    def sox_upload():
        settings = importlib.import_module('settings')
        plc_set = [75]
        df_plc = mysql_to_df('diagnose_trigger')
        plc_set = df_plc['plc_id'].unique()
        df_all = pd.DataFrame()
        for plc in plc_set:
            plc = int(plc)
            mysql_session = get_session()
            plc_status_query = mysql_session.query(diagnose_trigger).filter(diagnose_trigger.plc_id==plc).all()
            mysql_session.close()
            if plc_status_query[0].energy_flag != settings.flag_for_abnormal:
                continue
            df_data = dron.find_battery_to_check([plc])
            if df_data.shape[0] > 0:
                bat_to_check_set = df_data['Voltage.name'].unique()
                if len(bat_to_check_set) == 0:
                    print('PLCid: ' + str(plc) + ' has no abnormal batteries.')
                else:
                    for i in range(0, len(bat_to_check_set)):
                        df_the_bat = df_data[df_data['Voltage.name'].isin([bat_to_check_set[i]])]
                        df_soc_result = runEKF(df_the_bat)
                        df_soh_result = runSOH(df_soc_result)
                        df_soh_result['plc_id'] = plc
                        df_all = pd.concat([df_all, df_soh_result], axis=0, ignore_index=True)
            else:
                print('PLCid: ' + str(plc) + ' has no data.')
        
        if df_all.shape[0] == 0:
            print('All devices are running as expected.')
            try:
                mysql_add_modify.empty_sox()
                print('Cleaned the table successfully.')
            except:
                print('Failed to make the table clean.')
        else:
            try:
                mysql_add_modify.sox_calculation(df_all)
                print('Datalog of results has been outputed on mysql.')
            except:
                print('Datalog of results has been failed to be outputed on mysql.')

    def diff_sox():
        df_all = mysql_to_df('sox_calculation')
        plc_set = df_all['plc_id'].unique()
        df_diff = pd.DataFrame()
        if df_all.shape[0] == 0:
            try:
                mysql_add_modify.empty_diff_sox()
                print('Cleaned the table successfully.')
            except:
                print('Failed to make the table clean.')
        else:
            for plc in plc_set:
                plc = int(plc)
                df_data = df_all[df_all['plc_id']==plc]
                df_data = df_data.sort_values(by='time', ascending=True)
                df_data = df_data.reset_index(drop=True)
                bat_set = df_data['bat_id'].unique()
                for i in range(0, len(bat_set)):
                    thebat = bat_set[i]
                    if 'median' in thebat:
                        pass
                    else:
                        df_1b = df_data[df_data['bat_id'].isin([thebat])]
                        packid = int(thebat[:2])
                        bench_str = 'median_' + str(packid)
                        df_bench = df_data[df_data['bat_id'].isin([bench_str])]
                        df_1b = df_1b.sort_values(by='time', ascending=True)
                        df_bench = df_bench.sort_values(by='time', ascending=True)
                        df_1b_output = pd.DataFrame()
                        df_1b_output['time'] = df_1b['time'].values
                        df_1b_output['plc_id'] = plc
                        df_1b_output['bat_id'] = df_1b['bat_id'].values
                        df_1b_output['voltage'] = df_1b['voltage'].values
                        df_1b_output['soc'] = df_1b['soc'].values
                        df_1b_output['soc_bound'] = df_1b['soc_bound'].values
                        df_1b_output['soh'] = df_1b['soh'].values
                        df_1b_output['soh_bound'] = df_1b['soh_bound'].values
                        df_1b_output['voltage_bench'] = df_bench['voltage'].values
                        df_1b_output['soc_bench'] = df_bench['soc'].values
                        df_1b_output['soc_bound_bench'] = df_bench['soc_bound'].values
                        df_1b_output['soh_bench'] = df_bench['soh'].values
                        df_1b_output['soh_bound_bench'] = df_bench['soh_bound'].values
                        df_1b_output['diff_soc'] = df_1b_output['soc'] - df_1b_output['soc_bench']
                        df_1b_output['diff_soc_bound'] = 3*np.sqrt((df_1b_output['soc_bound']/3)**2 + (df_1b_output['soc_bound_bench']/3)**2)
                        df_1b_output['diff_soh'] = df_1b_output['soh'] - df_1b_output['soh_bench']
                        df_1b_output['diff_soh_bound'] = 3*np.sqrt((df_1b_output['soh_bound']/3)**2 + (df_1b_output['soh_bound_bench']/3)**2)
                        df_diff = pd.concat([df_diff, df_1b_output])
            df_diff = df_diff.sort_values(by='time', ascending=True)
            df_diff = df_diff.reset_index(drop=True)
            if df_diff.shape[0] == 0:
                print('No data to upload.')
                try:
                    mysql_add_modify.empty_diff_sox()
                    print('Cleaned the table successfully.')
                except:
                    print('Failed to make the table clean.')
            else:
                try:
                    mysql_add_modify.diff_sox(df_diff)
                    print('diff_sox uploaded.')
                except:
                    print('Failed to upload diff_sox')
    
    @staticmethod
    def final_conclusions():
        settings = importlib.import_module('settings')
        df_data = mysql_to_df('diff_sox')
        plc_set = df_data['plc_id'].unique()
        if df_data.shape[0] == 0:
            try:
                mysql_add_modify.empty_conclusions()
                print('No data in mysql.')
            except:
                print('Cleaning outdated conclusions failed.')
            pass
        else:
            df_data = df_data.sort_values(by='time', ascending=True)
            df_data = df_data.reset_index(drop=True)
            plc_set = df_data['plc_id'].unique()
            df_results = pd.DataFrame()
            ind = 0
            for plc in plc_set:
                df_1p = df_data[df_data['plc_id'].isin([plc])]
                bat_set = df_1p['bat_id'].unique()
                for thebat in bat_set:
                    if 'median' in thebat:
                        pass
                    else:
                        df_1p_1b = df_1p[df_1p['bat_id'].isin([thebat])]
                        df_1p_1b = df_1p_1b.sort_values(by='time', ascending=True)
                        num_selected = int(df_1p_1b.shape[0]*settings.ratio_for_conclusion)
                        df_1p_1b_selected = df_1p_1b.tail(num_selected)
                        median_soc = df_1p_1b_selected['diff_soc'].median()
                        median_soh = df_1p_1b_selected['diff_soh'].median()
                        if abs(median_soc) < settings.dsoc_threshold:
                            pass
                        else:
                            to_append = pd.DataFrame({
                                                    'ind': [ind],
                                                    'plc_id': [plc], 
                                                    'bat_id': [thebat], 
                                                    'dsoc': [median_soc], 
                                                    'dsoh': [median_soh],
                                                    })
                            ind += 1
                            df_results = pd.concat([df_results, to_append])
            if df_results.shape[0] > 0:
                try:
                    mysql_add_modify.final_conclusions(df_results)
                    print('The conclusions have been uploaded.')
                except:
                    print('The conclusions have been failed to be uploaded.')
            else:
                mysql_add_modify.empty_conclusions()
                print('No conclusions.')