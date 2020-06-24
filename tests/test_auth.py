#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : test_auth.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/3/11 14:23
import time

import pytest
from app.libs.token_auth import get_token_info


def test_get_token(app, client, default_super_user):
    data = {
        'username': 'MoSuperAdmin',
        'password': '123456'
    }
    res = client.post("/v1/auth", json=data)
    assert res.status_code == 200, res.json
    with app.app_context():
        assert get_token_info(res.json.get('access_token'), _type='access').role == default_super_user.role
        assert get_token_info(res.json.get('refresh_token'), _type='refresh').role == default_super_user.role


def test_get_token_with_error_account(client, default_super_user):
    error_user_name_data = {
        'username': '',
        'password': '123456'
    }
    error_password_data = {
        'username': 'MoSuperAdmin',
        'password': 'xxxxxx'
    }
    res = client.post("/v1/auth", json=error_user_name_data)
    assert res.status_code == 401, res.json
    res = client.post("/v1/auth", json=error_password_data)
    assert res.status_code == 401, res.json


def test_refresh_token(client, default_super_user):
    data = {
        'username': 'MoSuperAdmin',
        'password': '123456'
    }
    login = client.post("/v1/auth", json=data).json
    refresh = client.post('/v1/auth/refresh', json={'refresh_token': login.get('refresh_token')})
    assert refresh.status_code == 200, refresh.json
    assert refresh.json.get('access_token') and refresh.json.get('refresh_token')


def test_refresh_token_with_error_token(client, default_super_user):
    error_refresh_token = 'xxxx'
    refresh = client.post('/v1/auth/refresh', json={'refresh_token': error_refresh_token})
    assert refresh.status_code == 401, refresh.json
    assert refresh.json.get('code') == 'AuthFailed', refresh.json


def test_refresh_token_with_expired_token(client, expired_refresh_token):
    refresh = client.post('/v1/auth/refresh', json={'refresh_token': expired_refresh_token})
    assert refresh.status_code == 401, refresh.json
    assert refresh.json.get('code') == 'AuthExpired', refresh.json


if __name__ == '__main__':
    pytest.main()
