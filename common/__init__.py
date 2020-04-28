#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2020/3/24
from .logutils import sl4py
from enum import IntEnum
from threading import Lock

_status_consistency_lock = Lock()

class JobStatus(IntEnum):
    CREATE = 0
    RUNNING = 1
    PAUSE = 2
    TERMINATE = 3
    SUCCESS = 4
    FAILED = 5


class TaskStatus(IntEnum):
    INIT = 0
    ASSIGN_PREPARE = 1
    ASSIGN_FAILED = 2
    ASSIGN_SUCCESS = 3
    RUNNING = 4
    PAUSE = 5
    SKIP = 6
    SUCCESS = 8
    FAILED = 9


class TaskType(IntEnum):
    START = 0
    TASK = 1
    JOB = 2
    END = 5

class TaskNodeStatus(IntEnum):
    ONLINE = 1
    OFFLINE = -1

class DependenCondition(IntEnum):
    ALL_SUCCESS = 0
    ALL_FAILED = 1
    ALL_DONE = 2
    AT_LEAST_ONE_SUCCESS = 3
    AT_LEAST_ONE_FAILED = 4