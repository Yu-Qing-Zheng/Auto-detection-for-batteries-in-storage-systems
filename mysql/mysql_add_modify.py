# add/update data:
from mysql.mysql_model import *
import pandas as pd
import sqlalchemy
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
    
    @staticmethod
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
    def empty_Date():
        mysql_session = get_session()
        mysql_session.query(diagnosed_date).delete()
        mysql_session.commit()
        mysql_session.close()

    @staticmethod
    def results_outdated(df):
        mysql_session = get_session()
        mysql_session.query(sox_calculation).delete()
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
            add = sox_calculation(
                                   plc_id=plc, 
                                   time=time,
                                   bat_id=batid, 
                                   voltage=volt,
                                   current=curr,
                                   temperature=temp,
                                   soc=soc,
                                   soc_bound=soc_bound,
                                   soh=soh,
                                   soh_bound=soh_bound,
                                   )
            mysql_session.add(add)
            mysql_session.commit()
        mysql_session.close()

    @staticmethod
    def sox_calculation(df):
        df = df.sort_values(by='time', ascending=True)
        df = df.reset_index(drop=True)
        ind = df.index.values
        df_tosql = pd.DataFrame()
        df_tosql['ind'] = ind
        df_tosql['plc_id'] = df['plc_id']
        df_tosql['bat_id'] = df['Voltage.name']
        df_tosql['time'] = df['time']
        df_tosql['voltage'] = round(df['Voltage'], 2)
        df_tosql['current'] = round(df['Current'], 2)
        df_tosql['temperature'] = round(df['Temperature'], 2)
        df_tosql['soc'] = round(df['SOC'], 4)
        df_tosql['soc_bound'] = round(df['SOCBound'], 4)
        df_tosql['soh'] = round(df['SOH'], 4)
        df_tosql['soh_bound'] = round(df['SOHBound'], 4)
        num = df_tosql.shape[0]
        df_tosql.to_sql(
                        'sox_calculation', 
                        con=engine, 
                        schema='data_preprocessing', 
                        index=False, 
                        index_label=False, 
                        if_exists='replace', 
                        chunksize=num,
                        dtype={
                               'ind': sqlalchemy.types.Integer(),
                               'plc_id': sqlalchemy.types.Integer(),
                               'bat_id': sqlalchemy.types.VARCHAR(length=16),
                               'time': sqlalchemy.DateTime(),
                               'voltage': sqlalchemy.types.Float(),
                               'current': sqlalchemy.types.Float(),
                               'temperature': sqlalchemy.types.Float(),
                               'soc': sqlalchemy.types.Float(),
                               'soc_bound': sqlalchemy.types.Float(),
                               'soh': sqlalchemy.types.Float(),
                               'soh_bound': sqlalchemy.types.Float(),
                              }
                        )
        with engine.connect() as con:
            con.execute('ALTER TABLE `sox_calculation` ADD PRIMARY KEY (`ind`);')

    @staticmethod
    def empty_sox():
        mysql_session = get_session()
        mysql_session.query(sox_calculation).delete()
        mysql_session.commit()
        mysql_session.close()

    @staticmethod
    def diff_sox(df):
        df = df.sort_values(by='time', ascending=True)
        df = df.reset_index(drop=True)
        ind = df.index.values
        df_tosql = pd.DataFrame()
        df_tosql['ind'] = ind
        df_tosql['plc_id'] = df['plc_id']
        df_tosql['bat_id'] = df['bat_id']
        df_tosql['time'] = df['time']
        df_tosql['voltage'] = round(df['voltage'], 2)
        df_tosql['soc'] = round(df['soc'], 4)
        df_tosql['soc_bound'] = round(df['soc_bound'], 4)
        df_tosql['soh'] = round(df['soh'], 4)
        df_tosql['soh_bound'] = round(df['soh_bound'], 4)
        df_tosql['voltage_bench'] = round(df['voltage_bench'], 2)
        df_tosql['soc_bench'] = round(df['soc_bench'], 4)
        df_tosql['soc_bound_bench'] = round(df['soc_bound_bench'], 4)
        df_tosql['soh_bench'] = round(df['soh_bench'], 4)
        df_tosql['soh_bound_bench'] = round(df['soh_bound_bench'], 4)
        df_tosql['diff_soc'] = round(df['diff_soc'], 4)
        df_tosql['diff_soc_bound'] = round(df['diff_soc_bound'], 4)
        df_tosql['diff_soh'] = round(df['diff_soh'], 4)
        df_tosql['diff_soh_bound'] = round(df['diff_soh_bound'], 4)
        num = df_tosql.shape[0]
        df_tosql.to_sql(
                        'diff_sox', 
                        con=engine, 
                        schema='data_preprocessing', 
                        index=False, 
                        index_label=False, 
                        if_exists='replace', 
                        chunksize=num,
                        dtype={
                               'ind': sqlalchemy.types.Integer(),
                               'plc_id': sqlalchemy.types.Integer(),
                               'bat_id': sqlalchemy.types.VARCHAR(length=16),
                               'time': sqlalchemy.DateTime(),
                               'voltage': sqlalchemy.types.Float(),
                               'soc': sqlalchemy.types.Float(),
                               'soc_bound': sqlalchemy.types.Float(),
                               'soh': sqlalchemy.types.Float(),
                               'soh_bound': sqlalchemy.types.Float(),
                               'voltage_bench': sqlalchemy.types.Float(),
                               'soc_bench': sqlalchemy.types.Float(),
                               'soc_bound_bench': sqlalchemy.types.Float(),
                               'soh_bench': sqlalchemy.types.Float(),
                               'soh_bound_bench': sqlalchemy.types.Float(),
                               'diff_soc': sqlalchemy.types.Float(),
                               'diff_soc_bound': sqlalchemy.types.Float(),
                               'diff_soh': sqlalchemy.types.Float(),
                               'diff_soh_bound': sqlalchemy.types.Float(),
                              }
                        )
        with engine.connect() as con:
            con.execute('ALTER TABLE `diff_sox` ADD PRIMARY KEY (`ind`);')

    @staticmethod
    def empty_diff_sox():
        mysql_session = get_session()
        mysql_session.query(diff_sox).delete()
        mysql_session.commit()
        mysql_session.close()
    
    @staticmethod
    def final_conclusions(df):
        df = df.sort_values(by='plc_id', ascending=True)
        df = df.reset_index(drop=True)
        num = df.shape[0]
        df_tosql = df
        df_tosql.to_sql(
                        'final_conclusions', 
                        con=engine, 
                        schema='data_preprocessing', 
                        index=False, 
                        index_label=False, 
                        if_exists='replace', 
                        chunksize=num,
                        dtype={
                               'ind': sqlalchemy.types.Integer(),
                               'plc_id': sqlalchemy.types.Integer(),
                               'bat_id': sqlalchemy.types.VARCHAR(length=16),
                               'dsoc': sqlalchemy.types.Float(),
                               'dsoh': sqlalchemy.types.Float(),
                              }
                        )
        with engine.connect() as con:
            con.execute('ALTER TABLE `final_conclusions` ADD PRIMARY KEY (`ind`);')
    
    @staticmethod
    def empty_conclusions():
        mysql_session = get_session()
        mysql_session.query(final_conclusions).delete()
        mysql_session.commit()
        mysql_session.close()