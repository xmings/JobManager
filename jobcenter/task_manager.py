#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task_manager.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from core import _task_queue, _state_queue, logger
from core.worker import Worker
from multiprocessing import Process
from threading import Thread
import time


class TaskManager(object):
    def __init__(self, worker_count=4):
        self.all_workers = []
        self.worker_count = worker_count

    def listen_task_queue(self, task_queue, state_queue):
        while True:
            if len(self.all_workers) == self.worker_count:
                time.sleep(1)
                continue

            task = task_queue.get()
            logger.info("listen_task: {}".format(task))
            # self.all_workers.append(worker)
            w = Worker(task)
            # logger.info("listen_task: start task {}".format(task))

            p = Thread(target=w.run, args=(state_queue, ), name="feed_state")
            p.setDaemon(True)
            p.start()



def task_start():
    t = TaskManager()
    task_listener = Process(target=t.listen_task_queue, args=(_task_queue,_state_queue), name="task_listener")
    task_listener.start()
    return (task_listener,)

if __name__ == '__main__':
    task_start()

