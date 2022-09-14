from mongoengine import *
from utils import logger
import traceback
from mongodb.mongo_model import Datalog, energy_threshold_log, energy_trigger_log
from mongodb.mongo_connect import mongo_connect

class query_request:

    @staticmethod
    def datalog_query(start_time, end_time, plc, data_filter):
        try:
            mongo_connect()
            aggregate_query = [
                {
                    "$match": {
                        "$and": [{
                            "PLC_id": {
                                "$in": plc
                            }
                        }, {
                            "time": {"$gte": start_time, "$lte": end_time}
                        }]
                    }
                },
                {
                    "$sort": {"time": 1}
                },
                data_filter
            ]
            query_result = Datalog._get_collection().aggregate(aggregate_query)
            print('***data queried!***')
            return list(query_result)
        except:
            print('no datalog downloaded!')
        # except Exception as e:
        #     logger.error(e.args)
        #     logger.error(traceback.print_exc())
    
    @staticmethod
    def threshold_query(start_time, end_time, plc, data_filter):
        try:
            mongo_connect()
            aggregate_query = [
                {
                    "$match": {
                        "$and": [{
                            "plc": {
                                "$in": plc
                            }
                        }, {
                            "time": {"$gte": start_time, "$lte": end_time}
                        }]
                    }
                },
                {
                    "$sort": {"time": -1}
                },
                data_filter
            ]
            query_result = energy_threshold_log._get_collection().aggregate(aggregate_query)
            print('***threshold queried!***')
            return list(query_result)
        except:
            print('no threshold downloaded!')
        # except Exception as e:
        #     logger.error(e.args)
        #     logger.error(traceback.print_exc())

    @staticmethod
    def trigger_query(start_time, end_time, plc, data_filter):
        try:
            mongo_connect()
            aggregate_query = [
                {
                    "$match": {
                        "$and": [{
                            "plc": {
                                "$in": plc
                            }
                        }, {
                            "time": {"$gte": start_time, "$lte": end_time}
                        }]
                    }
                },
                {
                    "$sort": {"time": -1}
                },
                data_filter
            ]
            query_result = energy_trigger_log._get_collection().aggregate(aggregate_query)
            print('***trigger queried!***')
            return list(query_result)
        except:
            print('no trigger downloaded!')
        # except Exception as e:
        #     logger.error(e.args)
        #     logger.error(traceback.print_exc())