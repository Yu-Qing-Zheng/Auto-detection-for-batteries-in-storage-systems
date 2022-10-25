from data.diagnose_switch import diagnose_switch
from soc.runEKF import runEKF
from soh.runSOH import runSOH
from data.dron import dron

def diagnose(plc):
    flag = diagnose_switch()
    if flag == 1:
        df_data = dron.find_battery_to_check([plc])
        bat_to_check_set = df_data['Voltage.name'].unique()
        if len(bat_to_check_set) == 0:
            pass
        else:
            for i in range(0, len(bat_to_check_set)):
                df_the_bat = df_data[df_data['Voltage.name'].isin([bat_to_check_set[i]])]
                df_soc_result = runEKF(df_the_bat)
                df_soh_result = runSOH(df_soc_result)
                