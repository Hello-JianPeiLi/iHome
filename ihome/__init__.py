# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 11:13

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_map
from flask_wtf import CSRFProtect
from flask_session import Session
import redis

# 数据库
db = SQLAlchemy()

# redis连接对象
redis_store = None


# 工厂模式
def create_app(config_name):
    """
    创建flask应用对象(工厂模式)
    :param config_name: str 配置模式的名字('develop', 'product')
    :return:
    """
    app = Flask(__name__)
    # 根据配置模式的名字获取配置参数的类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)
    db.init_app(app)
    # redis
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT,
                                    password=config_class.REDIS_AUTH)

    # 利用flask-session将session数据保存在redis中
    Session(app)

    # 为flask补充csrf防护
    CSRFProtect(app)

    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')

    return app
