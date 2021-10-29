# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 14:41
from . import api


@api.route('/index')
def index():
    return 'index page'
