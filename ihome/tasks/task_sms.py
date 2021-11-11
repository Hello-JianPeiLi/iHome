# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/11 17:08
from celery import Celery
from ihome.libs.yuntongxun.ronglian_sms_sdk.SmsSDK import CCP

app = Celery('ihome', broker='redis://:Libai.123@172.16.126.198:9763/2')


@app.task
def send_sms(tid, mobile, data):
    """发送短信的异步数据"""
    ccp = CCP()
    ccp.send_template_sms(tid, mobile, data)
