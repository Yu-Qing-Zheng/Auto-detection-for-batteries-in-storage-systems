from sqlite3 import Timestamp
import pandas as pd
import sys 
sys.path.append("..")
from mysql.mysql_add_modify import mysql_add_modify

def threshold_upload():
    df = pd.read_csv('energy_threshold.csv')
    plc_set = df['plc'].values
    df['time'] = pd.to_datetime(df['time'])
    for i in range(0, df.shape[0]):
        plc = df['plc'].values[i]
        f = df['median_max_forward'].values[i]
        r = df['median_max_reverse'].values[i]
        Timestamp = df['time'].values[i]
        mysql_add_modify.threshold(plc, f, r, Timestamp)
        print('PLCID '+str(plc)+' has been finished.')
if __name__ == '__main__':
    threshold_upload()