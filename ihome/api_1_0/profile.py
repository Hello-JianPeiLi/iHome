# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/09 15:27

from . import api


@api.route('/users/avatar', methods=['POST'])
def set_user_avatar():
    """
    设置用户的头像
    :return:
    """
    pass

