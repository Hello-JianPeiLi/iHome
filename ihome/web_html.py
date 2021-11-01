# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/11/01 12:17
from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

html = Blueprint('web_html', __name__)


@html.route('/<re(r".*"):html_file_name>')
def get_html(html_file_name):
    """提供html文件"""
    # 如果html_html_file_name为'',表示访问的路径是/，请求的是主页
    if not html_file_name:
        html_file_name = 'index.html'
    if html_file_name != 'favicon.ico':
        html_file_name = 'html/' + html_file_name

    # 生成一个csrf_token
    csrf_token = csrf.generate_csrf()

    # flask提供的返回静态文件的方法
    rep = make_response(current_app.send_static_file(html_file_name))
    # 设置cookies值，不设置有效期，每次重开就生成，保证安全
    rep.set_cookie('csrf_token', csrf_token)

    return rep
