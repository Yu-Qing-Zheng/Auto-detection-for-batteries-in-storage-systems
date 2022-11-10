from data.diagnose_begin_switch import diagnose_begin_switch
from data.param_calculate import param_calculate
from draw.dopic import dopic
import datetime
import pause
import math
import importlib

def diagnose_loop():
    settings = importlib.import_module('settings')
    when_to_go = datetime.datetime.now()
    while settings.do_diagnose == 1:
        now_time_ts = datetime.datetime.now()
        time_diff = round((now_time_ts - when_to_go).seconds, 4)
        print('time_diff:', time_diff)
        print('Start a new loop:', now_time_ts)
        diagnose_flag = diagnose_begin_switch()
        if diagnose_flag == 1:
            print('It is time!')
            print('diagnose_flag:', diagnose_flag)
            try:
                param_calculate.sox_upload()
                param_calculate.diff_sox()
                param_calculate.final_conclusions()
                dopic.checkfile()
                dopic.dsox()
                dopic.packpic()
            except:
                print('error.')
            when_to_next = now_time_ts + \
                datetime.timedelta(\
                    hours=math.ceil(\
                        max(settings.diagnose_loop_interval, (datetime.datetime.now() - now_time_ts).seconds/3600)))
            pause.until(when_to_next)
            continue
        else:
            print('It is not time yet.')
            when_to_next = now_time_ts + datetime.timedelta(hours=settings.diagnose_loop_interval)
            pause.until(when_to_next)
            continue