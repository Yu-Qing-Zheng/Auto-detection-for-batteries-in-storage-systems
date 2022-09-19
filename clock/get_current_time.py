import time
# from settings import fmt1, fmt2, fmt3
import importlib

def get_current_time():
    settings = importlib.import_module('settings')
    # importlib.reload(settings)
    ts = time.time()
    timeArray = time.localtime(ts)
    strtime1 = time.strftime(settings.fmt1, timeArray)
    strtime2 = time.strftime(settings.fmt2, timeArray)
    strtime3 = time.strftime(settings.fmt3, timeArray)
    strtime = [strtime1, strtime2, strtime3]
    return strtime