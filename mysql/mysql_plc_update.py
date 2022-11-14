from mysql.mysql_model import *
from mysql.mysql_to_df import mysql_to_df
import numpy as np

def mysql_plc_update(plc_set):
    df_thres = mysql_to_df('energy_threshold')
    df_trigg = mysql_to_df('diagnose_trigger')
    to_remove_set_thres = []
    to_remove_set_trigg = []
    for i in range(0, len(plc_set)):
        if df_thres[df_thres['plc_id']==plc_set[i]].shape[0] == 0:
            to_remove_set_thres.append(plc_set[i])
        if df_trigg[df_trigg['plc_id']==plc_set[i]].shape[0] == 0:
            to_remove_set_trigg.append(plc_set[i])
    df_thres_remain = df_thres[~df_thres['plc_id'].isin(plc_set)]
    to_remove_set_thres = np.append(to_remove_set_thres, df_thres_remain['plc_id'].unique())
    df_trigg_remain = df_trigg[~df_trigg['plc_id'].isin(plc_set)]
    to_remove_set_trigg = np.append(to_remove_set_trigg, df_trigg_remain['plc_id'].unique())
    # print(to_remove_set_thres)
    # print(to_remove_set_trigg)
    if len(to_remove_set_thres) == 0:
        pass
    else:
        mysql_session = get_session()
        for i in range(0, len(to_remove_set_thres)):
            mysql_session.query(energy_threshold).filter(energy_threshold.plc_id==to_remove_set_thres[i]).delete()
            mysql_session.commit()
        mysql_session.close()
    if len(to_remove_set_trigg) == 0:
        pass
    else:
        mysql_session = get_session()
        for i in range(0, len(to_remove_set_trigg)):
            mysql_session.query(diagnose_trigger).filter(diagnose_trigger.plc_id==to_remove_set_trigg[i]).delete()
            mysql_session.commit()
        mysql_session.close()