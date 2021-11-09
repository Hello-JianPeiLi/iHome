# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/10/29 14:41

from flask import Blueprint

# 创建蓝图对象
api = Blueprint('api_1_0', __name__)

from . import demo, verify_code, passport,profile
