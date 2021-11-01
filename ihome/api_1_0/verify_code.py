# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/01 16:50
from . import api
from ihome.utils.captcha.captcha import captcha


# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>

@api.route('/')
def get_image_code():
    """
    获取图片验证码
    :return: 验证码图片
    """
    # 业务逻辑处理
    # 生成验证码图片
    # 名字，真是文本，图片数据
    name, text, image_data = captcha.generate_captcha()
