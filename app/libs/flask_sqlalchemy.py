#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : query.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 17:16
from contextlib import contextmanager

from flask_sqlalchemy import BaseQuery, SQLAlchemy as _SQLAlchemy

from app.libs.response import NotFound


class Query(BaseQuery):
    def get_or_404(self, ident, description=None):
        rv = self.get(ident)
        if not rv:
            raise NotFound(message=description)
        return rv

    def first_or_404(self, description=None):
        rv = self.first()
        if not rv:
            raise NotFound(message=description)
        return rv


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        """通过 with db.auto_commit() 管理上下文，失败自动回滚"""
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
