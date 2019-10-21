#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from core import WAITING, SUCCESS, FAILED
from core import ALL_SUCCESS

class Task(object):
    def __init__(self, job_id, task_id, task_name, script, _task_type="Shell"):
        self.job_id = job_id
        self.task_id = task_id
        self.task_name = task_name
        self._script = script
        self._task_type = _task_type
        self._children = ()
        self._status = WAITING
        self._prev_task_ids = ()
        self.exec_condition_id = ALL_SUCCESS
        self.exec_result = None

    @property
    def status(self):
        return self._status

    def change_status(self, status):
        assert status in (WAITING, SUCCESS, FAILED)
        self._status = status

    @property
    def children(self):
        return self._children

    def add_child(self, task):
        assert isinstance(task, Task)
        x = list(self._children)
        x.append(task)
        self._children = tuple(x)

    @property
    def prev_ids(self):
        return self._prev_task_ids

    def add_prev_id(self, task_id):
        prev_task_ids = list(self._prev_task_ids)
        prev_task_ids.append(task_id)
        self._prev_task_ids = tuple(prev_task_ids)

    def replace_vars(self, vars):
        assert isinstance(vars, dict)
        for k, v in vars.items():
            self._script = self._script.replace("${%s}"%(k), v)

    @property
    def script(self):
        return self._script

    @property
    def task_type(self):
        return self._task_type

    def __eq__(self, other):
        return True if self.task_id == other.task_id else False

    def __str__(self):
        return "<job_id: {}, task_id: {}, task_type, task_name: {}, status: {}, condition: {}, children: {}>".format(
            self.job_id, self.task_id, self.task_type, self.task_name, self._status, self.exec_condition_id,
            self._children
        )

    def __repr__(self):
        return str(self)

    