#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from common import logger
from multiprocessing import Manager

mp_manager = Manager()

_job_queue = mp_manager.Queue()
_task_queue = mp_manager.Queue()
_state_queue = mp_manager.Queue()
_resource_queue = mp_manager.Queue()

job_queue_listener_running_event = mp_manager.Event()


def submit_job(job_id, job_batch_id, job_content):
    logger.info(f"submit job: <job_id: {job_id}, job_batch_id: {job_batch_id}>")
    _job_queue.put((job_id, job_batch_id, job_content))

from .job_manager import job_start
from .task_manager import task_start
from model.job import Job
from model.task import Task

__all__ = ("submit_job", "job_start", "task_start", "Job", "Task")
