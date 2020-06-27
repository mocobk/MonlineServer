#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : manage.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 14:27

from flask_migrate import MigrateCommand
from flask_script import Manager, Server

from app import create_app
# from app.extensions import db, scheduler

app = create_app()
# db.create_all(app=app)
# scheduler.start()

manager = Manager(app)


manager.add_command('db', MigrateCommand)
manager.add_command('runserver',
                    Server(host='0.0.0.0', port=8090, use_reloader=True, threaded=False))

if __name__ == '__main__':
    manager.run(default_command='runserver')
