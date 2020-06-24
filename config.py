#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import datetime
import os


class _Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    DEBUG = False
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

    def __getitem__(self, item):
        return getattr(self, item)


# 生产环境
class _ProductionConfig(_Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:admin@mysql:3306/test_fly?charset=utf8mb4"
    SCHEDULER_API_ENABLED = True  # 可以直接提供API操作jobs   http://172.22.145.101:8090/scheduler/jobs
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 128,
        'pool_recycle': 10,
        'max_overflow': 128,
    }


class _DevelopmentConfig(_Config):
    ENV = 'Development'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://DSJ_test_supper:c5f3cHH8fe_76c20c8d6#Hc030,f@172.22.145.101:3306/test_fly?charset=utf8mb4"
    SQLALCHEMY_ECHO = True  # 开启 sqlalchemy 调试模式
    SCHEDULER_ALLOWED_HOSTS = ['NOT ALLOWED']  # 本机调试不开启 默认开启
    SQLALCHEMY_ECHO_POOL = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 128,
        'pool_recycle': 10,
        'max_overflow': 128,
    }
    DEBUG = True


class _TestConfig(_DevelopmentConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://DSJ_test_supper:c5f3cHH8fe_76c20c8d6#Hc030,f@172.22.145.101:3306/test_fly_test_db?charset=utf8mb4"
    TESTING = True
    SQLALCHEMY_ECHO = False  # 开启 sqlalchemy 调试模式


CONFIG = {
    'development': _DevelopmentConfig(),
    'production': _ProductionConfig(),
    'test': _TestConfig(),
}
