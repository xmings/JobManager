#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_state_manager.py
# @Author: wangms
# @Date  : 2020/3/26
# @Brief: 简述报表功能
import json
from kazoo.client import KazooClient

from model.job import Job
from model.task import Task



class ZKJobStateManager(object):
    def __init__(self):
        self.zk = KazooClient(hosts="192.168.1.111")
        self.zk.start()

        self.job_data_base_path = "/job_center"
        self.task_base_path = f"{self.job_data_base_path}/job"
        self.task_node_id_path = f"{self.job_data_base_path}/task_node_id"
        self.job_batch_num_path = f"{self.job_data_base_path}/job_batch_num"
        self.node_register_base_path = f"{self.job_data_base_path}/node_register"

        self.zk.ensure_path(self.task_base_path)
        self.zk.ensure_path(self.task_node_id_path)
        self.zk.ensure_path(self.job_batch_num_path)

        if self.zk.exists(self.node_register_base_path):
            self.zk.delete(self.node_register_base_path, recursive=True)
            self.zk.create(self.node_register_base_path)

    def __del__(self):
        self.zk.close()

    def create_job_with_tasks(self, job: Job):
        path = self.generate_path_by_id(job.job_id)
        if not self.zk.exists(path):
            data = {
                "job_id": job.job_id,
                "job_name": job.job_name
            }
            self.create(path, data)

        self.create_job(job)

        for t in job.tasks:
            self.create_task(t)

    def create_job(self, job: Job):
        data = {
            "job_id": job.job_id,
            "job_batch_num": job.job_batch_num,
            "status": job.status,
            "current_running_tasks": [i for i in job.current_running_tasks],
            "current_prepare_tasks": [i for i in job.current_prepare_tasks]
        }
        self.create(self.generate_path_by_id(job.job_id, job.job_batch_num), data)

    def create_task(self, task: Task):
        data = {
            "job_id": task.job_id,
            "job_batch_num": task.job_batch_num,
            "task_id": task.task_id,
            "task_name": task.task_name,
            "task_content": task.task_content,
            "task_type": task.task_type,
            "exec_condition": task.exec_condition,
            "status": task.status,
            "exec_task_node": None
        }
        self.create(self.generate_path_by_id(task.job_id, task.job_batch_num, task.task_id), data)

    def create(self, path, data=None, ephemeral=False):
        data = data if data else {}
        self.zk.create(path, json.dumps(data).encode("utf8"), ephemeral=ephemeral)

    def update_job(self, job_id, job_batch_num, data):
        path = self.generate_path_by_id(job_id, job_batch_num)
        self.update_data(path, data)

    def update_task(self, job_id, job_batch_num, task_id, data):
        path = self.generate_path_by_id(job_id, job_batch_num, task_id)
        self.update_data(path, data)

    def fetch_data(self, path, with_state=False):
        data, state = self.zk.get(path)
        data = json.loads(data.decode("utf8"))
        return data if not with_state else (data, state)

    def fetch_task_data_by_id(self, job_id, job_batch_num, task_id):
        return self.fetch_data(self.generate_path_by_id(job_id, job_batch_num, task_id))

    def update_data(self, path, data, overwrite=False):
        if not overwrite:
            old_data = self.fetch_data(path)
            old_data.update(data)
            self.zk.set(path, json.dumps(old_data).encode("utf8"))
            return True
        self.zk.set(path, json.dumps(data).encode("utf8"))

    def data_listener_callback(self, path, callback):
        @self.zk.DataWatch(path)
        def __func(data, state):
            if data and state:
                # 防止ephemeral节点被zookeeper删除时，触发回调时传入的参数为None
                data = json.loads(data.decode("utf8"))
                return callback(data, state)
        return __func

    def children_listener_callback(self, path, callback):
        @self.zk.ChildrenWatch(path)
        def __func(children):
            return callback(children)

        return __func

    def generate_path_by_id(self, job_id=None, job_batch_num=None, task_id=None):
        path = self.task_base_path
        if job_id != None:
            path += f"/{job_id}"
            if job_batch_num != None:
                path += f"/{job_batch_num}"
                if task_id != None:
                    path += f"/{task_id}"
        return path

    def fetch_task_node_id(self):
        if not self.zk.exists(self.task_node_id_path):
            self.zk.create(self.task_node_id_path)

        state = self.zk.set(self.task_node_id_path, b"")
        return f"task_node_{state.version}"

    def fetch_job_batch_num(self):
        if not self.zk.exists(self.job_batch_num_path):
            self.zk.create(self.job_batch_num_path)

        state = self.zk.set(self.job_batch_num_path, b"")
        return state.version


    def __getattr__(self, item):
        return getattr(self.zk, item)
