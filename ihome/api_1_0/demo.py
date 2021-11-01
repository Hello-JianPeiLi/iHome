# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 14:41
from . import api
from ihome import db, models
from flask import current_app


@api.route('/index')
def index():
    current_app.logger.error('error msg')
    current_app.logger.warning('warning msg')
    current_app.logger.info('info msg')
    current_app.logger.debug('debug msg')
    return 'index page'
