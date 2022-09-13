from sched import scheduler
from clock.get_current_time import get_current_time
from energy.energy_trigger import energy_trigger
from apscheduler.schedulers.blocking import BlockingScheduler
from plcid.query_all_plc import query_all_plc
from settings import plc_csv_file, plc_csv_path, seconds_interval
import pandas as pd
start_time = get_current_time()[0]
def diagnose_trigger_service():
    plc_update = query_all_plc()
    df_plc = pd.read_csv(plc_csv_path+plc_csv_file)
    plc_set = df_plc['plc'].values
    for i in range(0, df_plc.shape[0]):
        plc = [int(plc_set[i])]
        print(plc)
        flag = energy_trigger(plc)
        print(get_current_time()[0], flag)
scheduler = BlockingScheduler()
scheduler.add_job(diagnose_trigger_service, 'interval', seconds = seconds_interval)
scheduler.start()