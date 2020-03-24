#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task_manager.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from core import _task_queue, _state_queue
from core.worker import Worker
from threading import Thread
from dao.redis import JobCenterPersist
from common import logger
import time


class TaskManager(object):
    def __init__(self, worker_count=5):
        self.worker_count = worker_count
        self.db = JobCenterPersist()
        self.thead_pool = []

    def listen_task_queue(self, task_queue, state_queue):
        while True:
            task = task_queue.get()
            logger.info("[task listener] {}".format(task))
            w = Worker(task.job_id, task.job_batch_num, task.task_id, task.task_content)

            p = Thread(target=w.run, args=(state_queue,), name="feed_state")
            p.setDaemon(True)
            p.start()
            self.thead_pool.append(p)

            while True:
                alive_thread = len([i for i in self.thead_pool if i.is_alive()])
                if alive_thread < self.worker_count:
                    break
                time.sleep(0.2)
                logger.info(f"Exceeded maximum thread count {self.worker_count}, in fact is {alive_thread}")

def task_start():
    t = TaskManager()
    task_listener = Thread(target=t.listen_task_queue, args=(_task_queue,_state_queue), name="task_listener")
    task_listener.start()
    return (task_listener,)

if __name__ == '__main__':
    task_start()

