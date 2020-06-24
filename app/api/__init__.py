#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : __init__.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 14:39

from app.api.v1 import test


BLUEPRINTS = [
    (test.blueprint, '/test'),
]
