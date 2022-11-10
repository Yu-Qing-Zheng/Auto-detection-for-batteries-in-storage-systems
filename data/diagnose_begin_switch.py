import importlib
import datetime
from mysql.mysql_model import *
from mysql.mysql_add_modify import mysql_add_modify

def diagnose_begin_switch():
    try:
        settings = importlib.import_module('settings')
        timegate = datetime.datetime.strptime(settings.specified_time, settings.fmt2)
        now_time = datetime.datetime.now()
        yesterday = now_time - datetime.timedelta(days=settings.diagnose_days_interval)
        today = now_time
        mysql_session = get_session()
        diag_date = mysql_session.query(diagnosed_date).all()
        mysql_session.close()
        if len(diag_date) == 0:
            mysql_add_modify.Date(yesterday)
            if now_time.hour >= timegate.hour:
                diagnose_switch = 1
                mysql_add_modify.Date(today)
            else:
                diagnose_switch = 0
        else:
            if len(diag_date) == 1:
                priorDate = diag_date[0].Date
                Date_diff = (now_time - priorDate).days
                if Date_diff >= settings.diagnose_days_interval and now_time.hour >= timegate.hour:
                    diagnose_switch = 1
                    mysql_add_modify.Date(now_time)
                else:
                    diagnose_switch = 0
            else:
                print('Date table error.')
                mysql_add_modify.empty_Date()
                mysql_add_modify.Date(yesterday)
                if now_time.hour >= timegate.hour:
                    diagnose_switch = 1
                    mysql_add_modify.Date(today)
                else:
                    diagnose_switch = 0
                # if now_time.hour >= timegate.hour:
                #     diagnose_switch = 1
                # else:
                #     diagnose_switch = 0
    except:
        print('no diagnose_switch calculated.')
        diagnose_switch = 0
    return diagnose_switch



    