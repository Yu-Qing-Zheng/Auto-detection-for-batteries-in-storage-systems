from clock.get_current_time import get_current_time
from datetime import datetime
from settings import fmt1

def time_count(start_time, end_time):
    ts = datetime.strptime(start_time, fmt1)
    st = datetime.strptime(end_time, fmt1)
    time_delta = (st - ts).days
    return time_delta