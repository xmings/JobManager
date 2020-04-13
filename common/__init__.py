#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2020/3/24
from dataclasses import dataclass

WAITING = 0
PREPARE = 1
RUNNING = 2
SUCCESS = 3
FAILED = 4

ALL_SUCCESS = 1
ALL_FAILED = 2
AT_LEAST_ONE_SUCCESS = 3
AT_LEAST_ONE_FAILED = 4
ALL_DONE = 5


def configuration(prefix):
    def _fun(cls):
        cls = dataclass(cls)



        return cls
    return _fun