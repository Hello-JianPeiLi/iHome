# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/01 12:17
from flask import Blueprint, current_app

html = Blueprint('web_html', __name__)


@html.route('/<re(r".*"):html_file_name>')
def get_html(html_file_name):
    """提供html文件"""
    # 如果html_html_file_name为'',表示访问的路径是/，请求的是主页
    if not html_file_name:
        html_file_name = 'index.html'
    if html_file_name != 'favicon.ico':
        html_file_name = 'html/' + html_file_name

    # flask提供的返回静态文件的方法
    return current_app.send_static_file(html_file_name)
