"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

import redis
from mongoengine import connect

from soc.utils import logger
from soc.main.settings import *


def DBConnect():
    try:
        # MongoDB
        connect(MONGO_DB_NAME, host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USERNAME,
                password=MONGO_PWD, authentication_source=MONGO_AUTH_SOURCE, connect=False)

        # Redis
        pool = redis.ConnectionPool(host=REDIS_HOST,
                                    port=REDIS_PORT,
                                    db=REDIS_DB,
                                    decode_responses=True)
        rdc = redis.StrictRedis(connection_pool=pool)
        return rdc
    except Exception as e:
        logger.error(
            'fail to connect redis with error: {err}'.format(err=e.args))
        raise Exception(
            'fail to connect redis with error: {err}'.format(err=e.args))


rdc = DBConnect()
