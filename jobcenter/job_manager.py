#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_manager.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
import time
import pickle
from datetime import datetime
from redis import Redis
from multiprocessing import Process, Lock
from dao import Job
from jobcenter import _job_queue, _task_queue, _state_queue, COMPLETED, logger, job_queue_listener_running_event

lock = Lock()

class JobManager(object):
    def __init__(self):
        self.job_queue = _job_queue
        self.task_queue = _task_queue
        self.state_queue = _state_queue
        self.conn = Redis(host='192.168.1.111', port=6379, db=0)

    def listen_job_queue(self, job_queue, task_queue):
        while True:
            job_id = job_queue.get()
            job = Job(job_id)
            logger.info("listen_job: {}".format(job))
            task_queue.put(job.next_task())
            self.conn.hset("job_manager.jobs", job_id, pickle.dumps(job))
            job_queue_listener_running_event.set()

    def listen_job_table(self):
        last_scan_time = datetime.now()
        while True:

    def listen_state_queue(self, task_queue, state_queue):
        while job_queue_listener_running_event.wait():
            state = state_queue.get()
            job_bin = self.conn.hget("job_manager.jobs", state.job_id)
            if job_bin:
                job = pickle.loads(job_bin)
                logger.info("listen_sate: {}".format(state))
                next_tasks = job.next_task(state.task_id, state._status, state.exec_result)
                self.conn.hset("job_manager.jobs", job.job_id, pickle.dumps(job))
                # logger.info("listen_sate: {}".format(next_tasks))
                if not next_tasks:
                    # self.conn.hdel("job_manager.jobs", job.job_id)
                    job._status = COMPLETED
                    self.conn.hset("job_manager.jobs", job.job_id, pickle.dumps(job))
                    logger.info("this job has finished: {}".format(job))
                else:
                    for k, v in next_tasks.items():
                        task_queue.put(v)


def job_start():
    j = JobManager()
    job_listener = Process(target=j.listen_job_queue, args=(_job_queue, _task_queue), name="job_listener")
    job_listener.start()
    state_listener = Process(target=j.listen_state_queue, args=(_task_queue, _state_queue), name="state_listener")
    state_listener.start()

    return job_listener, state_listener


if __name__ == '__main__':
    job_start()


