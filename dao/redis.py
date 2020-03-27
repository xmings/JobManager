#!/bin/python
# -*- coding: utf-8 -*-
# @File  : redis.py
# @Author: wangms
# @Date  : 2019/10/17
from redis import Redis
from model.job import Job
from model.task import Task
import pickle
from threading import Lock

lock = Lock()


class JobCenterPersist(object):
    def __init__(self):
        self.conn = Redis(host='192.168.1.111', port=6379, db=0, password="create")

    def fetch_task_by_id(self, job_id, job_batch_num, task_id):
        return pickle.loads(self.conn.hget(f"jobmanager.task", f"{job_id}-{job_batch_num}-{task_id}"))

    def fetch_task_by_job_id(self, job_id, job_batch_num):
        for key in self.conn.hgetall("jobmanager.task").keys():
            key = key.decode("utf8")
            if key.startswith(f"{job_id}-{job_batch_num}"):
                job_id, job_batch_num, task_id = key.split("-")
                yield self.fetch_task_by_id(job_id, job_batch_num, task_id)

    def save_task(self, task: Task):
        self.conn.hset(f"jobmanager.task", f"{task.job_id}-{task.job_batch_num}-{task.task_id}", pickle.dumps(task))

    def fetch_job_by_id(self, job_id, job_batch_num):
        value = self.conn.hgetall(f"jobmanager.job-{job_id}-{job_batch_num}")
        job = Job(job_id=job_id, job_batch_num=job_batch_num)
        job.job_name = value.get(b"job_name").decode("utf8")
        job.status = int(value.get(b"status").decode("utf8"))
        for task in self.fetch_task_by_job_id(job_id, job_batch_num):
            job.add_task(task)
        return job

    def save_job(self, job: Job):
        self.conn.hset(f"jobmanager.job-{job.job_id}-{job.job_batch_num}", "job_name", job.job_name.encode("utf8"))
        self.conn.hset(f"jobmanager.job-{job.job_id}-{job.job_batch_num}", "status", job.status)
        for task in job.tasks:
            self.save_task(task)

    def fetch_job_batch_num(self, job_id):
        batch_num = self.fetch_current_job_batch_num(job_id)
        batch_num += 1
        with lock:
            self.conn.hset("jobmanager.batchnum", job_id, batch_num)
        return batch_num

    def fetch_current_job_batch_num(self, job_id):
        with lock:
            batch_num = self.conn.hget("jobmanager.batchnum", job_id)
            return int(batch_num) if batch_num else 0



