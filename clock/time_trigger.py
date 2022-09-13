from clock.get_current_time import get_current_time
from pandas import to_datetime


def time_trigger(specified_time):
    ts = get_current_time()
    time = ts[1]
    time = to_datetime(time)
    specified_time_ts = to_datetime(specified_time)
    if specified_time_ts > time:
        flag = 0
    else:
        flag = 1
    return flag