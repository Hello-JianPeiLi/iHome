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
from ihome import redis_store
import json


# GET /api/v1.0/areas
@api.route('/areas', methods=['GET'])
def get_area_info():
    """获取城区信息"""
    try:
        resp_json = redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 如果缓存存在则返回缓存的信息，不往下执行
        if resp_json:
            current_app.logger.info('hit area info')
            return resp_json, 200, {'Content-Type': 'application/json'}
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    area_dict_li = []
    for area in area_li:
        area_dict_li.append(area.to_dict())

    # 将数据转换成json字符串
    resp_dict = dict(errno=RET.OK, errmsg='查询成功', data=area_dict_li)
    resp_json = json.dumps(resp_dict)

    # 设置缓存
    try:
        redis_store.setex('area_info', constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {'Content-Type': 'application/json'}
