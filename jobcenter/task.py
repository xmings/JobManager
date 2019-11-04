#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from uuid import uuid4
from jobcenter import WAITING, SUCCESS, FAILED
from jobcenter import ALL_SUCCESS


class Task(object):
    def __init__(self, job_id, task_name, task_content, task_id=uuid4().hex):
        self.job_id = job_id
        self.task_id = task_id
        self.task_name = task_name
        self._task_content = task_content
        self._status = WAITING
        self._prev_task_ids = ()
        self._next_task_ids = ()
        self.exec_condition_id = ALL_SUCCESS
        self.exec_returnning_message = None

    @property
    def status(self):
        return self._status

    def change_status(self, status):
        assert status in (WAITING, SUCCESS, FAILED)
        self._status = status

    def add_next_ids(self, *task_id):
        ids = list(self._next_task_ids) + list(task_id)
        self._next_task_ids = tuple(set(ids))

    @property
    def next_ids(self):
        return self._next_task_ids

    def add_prev_ids(self, *task_id):
        ids = list(self._prev_task_ids) + list(task_id)
        self._prev_task_ids = tuple(set(ids))

    @property
    def prev_ids(self):
        return self._prev_task_ids

    def replace_vars(self, vars):
        assert isinstance(vars, dict)
        for k, v in vars.items():
            self._task_content = self._task_content.replace("${%s}" % (k), v)

    @property
    def task_content(self):
        return self._task_content

    def __eq__(self, other):
        return True if self.task_id == other.task_id else False

    def __str__(self):
        return "<job_id: {}, task_id: {}, task_name: {}, status: {}, condition: {}, next_task_ids: {}>".format(
            self.job_id, self.task_id, self.task_name, self._status, self.exec_condition_id, self._next_task_ids
        )

