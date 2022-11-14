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
        # try:
        settings = importlib.import_module('settings')
        # df_plc = pd.read_csv(settings.plc_csv_path+settings.plc_csv_file)
        # plc_set = df_plc['plc'].values
        # plc_set = [44]
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
            # print('plc_id:', plc)
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
        # except:
        #     print('error on sox_upload.')

    def diff_sox():
        # try:
        # settings = importlib.import_module('settings')
        df_all = mysql_to_df('sox_calculation')
        plc_set = df_all['plc_id'].unique()
        # mysql_session = get_session()
        # df_plc = pd.read_csv(settings.plc_csv_path+settings.plc_csv_file)
        # plc_set = df_plc['plc'].values
        df_diff = pd.DataFrame()
        for plc in plc_set:
            plc = int(plc)
            # print('plc_id:', plc)
            # data_query = mysql_session.query(sox_calculation).filter(sox_calculation.plc_id==plc).all() # .all()
            # df_data = pd.DataFrame()
            # if len(data_query) == 0:
            if df_all.shape[0] == 0:
                pass
            else:
                # for i in range(0, len(data_query)):
                #     data_series = {'plc_id': data_query[i].plc_id}
                #     data_series.update({'time': data_query[i].time})
                #     data_series.update({'voltage': data_query[i].voltage})
                #     data_series.update({'current': data_query[i].current})
                #     data_series.update({'temperature': data_query[i].temperature})
                #     data_series.update({'soc': data_query[i].soc})
                #     data_series.update({'soc_bound': data_query[i].soc_bound})
                #     data_series.update({'soh': data_query[i].soh})
                #     data_series.update({'soh_bound': data_query[i].soh_bound})
                #     data_series.update({'bat_id': data_query[i].bat_id})
                #     to_append_to_data = pd.DataFrame(data_series, index=[0])
                #     df_data = pd.concat([df_data, to_append_to_data], axis=0)
                df_data = df_all[df_all['plc_id']==plc]
                df_data = df_data.sort_values(by='time', ascending=True)
                df_data = df_data.reset_index(drop=True)
                bat_set = df_data['bat_id'].unique()
                for i in range(0, len(bat_set)):
                    thebat = bat_set[i]
                    if 'median' in thebat:
                        pass
                    else:
                        # print('bat_id:', bat_set[i])
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
        # mysql_session.close()
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
        # return df_diff
        # except:
        #     print('error on diff_sox.')
    
    @staticmethod
    def final_conclusions():
        # try:
        settings = importlib.import_module('settings')
        # mysql_session = get_session()
        # data_query = mysql_session.query(diff_sox).all()
        # mysql_session.close()
        df_data = mysql_to_df('diff_sox')
        plc_set = df_data['plc_id'].unique()
        # if len(data_query) == 0:
        if df_data.shape[0] == 0:
            mysql_add_modify.empty_conclusions()
            print('No data in mysql.')
            pass
        else:
            # df_data = pd.DataFrame()
            # for i in range(0, len(data_query)):
            #     data_series = {'time': data_query[i].time}
            #     data_series.update({'plc_id': data_query[i].plc_id})
            #     data_series.update({'bat_id': data_query[i].bat_id})
            #     data_series.update({'voltage': data_query[i].voltage})
            #     data_series.update({'soc': data_query[i].soc})
            #     data_series.update({'soc_bound': data_query[i].soc_bound})
            #     data_series.update({'soh': data_query[i].soh})
            #     data_series.update({'soh_bound': data_query[i].soh_bound})
            #     data_series.update({'voltage_bench': data_query[i].voltage_bench})
            #     data_series.update({'soc_bench': data_query[i].soc_bench})
            #     data_series.update({'soc_bound_bench': data_query[i].soc_bound_bench})
            #     data_series.update({'soh_bench': data_query[i].soh_bench})
            #     data_series.update({'soh_bound_bench': data_query[i].soh_bound_bench})
            #     data_series.update({'diff_soc': data_query[i].diff_soc})
            #     data_series.update({'diff_soc_bound': data_query[i].diff_soc_bound})
            #     data_series.update({'diff_soh': data_query[i].diff_soh})
            #     data_series.update({'diff_soh_bound': data_query[i].diff_soh_bound})
            #     to_append_to_data = pd.DataFrame(data_series, index=[0])
            #     df_data = pd.concat([df_data, to_append_to_data], axis=0)
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
            # return df_results
                    
        # except:
        #     print('error on final_conclusions.')
            # try:
            #     mysql_add_modify.final_conclusions(df_results)
            #     print('The conclusions have been uploaded.')
            # except:
            #     print('The conclusions have been failed to be uploaded.')


                    # try:
                        # mysql_add_modify.sox_diff(df_diff)
                    #     print('The results of diff_sox has been uploaded to mysql.')
                    # except:
                    #     print('The results of diff_sox has been failed to be uploaded to mysql.')
                    # else:
                    #     print('There is no abnormal batteries.')
                    #     try:
                    #         mysql_add_modify.empty_diff_sox()
                    #         print('Cleaned the table successfully.')
                    #     except:
                    #         print('Failed to make the table clean.')
                # else:
                #     print('There is no sox results in mysql.')
                #     try:
                #         mysql_add_modify.empty_diff_sox()
                #         print('Cleaned the table successfully.')
                #     except:
                #         print('Failed to make the table clean.')

