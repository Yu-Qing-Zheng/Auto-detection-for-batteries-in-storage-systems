"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class base_config(object):
    SECRET_KEY = 'tmrenergy'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 7200

    LOG_PATH = os.path.join(BASE_DIR, 'logs')
    LOG_PATH_INFO = os.path.join(LOG_PATH, 'log.log')

    DEPEND_INFO_PREFIX = "depend_info_"
    PLC_TEMPLATE_PREFIX = "plc_template_"

    @classmethod
    def init_app(cls, app):
        import logging
        from logging.handlers import TimedRotatingFileHandler
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(process)d %(thread)d %(threadName)s '
            '%(pathname)s %(lineno)s %(message)s')

        file_handler_info = TimedRotatingFileHandler(
            filename=cls.LOG_PATH_INFO, when="D", interval=1, backupCount=30)
        file_handler_info.suffix = "%Y-%m-%d.log"
        file_handler_info.setFormatter(formatter)
        file_handler_info.setLevel(logging.INFO)

        app.logger.addHandler(file_handler_info)


class product_config(base_config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Tmr84937686!@47.92.252.35:3307/dems_Prime_test?charset=utf8'

    MONGO_HOST = 'dds-8vb381a9f7b950b43984-pub.mongodb.zhangbei.rds.aliyuncs.com'
    MONGO_PORT = 3717
    MONGO_DB_NAME = 'dems'
    MONGO_USERNAME = 'root'
    MONGO_PWD = 'TMRenergy!'
    MONGO_AUTH_SOURCE = 'admin'

    REDIS_HOST = 'localhost'
    REDIS_PORT = '6379'
    REDIS_DB = 0


config = {
    'product': product_config(),
}
