# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 11:13

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_map
from flask_wtf import CSRFProtect
from flask_session import Session
from logging.handlers import RotatingFileHandler
import redis
import logging
from pymysql import install_as_MySQLdb
from ihome.utils.commons import ReConverter
from . import web_html

install_as_MySQLdb()

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
    # CSRFProtect(app)

    # 设置日志等级
    logging.basicConfig(level=logging.INFO)  # 调式debug等级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象(flask app使用的)添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

    # 为flak添加自定义的转换器
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')
    # 注册提供静态文件的蓝图
    app.register_blueprint(web_html.html)

    return app
