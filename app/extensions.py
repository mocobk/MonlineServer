#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : manage.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 14:27
"""
这里添加 flask 各种插件
"""

from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from app.libs.flask_sqlalchemy import SQLAlchemy, Query


flask_ma = Marshmallow()
db = SQLAlchemy(query_class=Query)
migrate = Migrate(db=db)
scheduler = APScheduler()
# 允许跨域请求 supports_credentials=True  对应前端 axios.defaults.withCredentials = true;//让ajax携带cookie
cors = CORS(supports_credentials=True)


# 传入app以注册扩展
def register_extensions(app):
    cors.init_app(app)

    db.init_app(app)

    migrate.init_app(app)

    flask_ma.init_app(app)

    scheduler.init_app(app)
