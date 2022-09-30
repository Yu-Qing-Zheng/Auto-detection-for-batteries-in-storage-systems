"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

import os
import datetime
import traceback
from datetime import timedelta
from utils import logger

from soc.main.db.mysql_model import *
from soc.main.db.mongo_model import Datalog as DataLog, SOCTestlog as SOClog


class CollectDao:
    @staticmethod
    def query_all_plc():
        today = datetime.datetime.now().day
        if os.path.exists('./logs/last_update.txt'):
            last_update = open('./logs/last_update.txt', 'r')
            if last_update.readline() == str(today):
                read_plc_list = open('./logs/plc_list.txt', 'r')
                plc_list = read_plc_list.readline()
                plc_list = plc_list.lstrip('[').rstrip(']').replace(' ', '').split(',')
                return plc_list
        else:
            last_update = open('./logs/last_update.txt', 'w')
            last_update.write(str(today))

        mysql_session = get_session()
        query_result = mysql_session.query(Plc.plc_id).filter(Plc.device_id.isnot(None)).all()
        if not query_result:
            return []
        query_result = list(list(zip(*query_result))[0])
        mysql_session.close()

        if os.path.exists('./logs/plc_list.txt'):
            plc_list = open('./logs/plc_list.txt', 'w')
            plc_list.seek(0)
            plc_list.truncate()
            plc_list.write(str(query_result))
        else:
            plc_list = open('./logs/plc_list.txt', 'w')
            plc_list.write(str(query_result))

        return query_result

    @staticmethod
    def get_raw_parameter(start_time, end_time, plc):
        try:
            aggregate_query = [{
                "$match": {
                    "$and": [{
                        "PLC_id": {
                            "$in": plc
                        }
                    }, {
                        "time": {"$gte": start_time, "$lte": end_time}
                    }]
                }},
                # 取最新一条数据
                {"$sort": {"time": -1}},
                {
                    "$project": {
                        "_id": 0,
                        "PLC_id": 1,
                        "time": 1,
                        "data": {
                            "PCS电池电流": 1,
                            "正向有功总电能": 1,
                            "正向有功总电能2": 1,
                            "反向总有功电能": 1,
                            "反向总有功电能2": 1,
                            "1组1号电池电压": 1,
                            "1组2号电池电压": 1,
                            "1组3号电池电压": 1,
                            "1组4号电池电压": 1,
                            "1组5号电池电压": 1,
                            "1组6号电池电压": 1,
                            "1组7号电池电压": 1,
                            "1组8号电池电压": 1,
                            "1组9号电池电压": 1,
                            "1组10号电池电压": 1,
                            "1组11号电池电压": 1,
                            "1组12号电池电压": 1,
                            "1组13号电池电压": 1,
                            "1组14号电池电压": 1,
                            "1组15号电池电压": 1,
                            "1组16号电池电压": 1,
                            "1组17号电池电压": 1,
                            "1组18号电池电压": 1,
                            "1组19号电池电压": 1,
                            "1组20号电池电压": 1,
                            "1组21号电池电压": 1,
                            "1组22号电池电压": 1,
                            "1组23号电池电压": 1,
                            "1组24号电池电压": 1,
                            "1组电池温度1": 1,
                            "1组电池温度2": 1,
                            "2组1号电池电压": 1,
                            "2组2号电池电压": 1,
                            "2组3号电池电压": 1,
                            "2组4号电池电压": 1,
                            "2组5号电池电压": 1,
                            "2组6号电池电压": 1,
                            "2组7号电池电压": 1,
                            "2组8号电池电压": 1,
                            "2组9号电池电压": 1,
                            "2组10号电池电压": 1,
                            "2组11号电池电压": 1,
                            "2组12号电池电压": 1,
                            "2组13号电池电压": 1,
                            "2组14号电池电压": 1,
                            "2组15号电池电压": 1,
                            "2组16号电池电压": 1,
                            "2组17号电池电压": 1,
                            "2组18号电池电压": 1,
                            "2组19号电池电压": 1,
                            "2组20号电池电压": 1,
                            "2组21号电池电压": 1,
                            "2组22号电池电压": 1,
                            "2组23号电池电压": 1,
                            "2组24号电池电压": 1,
                            "2组电池温度1": 1,
                            "2组电池温度2": 1,
                            "3组1号电池电压": 1,
                            "3组2号电池电压": 1,
                            "3组3号电池电压": 1,
                            "3组4号电池电压": 1,
                            "3组5号电池电压": 1,
                            "3组6号电池电压": 1,
                            "3组7号电池电压": 1,
                            "3组8号电池电压": 1,
                            "3组9号电池电压": 1,
                            "3组10号电池电压": 1,
                            "3组11号电池电压": 1,
                            "3组12号电池电压": 1,
                            "3组13号电池电压": 1,
                            "3组14号电池电压": 1,
                            "3组15号电池电压": 1,
                            "3组16号电池电压": 1,
                            "3组17号电池电压": 1,
                            "3组18号电池电压": 1,
                            "3组19号电池电压": 1,
                            "3组20号电池电压": 1,
                            "3组21号电池电压": 1,
                            "3组22号电池电压": 1,
                            "3组23号电池电压": 1,
                            "3组24号电池电压": 1,
                            "3组电池温度1": 1,
                            "3组电池温度2": 1,
                            "4组1号电池电压": 1,
                            "4组2号电池电压": 1,
                            "4组3号电池电压": 1,
                            "4组4号电池电压": 1,
                            "4组5号电池电压": 1,
                            "4组6号电池电压": 1,
                            "4组7号电池电压": 1,
                            "4组8号电池电压": 1,
                            "4组9号电池电压": 1,
                            "4组10号电池电压": 1,
                            "4组11号电池电压": 1,
                            "4组12号电池电压": 1,
                            "4组13号电池电压": 1,
                            "4组14号电池电压": 1,
                            "4组15号电池电压": 1,
                            "4组16号电池电压": 1,
                            "4组17号电池电压": 1,
                            "4组18号电池电压": 1,
                            "4组19号电池电压": 1,
                            "4组20号电池电压": 1,
                            "4组21号电池电压": 1,
                            "4组22号电池电压": 1,
                            "4组23号电池电压": 1,
                            "4组24号电池电压": 1,
                            "4组电池温度1": 1,
                            "4组电池温度2": 1,
                            "5组1号电池电压": 1,
                            "5组2号电池电压": 1,
                            "5组3号电池电压": 1,
                            "5组4号电池电压": 1,
                            "5组5号电池电压": 1,
                            "5组6号电池电压": 1,
                            "5组7号电池电压": 1,
                            "5组8号电池电压": 1,
                            "5组9号电池电压": 1,
                            "5组10号电池电压": 1,
                            "5组11号电池电压": 1,
                            "5组12号电池电压": 1,
                            "5组13号电池电压": 1,
                            "5组14号电池电压": 1,
                            "5组15号电池电压": 1,
                            "5组16号电池电压": 1,
                            "5组17号电池电压": 1,
                            "5组18号电池电压": 1,
                            "5组19号电池电压": 1,
                            "5组20号电池电压": 1,
                            "5组21号电池电压": 1,
                            "5组22号电池电压": 1,
                            "5组23号电池电压": 1,
                            "5组24号电池电压": 1,
                            "5组电池温度1": 1,
                            "5组电池温度2": 1,
                            "6组1号电池电压": 1,
                            "6组2号电池电压": 1,
                            "6组3号电池电压": 1,
                            "6组4号电池电压": 1,
                            "6组5号电池电压": 1,
                            "6组6号电池电压": 1,
                            "6组7号电池电压": 1,
                            "6组8号电池电压": 1,
                            "6组9号电池电压": 1,
                            "6组10号电池电压": 1,
                            "6组11号电池电压": 1,
                            "6组12号电池电压": 1,
                            "6组13号电池电压": 1,
                            "6组14号电池电压": 1,
                            "6组15号电池电压": 1,
                            "6组16号电池电压": 1,
                            "6组17号电池电压": 1,
                            "6组18号电池电压": 1,
                            "6组19号电池电压": 1,
                            "6组20号电池电压": 1,
                            "6组21号电池电压": 1,
                            "6组22号电池电压": 1,
                            "6组23号电池电压": 1,
                            "6组24号电池电压": 1,
                            "6组电池温度1": 1,
                            "6组电池温度2": 1,
                            "7组1号电池电压": 1,
                            "7组2号电池电压": 1,
                            "7组3号电池电压": 1,
                            "7组4号电池电压": 1,
                            "7组5号电池电压": 1,
                            "7组6号电池电压": 1,
                            "7组7号电池电压": 1,
                            "7组8号电池电压": 1,
                            "7组9号电池电压": 1,
                            "7组10号电池电压": 1,
                            "7组11号电池电压": 1,
                            "7组12号电池电压": 1,
                            "7组13号电池电压": 1,
                            "7组14号电池电压": 1,
                            "7组15号电池电压": 1,
                            "7组16号电池电压": 1,
                            "7组17号电池电压": 1,
                            "7组18号电池电压": 1,
                            "7组19号电池电压": 1,
                            "7组20号电池电压": 1,
                            "7组21号电池电压": 1,
                            "7组22号电池电压": 1,
                            "7组23号电池电压": 1,
                            "7组24号电池电压": 1,
                            "7组电池温度1": 1,
                            "7组电池温度2": 1,
                            "8组1号电池电压": 1,
                            "8组2号电池电压": 1,
                            "8组3号电池电压": 1,
                            "8组4号电池电压": 1,
                            "8组5号电池电压": 1,
                            "8组6号电池电压": 1,
                            "8组7号电池电压": 1,
                            "8组8号电池电压": 1,
                            "8组9号电池电压": 1,
                            "8组10号电池电压": 1,
                            "8组11号电池电压": 1,
                            "8组12号电池电压": 1,
                            "8组13号电池电压": 1,
                            "8组14号电池电压": 1,
                            "8组15号电池电压": 1,
                            "8组16号电池电压": 1,
                            "8组17号电池电压": 1,
                            "8组18号电池电压": 1,
                            "8组19号电池电压": 1,
                            "8组20号电池电压": 1,
                            "8组21号电池电压": 1,
                            "8组22号电池电压": 1,
                            "8组23号电池电压": 1,
                            "8组24号电池电压": 1,
                            "8组电池温度1": 1,
                            "8组电池温度2": 1,
                            "9组1号电池电压": 1,
                            "9组2号电池电压": 1,
                            "9组3号电池电压": 1,
                            "9组4号电池电压": 1,
                            "9组5号电池电压": 1,
                            "9组6号电池电压": 1,
                            "9组7号电池电压": 1,
                            "9组8号电池电压": 1,
                            "9组9号电池电压": 1,
                            "9组10号电池电压": 1,
                            "9组11号电池电压": 1,
                            "9组12号电池电压": 1,
                            "9组13号电池电压": 1,
                            "9组14号电池电压": 1,
                            "9组15号电池电压": 1,
                            "9组16号电池电压": 1,
                            "9组17号电池电压": 1,
                            "9组18号电池电压": 1,
                            "9组19号电池电压": 1,
                            "9组20号电池电压": 1,
                            "9组21号电池电压": 1,
                            "9组22号电池电压": 1,
                            "9组23号电池电压": 1,
                            "9组24号电池电压": 1,
                            "9组电池温度1": 1,
                            "9组电池温度2": 1,
                            "10组1号电池电压": 1,
                            "10组2号电池电压": 1,
                            "10组3号电池电压": 1,
                            "10组4号电池电压": 1,
                            "10组5号电池电压": 1,
                            "10组6号电池电压": 1,
                            "10组7号电池电压": 1,
                            "10组8号电池电压": 1,
                            "10组9号电池电压": 1,
                            "10组10号电池电压": 1,
                            "10组11号电池电压": 1,
                            "10组12号电池电压": 1,
                            "10组13号电池电压": 1,
                            "10组14号电池电压": 1,
                            "10组15号电池电压": 1,
                            "10组16号电池电压": 1,
                            "10组17号电池电压": 1,
                            "10组18号电池电压": 1,
                            "10组19号电池电压": 1,
                            "10组20号电池电压": 1,
                            "10组21号电池电压": 1,
                            "10组22号电池电压": 1,
                            "10组23号电池电压": 1,
                            "10组24号电池电压": 1,
                            "10组电池温度1": 1,
                            "10组电池温度2": 1,
                        },
                        "record": {
                            "info": {
                                "快速充电中": 1,
                                "放电中": 1,
                                "充电完成": 1,
                                "放电完成": 1,
                            }
                        },
                    }
                }
            ]
            query_result = DataLog._get_collection().aggregate(aggregate_query)

            return list(query_result)
        except Exception as e:
            logger.error(e.args)
            logger.error(traceback.print_exc())
            return []


