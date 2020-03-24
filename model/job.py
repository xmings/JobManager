#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_center.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from datetime import datetime, date, timedelta
from model.task import Task
from common import WAITING, SUCCESS, FAILED, logger, RUNNING
from common import ALL_DONE, ALL_SUCCESS, ALL_FAILED, AT_LEAST_ONE_FAILED, AT_LEAST_ONE_SUCCESS


class Job(object):
    def __init__(self, job_id, job_batch_num, job_name=None):
        self.job_id = job_id
        self.job_batch_num = job_batch_num
        self.job_name = job_name
        self.start_task = None
        self.end_task = None
        self._tasks = {}
        self.current_running_tasks = {}
        self._status = WAITING

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
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    def prev_tasks(self, task_id):
        task = self._tasks.get(task_id)
        return (self._tasks.get(i) for i in task.prev_ids)

    def next_tasks(self, task_id):
        return (t for t in self._tasks.values() if task_id in t.prev_ids)

    def get_task(self, task_id):
        return self._tasks.get(task_id)

    def add_task(self, task: Task):
        assert task.task_id not in self._tasks.keys(), f"Same task id {task.task_id}"
        self._tasks[task.task_id] = task

        if task.task_type == 0:
            self.start_task = task
        elif task.task_type == 2:
            self.end_task = task

    def next_executable_tasks(self, task_id=None):
        final_next_task = {}
        # 如果作业已经结束就不会继续作下一个任务的计算
        if self.status in (SUCCESS, FAILED):
            return final_next_task

        if task_id == None:
            return {self.start_task.task_id: self.start_task}

        task = self.get_task(task_id)
        # 如果任务未结束也不会计算下一个任务
        assert task.status in (SUCCESS, FAILED), "This task has not finished"

        for child in self.next_tasks(task.task_id):
            child_prev_tasks = [self.get_task(ptid) for ptid in child.prev_ids]
            if child.exec_condition == ALL_DONE and \
                    all(map(lambda x: x.status in (SUCCESS, FAILED), child_prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition == ALL_SUCCESS and \
                    all(map(lambda x: x.status == SUCCESS, child_prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition == ALL_FAILED and \
                    all(map(lambda x: x.status == FAILED, child_prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition == AT_LEAST_ONE_FAILED and \
                    any(map(lambda x: x.status == FAILED, child_prev_tasks)):
                final_next_task[child.task_id] = child
            elif child.exec_condition == AT_LEAST_ONE_SUCCESS and \
                    any(map(lambda x: x.status == SUCCESS, child_prev_tasks)):
                final_next_task[child.task_id] = child


        # 如果该任务是end_task也没必要计算下一个任务，直接结束。
        # 如果不是end_task并且final_next_task为空，说明依赖未满足，作业执行失败
        if final_next_task == {}:
            if task == self.end_task:
                self.status = SUCCESS
                logger.info("[job] this job has finished: {}".format(self))
            else:
                if all([i.status != RUNNING for i in self._tasks.values()]):
                    self.status = FAILED
                    logger.info("[job] this job finished with error: {}".format(self))

        return final_next_task

    def __str__(self):
        return "<job_id: {}, job_batch_num: {}, job_name: {}, status: {}, tasks: {}>"\
            .format(self.job_id, self.job_batch_num, self.job_name, self.status, self._tasks)
