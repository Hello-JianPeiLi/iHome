# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/09 14:17
# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_data, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'pVS6NiVZgz91sa5QMal9qsmzm37l_FFiqLV6R-uF'
secret_key = 'kLU33admkIlb2N4nF8tNQ4RGzNwYf1N5H9Tbn0k5'


def storage(file_data):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome-project-jp'

    # 上传后保存的文件名
    # key = 'my-python-logo.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'

    ret, info = put_data(token, None, file_data)
    if info.status_code == 200:
        return ret.get('key')
    else:
        raise Exception('上传七牛失败')


if __name__ == '__main__':
    with open('./wallhaven-rdj8jj.jpg', 'rb') as f:
        content = f.read()
        print(storage(content))
