#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_pool.py
# @Author: wangms
# @Date  : 2020/3/24
# @Brief: 简述报表功能
from model.job import Job
from dao.redis import JobCenterPersist
from threading import Lock
from common import RUNNING

lock = Lock()

class JobPool(object):
    def __init__(self):
        self._pool = ()
        self.db = JobCenterPersist()

    def add_job(self, job: Job):
        with lock:
            assert (job.job_id, job.job_batch_num) not in [(j.job_id, j.job_batch_num) for j in self._pool]
            pool = list(self._pool)
            pool.append(job)
            self._pool = tuple(pool)
            self.db.save_job(job)

    def delete_job(self, job: Job):
        with lock:
            pool = [j for j in self._pool if j.job_id != job.job_id and j.job_batch_num != job.job_batch_num]
            self._pool = tuple(pool)

    def update_job(self, job: Job):
        with lock:
            pool = [j for j in self._pool if j.job_id != job.job_id and j.job_batch_num != job.job_batch_num]
            if job.status == RUNNING:
                pool.append(job)
            self._pool = tuple(pool)
            self.db.save_job(job)


    def fetch_job(self, job_id, job_batch_num):
        with lock:
            for i in self._pool:
                if i.job_id == job_id and i.job_batch_num == job_batch_num:
                    return i

