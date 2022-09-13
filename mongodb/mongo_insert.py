from mongodb.mongo_model import energy_trigger_log, energy_threshold_log
from mongodb.mongo_connect import mongo_connect
from utils import logger
import traceback

class mongo_insert:
    @staticmethod
    def energy_threshold_insert(plc, time, median_max_forward, median_max_reverse):
        threshold_log = energy_threshold_log(plc=plc,
                                             time=time,
                                             median_max_forward = median_max_forward,
                                             median_max_reverse = median_max_reverse)
        try:
            mongo_connect()
            threshold_log.save()
            print('energy_threshold uploaded!')
        except:
            print('no energy_threshold uploaded!')
        # except Exception as e:
        #     logger.error(e.args)
        #     logger.error(traceback.print_exc())
    
    @staticmethod
    def energy_trigger_insert(plc, time, energy_flag):
        trigger_log = energy_trigger_log(plc=plc,
                                         time=time,
                                         energy_flag=energy_flag)
        try:
            mongo_connect()
            trigger_log.save()
            print('energy_trigger uploaded!')
        except:
            print('no energy_trigger uploaded!')
        # except Exception as e:
        #     logger.error(e.args)
        #     logger.error(traceback.print_exc())