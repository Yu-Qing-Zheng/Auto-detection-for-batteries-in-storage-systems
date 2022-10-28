# add/update data:
from mysql.mysql_model import *
import pandas as pd
# from settings import threshold_database, trigger_database

class mysql_add_modify():

    @staticmethod
    def threshold(plc, f, r, t):
        mysql_session = get_session()
        plc = int(plc)
        query = mysql_session.query(energy_threshold).filter(energy_threshold.plc_id==plc).all()
        if len(query) == 1:
            mysql_session.query(energy_threshold).\
                filter(energy_threshold.plc_id==plc).\
                    update({'time':t, # to_datetime(datetime.datetime.now()), 
                            'median_max_forward':f, 
                            'median_max_reverse':r, 
                            })
            mysql_session.commit()
            mysql_session.close()
        else:
            if len(query) < 1:
                add = energy_threshold(plc_id=plc, \
                                         time=t, \
                                         median_max_forward=f, \
                                         median_max_reverse=r)
                mysql_session.add(add)
                mysql_session.commit()
                mysql_session.close()
            else:
                print('PLC_ID ' + str(plc) + ' has more than one segment of data.')
                mysql_session.close()
    
    @staticmethod
    def trigger(plc, trigger, t):
        mysql_session = get_session()
        plc = int(plc)
        query = mysql_session.query(diagnose_trigger).filter(diagnose_trigger.plc_id==plc).all()
        if len(query) == 1:
            mysql_session.query(diagnose_trigger).\
                filter(diagnose_trigger.plc_id==plc).\
                    update({'time':t, 
                            'energy_flag':trigger, 
                            })
            mysql_session.commit()
            mysql_session.close()
        else:
            if len(query) < 1:
                add = diagnose_trigger(plc_id=plc, \
                                         time=t, \
                                         energy_flag=trigger)
                mysql_session.add(add)
                mysql_session.commit()
                mysql_session.close()
            else:
                print('PLC_ID ' + str(plc) + ' has more than one segment of data.')
    
    def Date(t):
        mysql_session = get_session()
        query = mysql_session.query(diagnosed_date).all()
        if len(query) == 1:
            mysql_session.query(diagnosed_date).update({'Date':t})
            mysql_session.commit()
            mysql_session.close()
        else:
            if len(query) < 1:
                add = diagnosed_date(Date=t)
                mysql_session.add(add)
                mysql_session.commit()
                mysql_session.close()
            else:
                print('It has more than one segment of data.')

    @staticmethod
    def results_outdated(df):
        mysql_session = get_session()
        mysql_session.query(diagnose_results).delete()
        plc = list(df['plc_id'].values)
        time = list(df['time'].values)
        batid = list(df['Voltage.name'].values)
        volt = list(df['Voltage'].values)
        curr = list(df['Current'].values)
        temp = list(df['Temperature'].values)
        soc = list(df['SOC'].values)
        soc_bound = list(df['SOCBound'].values)
        soh = list(df['SOH'].values)
        soh_bound = list(df['SOHBound'].values)
        # add = diagnose_results(
        #                        plc_id=plc, 
        #                        time=time,
        #                        bat_id = batid, 
        #                        voltage = volt,
        #                        current = curr,
        #                        temperature = temp,
        #                        soc = soc,
        #                        soc_bound = soc_bound,
        #                        soh = soh,
        #                        soh_bound = soh_bound,
        #                        )
        # mysql_session.add(add)
        # mysql_session.commit()
        # mysql_session.close()
        for i in range(0, df.shape[0]):
            plc = df['plc_id'].values[i]
            time = df['time'].values[i]
            batid = df['Voltage.name'].values[i]
            volt = df['Voltage'].values[i]
            curr = df['Current'].values[i]
            temp = df['Temperature'].values[i]
            soc = df['SOC'].values[i]
            soc_bound = df['SOCBound'].values[i]
            soh = df['SOH'].values[i]
            soh_bound = df['SOHBound'].values[i]
            add = diagnose_results(
                                   plc_id=plc, 
                                   time=time,
                                   bat_id = batid, 
                                   voltage = volt,
                                   current = curr,
                                   temperature = temp,
                                   soc = soc,
                                   soc_bound = soc_bound,
                                   soh = soh,
                                   soh_bound = soh_bound,
                                   )
            mysql_session.add(add)
            mysql_session.commit()
        mysql_session.close()

    @staticmethod
    def results(df):
        df_tosql = pd.DataFrame()
        df_tosql['plc_id'] = df['plc_id']
        df_tosql['time'] = df['time']
        df_tosql['voltage'] = round(df['Voltage'], 2)
        df_tosql['current'] = round(df['Current'], 2)
        df_tosql['temperature'] = round(df['Temperature'], 2)
        df_tosql['soc'] = round(df['SOC'], 4)
        df_tosql['soc_bound'] = round(df['SOCBound'], 4)
        df_tosql['soh'] = round(df['SOH'], 4)
        df_tosql['soh_bound'] = round(df['SOHBound'], 4)
        df_tosql['bat_id'] = df['Voltage.name']
        df_tosql.to_sql(
                        'diagnose_results', 
                        con=engine, 
                        schema='data_preprocessing', 
                        index=False, 
                        index_label=False, 
                        if_exists='replace', 
                        chunksize=10000,
                        )