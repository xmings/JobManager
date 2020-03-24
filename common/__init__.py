#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2020/3/24
# @Brief: 简述报表功能
import logging

WAITING = 0
RUNNING = 1
SUCCESS = 2
FAILED = 3
COMPLETED = 4

ALL_SUCCESS = 1
ALL_FAILED = 2
AT_LEAST_ONE_SUCCESS = 3
AT_LEAST_ONE_FAILED = 4
ALL_DONE = 5


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
file = logging.FileHandler("core.log")
file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(console)
logger.addHandler(file)
