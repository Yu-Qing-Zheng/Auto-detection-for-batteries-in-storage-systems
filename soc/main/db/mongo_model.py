"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

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


class SOCTestlog(DynamicDocument):
    plc = IntField(required=True)
    time = DateTimeField(required=True)
    voltage = FloatField(required=True)
    current = FloatField(required=True)
    temperature = FloatField(required=True)
    predict = FloatField(required=True)
    meta = {
        'indexes': ['time'],
        'index_background': True,
        'auto_create_index': True,
        'collection': 'soctestlog'
    }
