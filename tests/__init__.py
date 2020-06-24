#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : __init__.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/5/8 19:33
import json

from flask.testing import FlaskClient
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def gen_token(secret_key, expires_in, uid, role, _type='access'):
    s = Serializer(
        secret_key=secret_key,
        expires_in=expires_in
    )
    return s.dumps({'uid': uid, 'role': role, 'type': _type}).decode()


class CustomFlaskClient(FlaskClient):
    def open(self, *args, **kwargs):
        response = super().open(*args, **kwargs)
        if response.is_json:
            print(f'\n响应内容：\n{json.dumps(response.json, ensure_ascii=False)}')
        else:
            print(f'\n响应内容：\n{response.data.decode()}')
        return response
