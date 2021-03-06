#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job.py
# @Author: wangms
# @Date  : 2019/7/15
import time
from datetime import datetime, date, timedelta
from model.task import Task
from common import JobStatus, TaskType, _status_consistency_lock


class Job(object):
    def __init__(self, job_id, job_batch_num, job_name=None):
        self.job_id = job_id
        self.job_batch_num = job_batch_num
        self.job_name = job_name
        self.start_task = None
        self.end_task = None
        self._tasks = {}
        self._status = JobStatus.CREATE
        self.last_running_tasks = set()

    def global_vars(self):
        return {
            "today": str(date.today()),
            "yesterday": str(date.today() - timedelta(days=1)),
            "start_time": str(datetime.now())
        }

    @property
    def tasks(self):
        return self._tasks.values()

    @property
    def current_running_tasks(self):
        for i in self.tasks:
            if i.status == JobStatus.RUNNING:
                yield i
    @property
    def status(self):
        with _status_consistency_lock:
            return int(self._status)

    @status.setter
    def status(self, status):
        with _status_consistency_lock:
            self._status = status

    def prev_tasks(self, task_id):
        task = self._tasks.get(task_id)
        return (self._tasks.get(i) for i in task.prev_ids)

    def next_tasks(self, task_id):
        return (t for t in self._tasks.values() if task_id in t.prev_ids)

    def get_task(self, task_id):
        return self._tasks.get(int(task_id))

    def add_task(self, task: Task):
        assert task.task_id not in self._tasks.keys(), f"Same task id {task.task_id}"
        self._tasks[task.task_id] = task

        if task.task_type == TaskType.START:
            self.start_task = task
            self.last_running_tasks.add(self.start_task)
        elif task.task_type == TaskType.END:
            self.end_task = task

    def poll(self):
        return None if self.status == JobStatus.RUNNING else self.status

    def wait(self):
        while self.poll() is None:
            time.sleep(1)

    def __str__(self):
        return "<job_id: {}, job_batch_num: {}, job_name: {}, status: {}, tasks: {}>"\
            .format(self.job_id, self.job_batch_num, self.job_name, self.status, self._tasks)
