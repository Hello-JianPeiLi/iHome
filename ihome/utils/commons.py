# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/01 12:16
from werkzeug.routing import BaseConverter


#  定义正则转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex
