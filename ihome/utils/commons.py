# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/01 12:16
from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import RET
from functools import wraps


#  定义正则转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# 定义验证登录状态装饰器
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get('user_id')
        # 如果用户时登录的，执行视图
        if user_id:
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    return wrapper
