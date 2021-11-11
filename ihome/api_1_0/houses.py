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
from ihome.models import Area, House, Facility, HouseImage
from ihome import redis_store
from ihome.utils.image_storage import storage
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


# POST /api/v1.0/houses/info
@api.route('/houses/info', methods=['POST'])
@login_required
def save_house_info():
    """
    保存房屋的基本信息
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["1", "2"]
    }
    :return:
    """
    # 获取数据
    user_id = g.user_id

    house_dict = request.get_json()
    title = house_dict.get('title')  # 房屋名称
    price = house_dict.get('price')  # 房屋单价
    area_id = house_dict.get('area_id')  # 房屋所属城区的编号
    address = house_dict.get('address')  # 房屋地址
    room_count = house_dict.get('room_count')  # 房屋包含的房间数目
    acreage = house_dict.get('acreage')  # 房屋面积
    unit = house_dict.get('unit')  # 房屋布局（一房一厅）
    capacity = house_dict.get('capacity')  # 房屋容纳人数
    beds = house_dict.get('beds')  # 房屋卧床数目
    deposit = house_dict.get('deposit')  # 押金
    min_days = house_dict.get('min_days')  # 最小入住天数
    max_days = house_dict.get('max_days')  # 最大入住天数

    # 校验参数
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 判断金额是否正确
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 判断城区ID是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据异常')

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg='城区信息有误')

    # 保存房屋信息
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 设施和房屋信息保存数据库要么一起保存成功，要么一起失败，所以保存在session中，不会操作数据库，即不用捕获异常,在下面设施提交一并操作
    db.session.add(house)
    # try:
    #     db.session.add(house)
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     db.session.rollback()
    #     return jsonify(errno=RET.DBERR, errmsg='保存数据异常')

    # 处理房屋的设施信息
    facility_ids = house_dict.get('facility')

    # 如果用户勾选了设施信息，在保存数据库
    if facility_ids:
        try:
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库异常')

        if facilities:
            # 表示有合法的设施数据
            # 保存设施数据
            house.facilities = facilities
    # 统一提交，房屋信息和设施信息
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    # 保存数据成功
    return jsonify(errno=RET.OK, errmsg='OK', data={'house_id': house.id})


# POST /api/v1.0/houses/image
@api.route('/houses/image', methods=['POST'])
@login_required
def save_house_image():
    """
    保存房屋的图片
    参数 图片 房屋的id
    :return:
    """
    image_file = request.files.get('house_image')
    house_id = request.form.get('house_id')

    current_app.logger.info(image_file)
    current_app.logger.info(house_id)
    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmgs='参数错误')

    # 判断house_id 的正确性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='数据库异常')

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 将图片保存在七牛中
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='保存失败')

    # 保存图片信息到数据库中
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)

    # 处理房屋的主图片
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存图片数据异常')

    return jsonify(errno=RET.OK, errmsg='OK', data={'image_url': file_name})
