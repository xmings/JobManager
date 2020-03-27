#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2020/3/24
import logging

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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
file = logging.FileHandler("job_manager.log")
file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(console)
logger.addHandler(file)
