#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : __init__.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 14:39

from app.api import test, tools


BLUEPRINTS = [
    (test.blueprint, '/test'),
    (tools.blueprint, '/tools'),
]
