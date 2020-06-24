#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : test_auth.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/3/11 14:23
import pytest


def test_get_users_info(auth_client, default_super_user):
    res = auth_client.get("/v1/user/info")
    assert res.status_code == 200, res.json
    assert isinstance(res.json, dict)
    assert 'password' not in res.json
    assert res.json.get('username') == 'MoSuperAdmin'


if __name__ == '__main__':
    pytest.main()
