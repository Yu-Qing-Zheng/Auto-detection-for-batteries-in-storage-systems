from data.diagnose_begin_switch import diagnose_begin_switch
from data.param_calculate import param_calculate
from draw.dopic import dopic
import datetime
import pause
import math
import importlib

def diagnose_loop():
    settings = importlib.import_module('settings')
    importlib.reload(settings)
    when_to_next = datetime.datetime.now()
    while settings.do_diagnose == 1:
        now_time_ts = datetime.datetime.now()
        print('Start a new loop:', now_time_ts)
        diagnose_flag = diagnose_begin_switch()
        if diagnose_flag == 1:
            print('It is time!')
            print('diagnose_flag:', diagnose_flag)
            try:
                print('###### waiting for calculation ######')
                print('(step 1/3) sox calculating ...')
                param_calculate.sox_upload()
                print('(step 2/3) dsox calculating ...')
                param_calculate.diff_sox()
                print('(step 3/3) conclusions calculating ...')
                param_calculate.final_conclusions()
                print('###### calculation finished ######')
                print('###### waiting for plots generation ######')
                print('(step 1/3) file cleaning ...')
                dopic.checkfile()
                print('(step 2/3) ploting dsox ...')
                dopic.dsox()
                print('(step 3/3) ploting packpic ...')
                dopic.packpic()
                print('###### ploting finished ######')
            except:
                print('error.')
            when_to_next = now_time_ts + \
                datetime.timedelta(\
                    hours=math.ceil(\
                        max(settings.diagnose_loop_interval, (datetime.datetime.now() - now_time_ts).seconds/3600)))
            print('next loop will begin at:', when_to_next)
            print('******************')
            pause.until(when_to_next)
            continue
        else:
            print('It is not time yet.')
            when_to_next = now_time_ts + datetime.timedelta(hours=settings.diagnose_loop_interval)
            print('next loop will begin at:', when_to_next)
            print('******************')
            pause.until(when_to_next)
            continue