#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : test_auth.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/3/11 14:23
import pytest


def test_get_users_info(auth_client, default_super_user):
    res = auth_client.get("/v1/users")
    assert res.status_code == 200, res.json
    assert isinstance(res.json, list) and len(res.json) >= 1


@pytest.mark.parametrize('tmp_user', [{'username': 'no_pemission_user', 'role': 'Member'}], indirect=True)
def test_get_users_with_no_permissions(get_auth_client, tmp_user):
    res = get_auth_client(tmp_user).get("/v1/users")
    assert res.status_code == 403
    assert res.json.get('code') == 'AccessDenied'


def test_get_single_user_info(auth_client, default_super_user):
    res = auth_client.get(f"/v1/users/{default_super_user.id}")
    assert res.status_code == 200, res.json
    assert isinstance(res.json, dict) and res.json.get('id') == default_super_user.id


if __name__ == '__main__':
    pytest.main()
