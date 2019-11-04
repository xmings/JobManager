#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_manager.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
import time
import pickle
from redis import Redis
from threading import Thread, Event
from jobcenter.job import build_job_from_json
from jobcenter import _job_queue, _task_queue, _state_queue, COMPLETED, logger

job_queue_listener_running_event = Event()

class JobManager(object):
    def __init__(self):
        self.conn = Redis(host='192.168.1.111', port=6379, db=0, password="create")

    def listen_job_queue(self, job_queue, task_queue):
        while True:
            path = job_queue.get()
            job = build_job_from_json(path)
            logger.info("listen_job: {}".format(job))
            task_queue.put(job.next_tasks())
            self.save_job(job)
            job_queue_listener_running_event.set()

    def listen_state_queue(self, task_queue, state_queue):
        while job_queue_listener_running_event.wait():
            state = state_queue.get()
            job = self.fetch_job(state.job_id)
            if job:
                logger.info("listen_sate: {}".format(state))
                next_tasks = job.next_tasks(state.task_id, state._status, state.exec_result)
                self.save_job(job)
                if not next_tasks:
                    job._status = COMPLETED
                    self.save_job(job)
                    logger.info("this job has finished: {}".format(job))
                else:
                    for k, v in next_tasks.items():
                        task_queue.put(v)

    def save_job(self, job):
        self.conn.hset("job_manager.jobs", job.job_id, pickle.dumps(job))
        return True

    def fetch_job(self, job_id):
        job_bin = self.conn.hget("job_manager.jobs", job_id)
        if job_bin:
            return pickle.loads(job_bin)
        return None


def job_start():
    j = JobManager()
    job_listener = Thread(target=j.listen_job_queue, args=(_job_queue, _task_queue), name="job_listener")
    job_listener.start()
    state_listener = Thread(target=j.listen_state_queue, args=(_task_queue, _state_queue), name="state_listener")
    state_listener.start()

    return job_listener, state_listener


if __name__ == '__main__':
    job_start()


