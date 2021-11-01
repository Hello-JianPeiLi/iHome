# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 10:16
import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = 'GLSDGL12359SDLF'

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/iHome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = '172.16.126.198'
    REDIS_PORT = '9763'
    REDIS_AUTH = 'Libai.123'

    # flask_session
    # doc：https://flask-session.readthedocs.io/en/latest/
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_AUTH)
    SESSION_USE_SIGNER = True  # 对cookies中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session有效时


class DevelopmentConfig(Config):
    """开发环境"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境"""
    pass


config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}
