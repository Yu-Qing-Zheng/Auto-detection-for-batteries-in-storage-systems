from data.diagnose_begin_switch import diagnose_begin_switch
from mysql.mysql_model import *
from mysql.mysql_add_modify import mysql_add_modify
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
        flag = diagnose_begin_switch()
        flag = 1
        if flag == 1:
            df_plc = pd.read_csv(settings.plc_csv_path+settings.plc_csv_file)
            plc_set = df_plc['plc'].values
            plc_set = [40]
            df_all = pd.DataFrame()
            for plc in plc_set:
                plc = int(plc)
                mysql_session = get_session()
                plc_status_query = mysql_session.query(diagnose_trigger).filter(diagnose_trigger.plc_id==plc).all()
                mysql_session.close()
                if plc_status_query.energy_flag != settings.flag_for_abnormal:
                    continue
                print('plc_id:', plc)
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
        else:
            pass

    def diff_sox():
        flag = diagnose_begin_switch()
        flag = 1
        settings = importlib.import_module('settings')
        if flag == 1:
            mysql_session = get_session()
            df_plc = pd.read_csv(settings.plc_csv_path+settings.plc_csv_file)
            plc_set = df_plc['plc'].values
            plc_set = [40]
            df_diff = pd.DataFrame()
            for plc in plc_set:
                plc = int(plc)
                print('plc_id:', plc)
                data_query = mysql_session.query(sox_calculation).filter(sox_calculation.plc_id==plc).all() # .all()
                df_data = pd.DataFrame()
                if len(data_query) == 0:
                    pass
                else:
                    for i in range(0, len(data_query)):
                        data_series = {'plc_id': data_query[i].plc_id}
                        data_series.update({'time': data_query[i].time})
                        data_series.update({'voltage': data_query[i].voltage})
                        data_series.update({'current': data_query[i].current})
                        data_series.update({'temperature': data_query[i].temperature})
                        data_series.update({'soc': data_query[i].soc})
                        data_series.update({'soc_bound': data_query[i].soc_bound})
                        data_series.update({'soh': data_query[i].soh})
                        data_series.update({'soh_bound': data_query[i].soh_bound})
                        data_series.update({'bat_id': data_query[i].bat_id})
                        to_append_to_data = pd.DataFrame(data_series, index=[0])
                        df_data = pd.concat([df_data, to_append_to_data], axis=0)
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
            mysql_session.close()
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
        else:
            pass





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

