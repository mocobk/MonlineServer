#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : user.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 14:39
import socket
import time

from flask import Blueprint

from app.libs.flask_restful import Api
from flask_restful import Resource
from app.libs.response import Success

blueprint = Blueprint('test', __name__)

api = Api(blueprint)


@api.resource('')
class DemoTest(Resource):
    @staticmethod
    def get_host_ip():
        """
        查询本机ip地址
        :return: ip
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip

    def get(self):
        data = {
            'hostname': socket.gethostname(),
            'ip': self.get_host_ip(),
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'now': time.time()
        }
        return Success(data=data)
