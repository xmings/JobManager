#!/bin/python
# -*- coding: utf-8 -*-
# @File  : task_manager.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from __init__ import _task_queue, _state_queue, logger
from worker import Worker
from multiprocessing import Process


class TaskManager(object):
    def __init__(self):
        self.all_workers = []

    def listen_task_queue(self, task_queue, state_queue):
        while True:
            task = task_queue.get()
            logger.info("listen_task: {}".format(task))
            worker = Worker(task, state_queue)
            self.all_workers.append(worker)
            worker.run()
            # logger.info("listen_task: start task {}".format(task))


def task_start():
    t = TaskManager()
    task_listener = Process(target=t.listen_task_queue, args=(_task_queue,_state_queue), name="task_listener")
    task_listener.start()
    return (task_listener,)

if __name__ == '__main__':
    task_start()

