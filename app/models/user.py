#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : user.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 16:08
from app.models.base import ModelBase, db, SQLAlchemyAutoSchema


class User(ModelBase):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), comment='姓名')
    username = db.Column(db.String(100), nullable=False, comment='用户名')
    _password = db.Column('password', db.String(255), nullable=False, comment='密码')
    phone = db.Column(db.String(20), comment='手机号')
    department = db.Column(db.String(255), comment='部门')
    business_line = db.Column(db.String(255), comment='业务线')
    role = db.Column(db.String(50), nullable=False, comment='用户角色: SuperAdmin Admin Member')
    avatar = db.Column(db.String(2048), comment='头像地址')

    @property
    def password(self):
        return self._password


class UserSchema(SQLAlchemyAutoSchema):
    """orm 模型序列化"""

    class Meta:
        model = User
        exclude = ("_password",)




