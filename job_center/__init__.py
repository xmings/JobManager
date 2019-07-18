#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能

from multiprocessing import Queue
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(console)

_job_queue = Queue()
_task_queue = Queue()
_state_queue = Queue()
_resource_queue = Queue()


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

def submit_job(job_id):
    _job_queue.put(job_id)

from job_center.job_manager import job_start
from job_center.task_manager import task_start

__all__ = ("submit_job", "job_start", "task_start")
