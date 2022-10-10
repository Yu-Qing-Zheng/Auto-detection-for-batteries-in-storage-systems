# add/update data:
from mysql.mysql_model import *
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