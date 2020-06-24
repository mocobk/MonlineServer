#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : SqlUtils.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2019/9/4 11:13
"""
用来调试 orm 对象的建表 sql 语句 与 查询 sql 语句
"""
from sqlalchemy import create_engine
from config import CONFIG
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable, CreateIndex
from app.extensions import db

ENGINE = create_engine(CONFIG.get('development').SQLALCHEMY_DATABASE_URI)


def _session():
    """
    query = session.query(CasesDoc).filter_by(id=1)
    print(query.statement)
    :return: session object
    """
    return sessionmaker(bind=ENGINE)()


session = _session()


def create_sql(model: db.Model):
    """
    from app.utils.SqlEcho import create_sql
    print(create_sql(WorkLink))
    :return: str
    """
    create_table_sql = str(CreateTable(model.__table__).compile(ENGINE))
    create_index_sql = [str(CreateIndex(index).compile(ENGINE)) for index in model.__table__.indexes]
    return '\n'.join([create_table_sql] + create_index_sql)


if __name__ == '__main__':
    from app.models.user import User
    print(create_sql(User))