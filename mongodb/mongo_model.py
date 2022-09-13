from mongoengine import *

class Datalog(DynamicDocument):
    PLC_id = IntField(required=True)
    time = DateTimeField(required=True)
    data = DictField(required=True)
    meta = {
        'indexes': [
            ('PLC_id', 'time')
        ],
        'index_background': True,
        'auto_create_index': True,
        'collection': 'datalog'
    }

class energy_threshold_log(DynamicDocument):
    plc = IntField(required=True)
    time = DateTimeField(required=True)
    median_max_forward = FloatField(required=True)
    median_max_reverse = FloatField(required=True)
    meta = {
        'indexes': [
            ('plc', 'time')
        ],
        'index_background': True,
        'auto_create_index': True,
        'collection': 'energy_threshold'
    }

class energy_trigger_log(DynamicDocument):
    plc = IntField(required=True)
    # time = IntField(required=True, prime=True)
    time = DateTimeField(required=True)
    energy_flag = IntField(required=True)
    meta = {
        'indexes': [
            ('plc', 'time')
        ],
        'index_background': True,
        'auto_create_index': True,
        'collection': 'diagnose_trigger'
    }