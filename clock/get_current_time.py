import time
from settings import fmt1, fmt2, fmt3


def get_current_time():
    ts = time.time()
    timeArray = time.localtime(ts)
    strtime1 = time.strftime(fmt1, timeArray)
    strtime2 = time.strftime(fmt2, timeArray)
    strtime3 = time.strftime(fmt3, timeArray)
    strtime = [strtime1, strtime2, strtime3]
    return strtime