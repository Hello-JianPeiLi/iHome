# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/05 10:35
import logging
import re

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError


# POST /api/v1.0/users
@api.route('/users', methods=["POST"])
def register():
    """
    注册
    请求参数：手机号、短信验证码、密码
    :return:
    """
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    print(mobile)
    print(sms_code)
    print(password2)
    print(password)
    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 判断手机号格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不一致')

    # 从redis中取出短信验证码
    # real_sms_code = None
    try:
        real_sms_code = redis_store.get('sms_code_%s' % mobile)
        if real_sms_code:
            real_sms_code = real_sms_code.decode('utf-8')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='读取真实短信验证码异常')

    # 判断验证码是否过期
    if real_sms_code is None:
        return jsonify(error=RET.NODATA, errmsg='短信验证码失效')

    # 删除短信验证码，只能使用一次，不管用户校验对错
    try:
        redis_store.delete('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户填写验证码的准确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    # 判断手机号是否注册过
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    else:
        if user:
            # 表示手机号已存在
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已存在')
    # 保存用户的注册数据到数据库中
    user = User(name=mobile, mobile=mobile)
    user.password = password  # 设置密码属性
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rrollback()
        # 表示手机号出现了重复，无法注册，手机号唯一
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已存在')
    except Exception as e:
        db.session.rrollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')

    # 保存登录状态到session中
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='注册成功')
