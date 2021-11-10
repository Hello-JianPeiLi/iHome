# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/10 09:21
from . import api
from flask import g, request, jsonify, current_app
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import db, constants
from ihome.utils.commons import login_required
from ihome.models import Area


# GET /api/v1.0/areas
@api.route('/areas', methods=['GET'])
def get_area_info():
    """获取城区信息"""
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    area_dict_li = []
    for area in area_li:
        area_dict_li.append(area.to_dict())
    return jsonify(errno=RET.OK, errmsg='查询成功', data=area_dict_li)
