# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/01 16:50
import random
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.tasks.task_sms import send_sms


# GET /api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证码
    :return: 验证码图片
    """
    # 业务逻辑处理
    # 生成验证码图片
    # 名字，真是文本，图片数据
    name, text, image_data = captcha.generate_captcha()

    # 将验证码真实值与编号保存到redis中，设置有效期
    # redis： 字符串  列表  哈希  set
    # 使用哈希维护有效期的时候只能整体设置
    # "image_codes":{"id1":"abc", "":""} 哈希  hset("image_codes","id1", "abc") hget("image_code")

    # 单条维护记录，选用字符串
    # "image_code_编号1": "真实值"
    # "image_code_编号2": "真实值"
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        print('--------', text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='save image code id failed')

    # 返回图片
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id
@api.route('/sms_codes/<re(r"1[1-9]\d{9}"):mobile>')
def get_sms_code(mobile):
    # 获取参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')
    # 校验参数
    if not all([image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 业务逻辑处理
    # 从redis中取出真实的图片验证码
    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
        if real_image_code is not None:
            real_image_code = real_image_code.decode('utf-8')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis数据库异常')

    # 判断验证码是否过期
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码失效')

    # 删除图片验证码,防止用户使用同一个验证码使用多次
    redis_store.delete('image_code_%s' % image_code_id)

    # 图片验证码比较
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')

    # 判断手机号是否60s内有发送过短信，如果60s内有发送短信记录，则不再发送短信，反之发送
    try:
        send_flag = redis_store.get('send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 如果没报错则，在60s内发送过，即不需要在发送短信
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg='请求频繁，请稍后再试')

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user:
            # 表示手机号存在
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已存在')

    # 如果手机号不存在则发送验 证码
    sms_code = '%06d' % random.randint(0, 999999)
    # 保存真实的短信验证码
    try:
        redis_store.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 给发送验证码的手机做个记录，防止60s内多次发送验证码
        redis_store.setex('send_sms_code_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存短信失败')

    # 发送短信
    info = (sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60))

    # 如下没有使用celery异步发送短信
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms('1', mobile, info)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送异常')

    # if result == 0:
    #     return jsonify(errno=RET.OK, errmsg='发送成功')
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送失败')

    # 使用celery异步发送短信
    send_sms.delay('1', mobile, info)

    return jsonify(errno=RET.OK, errmsg='发送成功')
