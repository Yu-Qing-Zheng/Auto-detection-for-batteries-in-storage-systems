from mongoengine import *
import importlib
# from utils import logger
# import traceback
# from settings import MONGO_DB_NAME, MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PWD, MONGO_AUTH_SOURCE

def mongo_connect():
    settings = importlib.import_module('settings')
    # importlib.reload(settings)
    try:
        connect(settings.MONGO_DB_NAME, host=settings.MONGO_HOST, port=settings.MONGO_PORT, username=settings.MONGO_USERNAME,
                    password=settings.MONGO_PWD, authentication_source=settings.MONGO_AUTH_SOURCE, connect=True)
        print('***connected!***')
    except:
        print('connection failed!')
    # except Exception as e:
    #         logger.error(e.args)
    #         logger.error(traceback.print_exc())