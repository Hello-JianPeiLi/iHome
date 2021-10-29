# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 14:41
from . import api
from ihome import db


@api.route('/index')
def index():
    return 'index page'
