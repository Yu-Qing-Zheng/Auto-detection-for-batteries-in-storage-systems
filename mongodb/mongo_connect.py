from mongoengine import *
# from utils import logger
# import traceback
from settings import MONGO_DB_NAME, MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PWD, MONGO_AUTH_SOURCE

def mongo_connect():
    try:
        connect(MONGO_DB_NAME, host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USERNAME,
                    password=MONGO_PWD, authentication_source=MONGO_AUTH_SOURCE, connect=True)
        print('***connected!***')
    except:
        print('connection failed!')
    # except Exception as e:
    #         logger.error(e.args)
    #         logger.error(traceback.print_exc())