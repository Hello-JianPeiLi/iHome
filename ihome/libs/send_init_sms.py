# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/03 15:06
from yuntongxun.ronglian_sms_sdk.SmsSDK import SmsSDK
import json


def send_message():
    sdk = SmsSDK('8aaf07087ce03b67017ce47d42090083', '5cb49b26a6994b8a9410dd40226ef0c9',
                 '8aaf07087ce03b67017ce47d439b008a')
    resp = sdk.sendMessage('1', '13620228033', ('112233', '奥斑马'))
    resp = json.loads(resp)
    if resp['statusCode'] == '000000':
        print("云通讯发送成功")
        print(resp)
        print(0)
    else:
        print(resp)
        print(-1)


if __name__ == '__main__':
    send_message()
