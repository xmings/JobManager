#!/bin/python
# -*- coding: utf-8 -*-
# @File  : zk.py
# @Author: wangms
# @Date  : 2020/3/26
# @Brief: 简述报表功能
import json
from kazoo import client
from model.job import Job
from model.task import Task


class JobTaskRunningState(object):
    def __init__(self, host="192.168.1.111"):
        self.zk = client.KazooClient(hosts=host)
        self.zk.start()
        self.job_data_base_path = "/job"
        self.resouce_data_base_path = "/resouce"

        if not self.zk.exists(self.job_data_base_path):
            self.zk.create(self.job_data_base_path)



    def init_job(self, job: Job):
        v1 = {}
        v1["job_id"] = job.job_id
        v1["job_name"] = job.job_name

        self._create_or_update(self._generate_path(job, True), json.dumps(v1))

        v2 = {}
        v2["job_batch_num"] = job.job_batch_num
        v2["status"] = job.status
        self._create_or_update(self._generate_path(job), json.dumps(v2))

        # 把当前的job的路径写入/job节点，等待task_manager监控
        self.zk.get(self.)


        self.zk.set(self.job_data_base_path, )

        for t in job.tasks:
            self._create_or_update(t)

    def _generate_path(self, i, base=False):
        p = f"{self.job_data_base_path}/{i.job_id}"
        if base:
            return p
        p += f"/{i.job_batch_num}"
        if isinstance(i, Job):
            return p
        elif isinstance(i, Task):
            return f"{p}/{i.task_id}"

    def create_or_update_task(self, task: Task):
        value = {}
        value["task_id"] = task.task_id
        value["task_name"] = task.task_name
        value["task_content"] = task.task_content
        value["task_type"] = task.task_type
        value["exec_condition"] = task.exec_condition
        value["status"] = task.status
        self._create_or_update(self._generate_path(task), json.dumps(value))
        return True

    def create_or_update_job(self, job: Job):
        value = {}
        value["job_batch_num"] = job.job_batch_num
        value["status"] = job.status
        value["current_running_tasks"] = [i for i in job.current_running_tasks]
        value["current_prepare_tasks"] = [i for i in job.current_prepare_tasks]
        self._create_or_update(self._generate_path(job), json.dumps(value))
        return True

    def _create_or_update(self, path, value=""):
        if self.zk.exists(path):
            self.zk.set(path, value.encode("utf8"))
        else:
            self.zk.create(path, value.encode("utf8"))

    def job_task_change_listener(self, i, callback):
        @self.zk.DataWatch(self._generate_path(i))
        def state_listener(data, stat):
            return callback(data.decode("utf8"), stat)
        return state_listener

    def fetch_running_jobs(self):
        pass


