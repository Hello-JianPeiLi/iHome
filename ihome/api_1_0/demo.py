# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 14:41
from . import api
from ihome import db
from flask import current_app


@api.route('/index')
def index():
    current_app.logger.error('error msg')
    return 'index page'
