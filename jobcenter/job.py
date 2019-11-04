#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_center.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
import json
from uuid import uuid4
from datetime import datetime, date, timedelta
from jobcenter.task import Task
from jobcenter import WAITING, SUCCESS, FAILED
from jobcenter import ALL_DONE, ALL_SUCCESS, ALL_FAILED, AT_LEAST_ONE_FAILED, AT_LEAST_ONE_SUCCESS


class Job(object):
    def __init__(self, job_id=uuid4().hex, job_name=None):
        self.job_id = job_id
        self.job_name = job_name
        self.start_task = None
        self.end_task = None
        self.tasks = {}
        self.current_running_tasks = {}
        self._status = WAITING

    def global_vars(self):
        return {
            "today": str(date.today()),
            "yesterday": str(date.today() - timedelta(days=1)),
            "start_time": str(datetime.now())
        }

    def prev_tasks(self, task_id):
        pass

    def next_tasks(self, task_id=None, status=None, exec_result=None):
        if not task_id and not status:
            self.current_running_tasks[self.start_task.task_id] = self.start_task
            return self.start_task

        task = self.current_running_tasks[task_id]
        task.change_status(status)
        task.exec_result = exec_result
        final_next_task = {}

        if task == self.end_task:
            return final_next_task

        children = map(lambda x: self.tasks[x[1]], filter(lambda x: x[0] == task.task_id, self.task_relations))
        # logger.info("children: {}".format(children))
        for child in children:
            # logger.info("child: {}".format(child))
            prev_tasks = map(lambda x: self.tasks[x[0]], filter(lambda x: x[1] == child.task_id, self.task_relations))
            if child.exec_condition_id == ALL_DONE and \
                    all(map(lambda x: x.status in (SUCCESS, FAILED), prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition_id == ALL_SUCCESS and \
                    all(map(lambda x: x.status == SUCCESS, prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition_id == ALL_FAILED and \
                    all(map(lambda x: x.status == FAILED, prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition_id == AT_LEAST_ONE_FAILED and \
                    any(map(lambda x: x.status == FAILED, prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition_id == AT_LEAST_ONE_SUCCESS and \
                    any(map(lambda x: x.status == SUCCESS, prev_tasks)):
                final_next_task[child.task_id] = child

        self.current_running_tasks.pop(task.task_id)
        self.current_running_tasks.update(final_next_task)

        return final_next_task

    def __str__(self):
        return "<job_id: {}, tasks: {}>".format(self.job_id, self.tasks)


def build_job_from_json(path):
    # "job_center/job_{}.json".format(self.job_id)
    with open(path, "r", encoding="utf8") as f:
        job_json = json.loads(f.read())

    job = Job()

    for v in job_json.values():
        t = Task(job_id=job.job_id, task_id=v["task_id"], task_name=v["task_name"], task_content=v["task_content"])
        t.replace_vars(job.global_vars())
        t.exec_condition_id = v["exec_condition_id"]
        for i in v["prev_task_ids"]:
            t.add_prev_ids(i)
        job.tasks[t.task_id] = t

        if v["task_type_id"] == 0:
            job.start_task = t
        elif v["task_type_id"] == 2:
            job.end_task = t

    for t in job.tasks:
        for i in t.prev_ids:
            job.tasks[i].add_next_ids(t.task_id)

    return job