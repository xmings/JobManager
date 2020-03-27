#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task_manager.py
# @Author: wangms
# @Date  : 2019/7/15
from core.worker import Worker
from threading import Thread
from common import logger
import time

from dao.zk import JobTaskRunningState


class TaskManager(object):
    def __init__(self, worker_count=5):
        self.worker_count = worker_count
        self.zkStat = JobTaskRunningState()
        self.thead_pool = []

    def listen_task_queue(self, task_queue):
        alive_thread = 0
        while True:
            task = task_queue.get()
            alive_thread += 1
            logger.info("[task listener] {}".format(task))
            w = Worker(task)

            p = Thread(target=w.run, name="feed_state")
            p.setDaemon(True)
            p.start()
            self.thead_pool.append(p)
            while True:
                alive_thread = len([i for i in self.thead_pool if i.is_alive()])
                if alive_thread < self.worker_count:
                    break
                time.sleep(0.2)
                logger.info(f"Reaches maximum thread count {self.worker_count}")

    def fetch_task(self):
        jobs = self.zkStat.fetch_running_job()


        pass

    def register_heartbeat(self):
        pass

    def register_resource(self):
        pass


def task_start():
    t = TaskManager()
    task_listener = Thread(target=t.listen_task_queue, name="task_listener")
    task_listener.start()
    return (task_listener,)

if __name__ == '__main__':
    task_start()

