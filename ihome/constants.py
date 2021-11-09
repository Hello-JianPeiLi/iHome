# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/03 10:12

# 图片验证码的redis有效期
IMAGE_CODE_REDIS_EXPIRES = 60
# 图片验证码的redis有效期
SMS_CODE_REDIS_EXPIRES = 300
# 发送短信验证码冷却时间,单位：秒
SEND_SMS_CODE_INTERVAL = 60
# 登录错误次数限制
LOGIN_ERROR_MAX_TIMES = 5
# 登录错误超过次数后，限制登录时间，单位秒
LOGIN_ERROR_FORBID_TIME = 300
# 七牛对象存储域名
QINIU_URL_DOMAIN = 'http://r2am6p7w9.hn-bkt.clouddn.com/'