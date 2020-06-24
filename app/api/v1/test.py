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
    def get(self):
        hostname = socket.gethostname()
        data = {
            'hostname': socket.gethostname(),
            'ip': socket.gethostbyname(hostname),
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'now': time.time()
        }
        return Success(data=data)
