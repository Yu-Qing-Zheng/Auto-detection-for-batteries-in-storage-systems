from data.diagnose_switch import diagnose_switch
from mysql.mysql_add_modify import mysql_add_modify
from soc.runEKF import runEKF
from soh.runSOH import runSOH
from data.dron import dron
import pandas as pd

def param_calculate(plc):
    flag = diagnose_switch()
    flag = 1
    if flag == 1:
        df_data = dron.find_battery_to_check([plc])
        bat_to_check_set = df_data['Voltage.name'].unique()
        print(bat_to_check_set)
        if len(bat_to_check_set) == 0:
            print('PLCid: ' + str(plc) + ' has no abnormal batteries.')
            pass
        else:
            df_all = pd.DataFrame()
            for i in range(0, len(bat_to_check_set)):
                df_the_bat = df_data[df_data['Voltage.name'].isin([bat_to_check_set[i]])]
                df_soc_result = runEKF(df_the_bat)
                df_soh_result = runSOH(df_soc_result)
                df_soh_result['plc_id'] = plc
                df_all = pd.concat([df_all, df_soh_result], axis=0, ignore_index=True)
            mysql_add_modify.results(df_all)
            try:
                mysql_add_modify.results(df_all)
                print('Datalog of results has been outputed on mysql.')
            except:
                print('Datalog of results has been failed to outputed on mysql.')
