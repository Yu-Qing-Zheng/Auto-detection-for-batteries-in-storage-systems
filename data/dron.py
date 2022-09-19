import pandas as pd
import datetime
import importlib
from clock.get_current_time import get_current_time
from mongodb.mongo_connect import mongo_connect
from mongodb.query_request import query_request

def dron(plc):
    settings = importlib.import_module('settings')
    importlib.reload(settings)
    now_time = get_current_time()
    now_time_ts = datetime.datetime.strptime()
    start_time = 
    mongo_connect()
    data = query_request.datalog_query()