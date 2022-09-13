import datetime
from datetime import date
from mongoengine import *


class DataLog(DynamicDocument):
    PLC_id = IntField(required=True)
    time = DateTimeField(required=True)
    data = DictField(required=True)
    save_money = FloatField()
    record = DictField()
    meta = {
        'indexes': [
            ('PLC_id', 'time'),
            ('time', 'PLC_id'),
            [('time', -1), ('PLC_id', 1), ('data.反向总有功电能', 1), ('data.反向总有功电能2', 1)]
        ],
        'index_background': True,
        'auto_create_index': True,
        'collection': 'datalog'
    }


MONGO_HOST = [
    "dds-8vb381a9f7b950b41137-pub.mongodb.zhangbei.rds.aliyuncs.com",
    "dds-8vb381a9f7b950b42142-pub.mongodb.zhangbei.rds.aliyuncs.com",
    "dds-8vb381a9f7b950b43984-pub.mongodb.zhangbei.rds.aliyuncs.com"
]
MONGO_DB_NAME = 'dems'
MONGO_USERNAME = 'root'
MONGO_PORT = 3717
MONGO_PWD = 'TMRenergy!'
MONGO_AUTH_SOURCE = 'admin'


connect(MONGO_DB_NAME, host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USERNAME,
        password=MONGO_PWD, authentication_source=MONGO_AUTH_SOURCE)


query_result = list(DataLog.objects().aggregate(
    *[
        {
            "$match": {
                "PLC_id": {
                    "$in": [53, 54]
                },
                "time": {
                    "$gte": datetime.datetime.combine(date.today(), datetime.time())
                }
            }
        },
        {
            "$project": {
                "PLC_id": 1,
                "time": 1,
                "forward": {
                    "$add": [
                        {
                            "$multiply": ["$data.正向有功总电能",
                                          655.35]
                        },
                        {
                            "$divide": ["$data.正向有功总电能2",
                                        100]
                        }
                    ]
                },
                "reverse": {
                    "$add": [
                        {
                            "$multiply": ["$data.反向总有功电能",
                                          655.35]
                        },
                        {
                            "$divide": ["$data.反向总有功电能2",
                                        100]
                        }
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "plc_id": "$PLC_id",
                    "time": {
                        "$dateToString": {
                            "date": "$time",
                            "format": "%Y-%m-%d %H:00:00",
                        },
                    }
                },
                "forward_energy": {
                    "$min": "$forward"
                },
                "reverse_energy": {
                    "$min": "$reverse"
                }
            }
        },
        {
            "$match": {
                "_id.time": {
                    "$in": [f'{date.today()} 00:00:00',
                            f'{date.today()} 08:00:00',
                            f'{date.today()} 11:00:00',
                            f'{date.today()} 14:00:00',
                            f'{date.today()} 17:00:00']
                }
            }
        },
        {
            "$sort":
                {
                    '_id.plc_id': 1,
                    "_id.time": 1
                }
        }
    ]
))

for q in query_result:
    print(q["_id"]["plc_id"], round(q["forward_energy"], 2), round(q["reverse_energy"], 2))

pre_f = 0
pre_r = 0
for i, q in enumerate(query_result):
    if i < 5:
        if i % 2:
            print(f"id: {q['_id']['plc_id']}, 正向: {round(q['forward_energy'] - pre_f, 2)}")
        if i and not (i % 2):
            print(f"id: {q['_id']['plc_id']}, 反向: {round(q['reverse_energy'] - pre_r, 2)}")
    elif i > 5:
        if not (i % 2):
            print(f"id: {q['_id']['plc_id']}, 正向: {round(q['forward_energy'] - pre_f, 2)}")
        if i and (i % 2):
            print(f"id: {q['_id']['plc_id']}, 反向: {round(q['reverse_energy'] - pre_r, 2)}")

    pre_f = q['forward_energy']
    pre_r = q['reverse_energy']



