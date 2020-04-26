#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task.py
# @Author: wangms
# @Date  : 2019/7/15
from uuid import uuid4
from common import TaskStatus, DependenCondition


class Task(object):
    def __init__(self, job_id, job_batch_num, task_name, task_content,
                 task_id=uuid4().hex, task_type=1, exec_condition=DependenCondition.ALL_SUCCESS):
        self.job_id = job_id
        self.job_batch_num = job_batch_num
        self.task_id = task_id
        self.task_name = task_name
        self.task_content = task_content
        self.exec_condition = exec_condition
        self.task_type = task_type
        self._status = TaskStatus.INIT
        self._prev_task_ids = ()
        self._next_task_ids = ()


    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        assert status in TaskStatus
        self._status = status

    def add_prev_id(self, task_id):
        ids = list(self._prev_task_ids)
        ids.append(task_id)
        self._prev_task_ids = tuple(set(ids))

    @property
    def prev_ids(self):
        return self._prev_task_ids

    def replace_vars(self, vars):
        assert isinstance(vars, dict)
        if not self.task_content: return
        for k, v in vars.items():
            self.task_content = self.task_content.replace("${%s}" % (k), v)

    def __eq__(self, other):
        return True if self.task_id == other.task_id else False

    def __str__(self):
        return "<job_id: {}, job_batch_num: {}, task_id: {}, task_name: {}, task_content: {}" \
               ", task_type: {}, status: {}, exec_condition: {}, prev_task_ids: {} >".format(
            self.job_id, self.job_batch_num, self.task_id, self.task_name, self.task_content,
            self.task_type, self.status, self.exec_condition, self.prev_ids
        )


