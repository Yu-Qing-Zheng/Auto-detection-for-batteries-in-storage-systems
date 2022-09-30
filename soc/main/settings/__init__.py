"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

import os
from soc.config import config

ENV = os.environ.get('TMR_DATA_ENV', 'product')
config = config[ENV]

REDIS_HOST = config.REDIS_HOST
REDIS_PORT = config.REDIS_PORT
REDIS_DB = config.REDIS_DB

MONGO_DB_NAME = config.MONGO_DB_NAME
MONGO_HOST = config.MONGO_HOST
MONGO_PORT = config.MONGO_PORT
MONGO_USERNAME = config.MONGO_USERNAME
MONGO_PWD = config.MONGO_PWD
MONGO_AUTH_SOURCE = config.MONGO_AUTH_SOURCE
