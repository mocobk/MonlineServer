# -*- coding: utf-8 -*-
# @File : views.py
# @Author : mocobk
# @Email : mailmzb@qq.com
# @Time : 2020/6/25 9:20 下午
import base64

from flask import Blueprint
from flask import g
from flask_restful import Resource
from requests import Response
from jieba import lcut

from app.api.tools.py_request import convert, Code
from app.libs.flask_restful import Api, RequestParser
from app.libs.response import Success

blueprint = Blueprint('tools', __name__)

api = Api(blueprint)


@api.resource('/convert2req')
class Convert2Request(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('request')
        args = parser.parse_args()
        return Success(data={'code': convert(args['request'])})


@api.resource('/convert2req/run')
class Convert2RequestRun(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('code')
        args = parser.parse_args()
        code = Code(args['code'])
        print_out = code.run()
        if hasattr(g, 'response') and isinstance(g.response, Response):
            content_type = g.response.headers.get('Content-Type', '')
            if content_type.startswith('image'):
                image = f'data:{content_type};base64,{base64.b64encode(g.content).decode()}'
            else:
                image = ''
            return Success({
                'headers': dict(g.response.headers),
                'text': g.response.text,
                'cookies': g.response.cookies.get_dict(),
                'status': g.response.status_code,
                'elapsed': g.response.elapsed.total_seconds(),
                'method': g.response.request.method,
                'image': image,
                'print_out': print_out
            })

        return Success({
            'print_out': print_out
        })


@api.resource('/big-bang')
class BigBang(Resource):
    def get(self):
        parser = RequestParser()
        parser.add_argument('text', location='args')
        args = parser.parse_args()
        return Success(data={'words': lcut(args['text'], cut_all=False, HMM=True, use_paddle=False)})
