#!/bin/python
# -*- coding: utf-8 -*-
# @File  : core.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
import json
from datetime import datetime, date, timedelta
from core.task import Task
from core import WAITING, SUCCESS, FAILED
from core import ALL_DONE, ALL_SUCCESS, ALL_FAILED, AT_LEAST_ONE_FAILED, AT_LEAST_ONE_SUCCESS


class Job(object):
    def __init__(self, job_id):
        self.job_id = job_id
        self.current_tasks = {}
        self.start_task = None
        self.end_task = None
        self.tasks = {}
        self.task_relations = []  # [(before,after), ...]
        self._status = WAITING

        with open("job_{}.json".format(self.job_id), "r", encoding="utf8") as f:
            self.job_json = json.loads(f.read())

        self._build()

    def global_vars(self):
        return {
            "today": str(date.today()),
            "yesterday": str(date.today() - timedelta(days=1)),
            "start_time": str(datetime.now())
        }

    def _build(self):
        for v in self.job_json.values():
            t = Task(self.job_id, v["task_id"], v["task_name"], v["script"])
            t.replace_vars(self.global_vars())
            t.exec_condition_id = v["exec_condition_id"]

            self.tasks[t.task_id] = t

            self.task_relations.append((t.task_id, v["next_step_id"]))

            if v["step_type_id"] == 1:
                self.start_task = t
            elif v["step_type_id"] == 2:
                self.end_task = t

    def next_task(self, task_id=None, status=None, exec_result=None):
        if not task_id and not status:
            self.current_tasks[self.start_task.task_id] = self.start_task
            return self.start_task

        task = self.current_tasks[task_id]
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

        self.current_tasks.pop(task.task_id)
        self.current_tasks.update(final_next_task)

        return final_next_task

    def __str__(self):
        return "<job_id: {}, tasks: {}>".format(self.job_id, self.tasks)


def build_job_from_db(job_id):
    pass

def build_job_from_json(job_json):
    pass