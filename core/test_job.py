#!/bin/python
# -*- coding: utf-8 -*-
# @File  : test_job.py
# @Author: wangms
# @Date  : 2019/7/17
# @Brief: 简述报表功能
from core import _job_queue
from core.job_manager import job_start
from core.task_manager import task_start

if __name__ == '__main__':
    _job_queue.put(1)
    _job_queue.put(2)
    _job_queue.put(3)
    job_start()
    task_start()