class InsertDao:
    @staticmethod
    def insert_soc(plc, time, voltage, current, temperature, predict):
        soclog = SOClog(plc=plc,
                        time=time,
                        voltage=voltage,
                        current=current,
                        temperature=temperature,
                        predict=predict)
        try:
            soclog.save()
        except Exception as e:
            logger.error(e)
            logger.error(traceback.print_exc())


class WhSocDao:
    def __init__(self, plc_list):
        self.plc_list = plc_list

    def get_total_energy(self):
        query_result = DataLog.objects().aggregate(
            [
                {
                    "$match": {
                        "PLC_id": {
                            "$in": self.plc_list
                        },
                    }
                },
                {
                    "$sort": {
                        "time": -1,
                    }
                },
                {
                    "$limit": len(self.plc_list) * 2,
                },
                {
                    "$project": {
                        "PLC_id": 1,
                        "time": 1,
                        "forward_energy": {
                            "$add": [
                                {
                                    "$multiply": [f"$data.正向有功总电能",
                                                  655.35]
                                },
                                {
                                    "$divide": [f"$data.正向有功总电能2",
                                                100]
                                }
                            ]
                        },
                        "reverse_energy": {
                            "$add": [
                                {
                                    "$multiply": [
                                        f"$data.反向总有功电能",
                                        655.35]
                                },
                                {
                                    "$divide": [f"$data.反向总有功电能2",
                                                100]
                                }
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "time": {
                                "$dateToString": {
                                    "date": "$time",
                                    "format": "%Y-%m-%d 00:00:00",
                                },
                            },
                            "plc_id": "$PLC_id",
                            "record": "$record"
                        },
                        "forward_energy": {
                            "$max": "$forward_energy"
                        },
                        "reverse_energy": {
                            "$max": "$reverse_energy"
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "time": "$_id.time",
                            "record": "$_id.record"
                        },
                        "forward_energy": {
                            "$sum": "$forward_energy"
                        },
                        "reverse_energy": {
                            "$sum": "$reverse_energy"
                        }
                    }
                }
            ]
        )
        return list(query_result)

    def get_point_info(self):
        point_info = DataLog.objects().aggregate(
            [
                {
                    "$match": {
                        "PLC_id": {
                            "$in": self.plc_list
                        },
                        "time": {
                            "$gte": datetime.datetime.now() - timedelta(days=2)
                        },
                        "$or": [
                            {
                                "record.info.充电完成": "1"
                            },
                            {
                                "record.info.快速充电中": "1"
                            },
                            {
                                "record.info.放电完成": "1"
                            },
                            {
                                "record.info.放电中": "1"
                            },
                        ]
                    }
                },
                {
                    "$project": {
                        "PLC_id": 1,
                        "time": 1,
                        "record.info.充电完成": 1,
                        "record.info.快速充电中": 1,
                        "record.info.放电完成": 1,
                        "record.info.放电中": 1,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "plc_id": "$PLC_id",
                            "charging_finish": "$record.info.充电完成",
                            "charging": "$record.info.快速充电中",
                            "discharging_finish": "$record.info.放电完成",
                            "discharging": "$record.info.放电中"
                        },
                        "time": {
                            "$max": "$time"
                        }
                    }
                },
                {
                    "$sort": {
                        "time": 1
                    }
                }
            ]
        )
        return list(point_info)

    @staticmethod
    def get_first_peak_end_time(plc_id):
        query_result = get_session().query(PricePolicy.end_time).join(
            Transformer, PricePolicy.project_id == Transformer.project_id
        ).join(
            Plc, Plc.transformer_id == Transformer.transformer_id
        ).filter(
            Plc.plc_id == plc_id, PricePolicy.time_type == 2
        ).first()
        return query_result

    def get_capacity(self):
        # 清理重复数据的
        aaa = DataLog.objects().aggregate(
            [
                {
                    "$match": {
                        "PLC_id": {
                            "$in": self.plc_list
                        },
                        "time": {
                            "$gte": datetime.datetime.now() - timedelta(days=7)
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "PLC_id": "$PLC_id",
                            "time": "$time"
                        },
                        "dups": {
                            "$first": "$_id"
                        },
                        "count": {
                            "$sum": 1
                        }
                    }
                },
                {
                    "$match": {
                        "count": {
                            "$gt": 1
                        }
                    }
                }
            ],
            allowDiskUse=True
        )

        for item in list(aaa):
            DataLog.objects(_id=item["dups"]).delete()

        query_result = DataLog.objects().aggregate(
            [
                {
                    "$match": {
                        "PLC_id": {
                            "$in": self.plc_list
                        },
                        "time": {
                            "$gte": datetime.datetime.now() - timedelta(days=7)
                        }
                    }
                },
                {
                    "$project": {
                        "PLC_id": 1,
                        "time": 1,
                        "minute": {
                            "$minute": "$time"
                        },
                        "data.正向有功总电能": 1,
                        "data.正向有功总电能2": 1,
                        "data.反向总有功电能": 1,
                        "data.反向总有功电能2": 1
                    }
                },
                {
                    "$match": {
                        "minute": 8
                    }
                },
                {
                    "$project": {
                        "PLC_id": 1,
                        "time": 1,
                        "forward_energy": {
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
                        "reverse_energy": {
                            "$add": [
                                {
                                    "$multiply": [
                                        "$data.反向总有功电能",
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
                            "time": {
                                "$dateToString": {
                                    "date": "$time",
                                    "format": "%Y-%m-%d %H:00:00",
                                },
                            }
                        },
                        "forward_energy": {
                            "$sum": "$forward_energy"
                        },
                        "reverse_energy": {
                            "$sum": "$reverse_energy"
                        }
                    }
                },
                {
                    "$sort": {"_id.time": 1}
                }
            ]
        )
        return list(query_result)
