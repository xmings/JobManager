#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能

from multiprocessing import Manager
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(console)

mp_manager = Manager()

_job_queue = mp_manager.Queue()
_task_queue = mp_manager.Queue()
_state_queue = mp_manager.Queue()
_resource_queue = mp_manager.Queue()

job_queue_listener_running_event = mp_manager.Event()



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

from core.job_manager import job_start
from core.task_manager import task_start

__all__ = ("submit_job", "job_start", "task_start")
