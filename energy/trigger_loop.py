from clock.get_current_time import get_current_time
from energy.energy_trigger import energy_trigger
from plcid.query_all_plc import query_all_plc
from settings import plc_csv_file, plc_csv_path, chatrobot_switch
from messager.dingtalk_chatbot import mychatrobot
import pandas as pd
start_time = get_current_time()[0]
def trigger_loop():
    plc_update = query_all_plc()
    df_plc = pd.read_csv(plc_csv_path+plc_csv_file)
    plc_set = df_plc['plc'].values
    for i in range(0, df_plc.shape[0]):
        plc = [int(plc_set[i])]
        print(plc)
        flag = energy_trigger(plc)
        print(get_current_time()[0], flag)
    if chatrobot_switch == 1:
        mychatrobot.energy_trigger_pusher()