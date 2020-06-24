# -*- coding: utf-8 -*-
# @File : conftest.py
# @Author : mocobk
# @Email : mailmzb@qq.com
# @Time : 2020/5/5 10:30 下午
import time

import pytest
from flask.testing import FlaskClient

from app import create_app
from app.extensions import db as _db, scheduler
from app.libs.enums import Roles
from app.models.user import User
from config import CONFIG
from tests import gen_token, CustomFlaskClient

config = CONFIG['test']
DEFAULT_USER = {
    'name': 'MoSuperAdmin',
    'password': '123456',
    'username': 'MoSuperAdmin',
    'phone': '18566772480',
    'role': 'SuperAdmin',
    'department': '大数据测试部',
    'business_line': '驭信',
    'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
}


@pytest.fixture(scope='session')
def init_app():
    app = create_app(_config=config)
    _db.drop_all(app=app)
    _db.create_all(app=app)
    scheduler.start()
    return app


@pytest.fixture(scope='session')
def app(init_app, request):
    init_app.test_client_class = CustomFlaskClient  # 统一打印响应结果，不需要可注释此句
    return init_app


@pytest.fixture(scope='session')
def db():
    return _db


@pytest.fixture(scope='session')
def client(app):
    """A test client for the app."""
    return app.test_client()


def create_client(app, user: User) -> FlaskClient:
    """根据传入的 app 和 user 返回对应已授权的的 test_client"""
    access_token = gen_token(
        secret_key=app.config['TOKEN_SECRET_KEY'],
        expires_in=app.config['ACCESS_TOKEN_EXPIRATION'],
        uid=user.id,
        role=user.role,
        _type='access'
    )
    client = app.test_client()
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    return client


@pytest.fixture(scope='module')
def auth_client(app, module_user):
    """A authorized test client for the app."""
    return create_client(app, module_user)


@pytest.fixture(scope='module')
def get_auth_client(app):
    def auth_client(user: User) -> FlaskClient:
        return create_client(app, user)

    return auth_client


def create_user(app, db, user: User) -> User:
    with app.app_context():
        with db.auto_commit():
            # # 创建一个超级管理员
            # user = User(**{**DEFAULT_USER, **{'role': user}})
            db.session.add(user)
        # Remove the `instance` from this ``Session``.
        #  This will free all internal references to the instance.  Cascading
        #  will be applied according to the *expunge* cascade rule.
        # 避免返回的 user 对象出现 not bound to a Session 错误
        db.session.refresh(user)
        db.session.expunge(user)
        return user


@pytest.fixture(scope='session')
def default_super_user(app, db):
    user = User(**{**DEFAULT_USER, **{'role': Roles.SUPER_ADMIN.value}})
    return create_user(app, db, user)


@pytest.fixture(scope='session')
def default_admin_user(app, db):
    user = User(**{**DEFAULT_USER, **{'role': Roles.ADMIN.value}})
    return create_user(app, db, user)


@pytest.fixture(scope='session')
def default_member_user(app, db):
    user = User(**{**DEFAULT_USER, **{'role': Roles.MEMBER.value}})
    return create_user(app, db, user)


@pytest.fixture(scope='module')
def module_user(request, app, db, default_super_user):
    """模块中有 USER 变量，则创建相应的用户"""
    _user = getattr(request.module, 'USER', {})
    if _user:
        user = create_user(app, db, User(**{**DEFAULT_USER, **_user}))
        return create_user(app, db, user)
    else:
        return default_super_user


@pytest.fixture()
def tmp_user(request, app, db, default_super_user) -> User:
    """临时用户，方便在测试函数中即用即走"""
    if not hasattr(request, 'param'):
        raise Exception('请先传一个 user 字典对象给 tmp_user fixture')
    _user = {**DEFAULT_USER, **request.param}
    with app.app_context():
        with db.auto_commit():
            print('添加临时用户', _user)
            user = User(**_user)
            db.session.add(user)

        yield user

        with db.auto_commit():
            print('清理临时用户', _user)
            db.session.delete(user)


@pytest.fixture(scope='session')
def expired_access_token(default_super_user):
    """过期的令牌"""
    token = gen_token(
        secret_key=config['TOKEN_SECRET_KEY'],
        expires_in=1,
        uid=default_super_user.id,
        role=default_super_user.role,
        _type='access'
    )
    time.sleep(2)
    return token


@pytest.fixture(scope='session')
def expired_refresh_token(db, default_super_user):
    """过期的刷新令牌"""
    token = gen_token(
        secret_key=config['TOKEN_SECRET_KEY'],
        expires_in=1,
        uid=default_super_user.id,
        role=default_super_user.role,
        _type='refresh'
    )
    time.sleep(2)
    return token
