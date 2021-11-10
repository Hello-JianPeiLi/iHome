# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/09 15:27

from . import api
from flask import g, request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import db, constants
from ihome.utils.commons import login_required


# POST /api/v1.0/users/avatar
@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    设置用户的头像
    参数：图片（多媒体表单格式） 用户id（g.user_id）
    :return:
    """
    user_id = g.user_id
    image_file = request.files.get('avatar')
    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='未上传图片')

    image_data = image_file.read()

    # 调用七牛上传图片
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

    # 保存文件名到数据库中
    try:
        User.query.filter_by(id=user_id).update({'avatar_url': file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片信息失败')

    # 保存成功返回
    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg='保存成功', data={'avatar_url': avatar_url})


# PUT /api/v1.0/users/name
@api.route('/users/name', methods=['PUT'])
@login_required
def change_user_name():
    """修改用户名"""
    user_id = g.user_id

    # 获取用户想要设置的用户名
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    name = req_data.get('name')
    try:
        User.query.filter_by(id=user_id).update({'name': name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='设置昵称失败')

    session['name'] = name
    return jsonify(errno=RET.OK, merrmsg='修改成功', data={'name': name})


# GET /api/v1.0/user
@api.route('/user', methods=['GET'])
@login_required
def get_user_profile():
    """获取个人信息"""
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='无效操作')

    return jsonify(errno=RET.OK, errmsg='查询成功', data=user.to_dict())


# GET /api/v1.0/users/auth
@api.route('/users/auth', methods=['GET'])
@login_required
def get_user_auth():
    """获取用户的实名认证信息"""
    user_id = g.user_id
    current_app.logger.info(user_id)
    # 在数据库中查询信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户实名信息失败')

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='无效操作')

    return jsonify(errno=RET.OK, errmsg='获取实名认证信息成功', data=user.auth_to_dict())


# PUT /api/v1.0/users/auth
@api.route('/users/auth', methods=['PATCH'])
@login_required
def set_user_auth():
    user_id = g.user_id
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    real_name = req_data.get('real_name')
    id_card = req_data.get('id_card')
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        user = User.query.filter_by(id=user_id, real_name=None, id_card=None).update(
            {'real_name': real_name, 'id_card': id_card})
        current_app.logger.info(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存实名信息失败')
    if not user:
        return jsonify(errno=RET.DATAEXIST, errmsg='已实名，请勿重复实名')

    return jsonify(errno=RET.OK, errmsg='实名认证成功')
