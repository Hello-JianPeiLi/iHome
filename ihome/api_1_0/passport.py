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
from ihome import constants


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


# POST /api/v1.0/sessions
@api.route('/sessions', methods=['POST'])
def login():
    """
    用户登录
    参数：手机号、密码
    :return:
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')
    # 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 参数完整的校验
    # 手机号格式校验
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errsg='手机格式错误')
    # 判断错误次数是否超过限制
    # redis记录："access_nums_请求的ip": "次数"
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(erron=RET.REQERR, errmsg='错误次数过多，请稍后再试')
    # 从数据库中根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')
    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or not user.check_password(password):
        # 如果验证失败记录失败次数
        try:
            redis_store.incr('access_num_%s' % user_ip)
            redis_store.expire('access_num_%s' % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='账号或密码错误')
    # 如果验证相同成功，保存登录状态，在session中保存
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id
    # 如果验证码失败，记录错误次数，并返回信息
    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/sessions', methods=['GET'])
def check_login():
    """
    获取登录状态
    :return:
    """
    # 从session中获取用户名字
    name = session.get('name')
    # 如果session中数据name名字存在，则表示已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='true', data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')


# POST /api/v1.0/sessions
@api.route('/sessions', methods=['DELETE'])
def logout():
    """
    登出
    :return:
    """
    session.clear()
    return jsonify(erron=RET.OK, errmsg='OK')
