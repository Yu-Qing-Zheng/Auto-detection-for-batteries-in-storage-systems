from clock.get_current_time import get_current_time
from datetime import datetime
# from settings import fmt1
import importlib

def time_count(start_time, end_time):
    settings = importlib.import_module('settings')
    # importlib.reload(settings)
    ts = datetime.strptime(start_time, settings.fmt1)
    st = datetime.strptime(end_time, settings.fmt1)
    time_delta = (st - ts).days
    return time_delta