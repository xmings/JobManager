#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task_manager.py
# @Author: wangms
# @Date  : 2019/7/15
from threading import Thread, current_thread
from common import logger, RUNNING, FAILED, SUCCESS
import time
import sys
import socket
import subprocess
from .job_state_manager import ZKJobStateManager


class TaskManager(object):
    def __init__(self, max_task_count=5):
        self.max_task_count = max_task_count
        self.zk = ZKJobStateManager()
        self.task_pool = {}
        # 注册当前任务节点为临时节点
        self.task_node_id = self.zk.fetch_task_node_id()
        self.task_node_path = f"{self.zk.node_register_base_path}/{self.task_node_id}"
        self.zk.create(self.task_node_path, {
            "task_node_id": self.task_node_id,
            "max_task_count": self.max_task_count,
            "current_task_count": 0,
            "status": "online",
            "ip_addr": socket.gethostbyname(socket.gethostname()),
            "thread_id":  current_thread().ident
        })
        self.zk.children_listener_callback(self.task_node_path, self.task_listener_callback)
        self.job_task_id_list = []

    def task_listener_callback(self, children):
        """获取job_manager分配到的任务，并更新该任务的状态和执行节点"""
        logger.info(f"task_listener_callback: children:{children}")
        for job_task_id in filter(lambda x: x not in self.task_id_list, children):
            job_id, job_batch_num, task_id = job_task_id.split("_")
            self.zk.update_task(job_id, job_batch_num, task_id, {"status": RUNNING, "exec_task_node": self.task_node_id})
            p = Thread(target=self.task_worker,
                       args=(job_id, job_batch_num, task_id),
                       name="task_worker")
            p.setDaemon(True)
            p.start()
            self.task_pool[job_task_id] = p
        self.task_id_list = children

    def run(self):
        while True:
            time.sleep(15)
            self.zk.update_data(self.task_node_path, {"current_task_count": len(self.task_pool)})

    def task_worker(self, job_id, job_batch_num, task_id):
        encoding = "gbk" if sys.platform == "win32" else "utf8"
        status = FAILED
        data = self.zk.fetch_task_data_by_id(job_id, job_batch_num, task_id)
        try:
            if data.get("task_content"):
                proc = subprocess.Popen(data.get("task_content"), shell=True, encoding=encoding,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                while proc.poll() is None:
                    out = proc.stdout.read()
                    if out:
                        logger.info(f"[worker] <job_id:{job_id}>, "
                                    f"job_batch_num: {job_batch_num}, task_id: {task_id}: {out}")
                    err = proc.stderr.read()
                    if err:
                        logger.error(f"[worker] This task <job_id:{job_id}>, "
                                     f"job_batch_num: {job_batch_num}, task_id: {task_id} finished with error: {err}")
                status = SUCCESS if proc.returncode == 0 else FAILED
        except Exception as e:
            logger.error(f"[worker] This task <job_id:{job_id}>, "
                         f"job_batch_num: {job_batch_num}, task_id: {task_id} finished with error: {str(e)}")

        self.zk.update_task(job_id, job_batch_num, task_id, {"status": status})


def task_manager_start():
    t = TaskManager()
    task_manager_process = Thread(target=t.run, name="task_manager")
    task_manager_process.start()
    return task_manager_process

