#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_manager.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from threading import Thread, Event
from core import _job_queue, _task_queue, _state_queue
from common import RUNNING, logger
from model.job import Job
from model.task import Task
from core.job_pool import JobPool

job_queue_listener_running_event = Event()

class JobManager(object):
    def __init__(self):
        self.job_pool = JobPool()
        # 启动时加载上次未完成的Job，略

    def listen_job_queue(self, job_queue, task_queue):
        while True:
            job_id, job_batch_num, job_content = job_queue.get()
            job = self.build_job_from_json(job_id, job_batch_num, job_content)
            logger.info(f"[job listener] {job}")
            task_queue.put(job.start_task)
            job.status = RUNNING
            self.job_pool.add_job(job)
            job_queue_listener_running_event.set()

    def listen_state_queue(self, task_queue, state_queue):
        while job_queue_listener_running_event.wait():
            state = state_queue.get()
            logger.info(f"[sate listener] {state}")
            job = self.job_pool.fetch_job(state.get("job_id"), state.get("job_batch_num"))
            if job:
                task = job.get_task(state.get("task_id"))
                task.status = state.get("status")
                next_tasks = job.next_executable_tasks(task.task_id)
                for i in next_tasks.values():
                    i.status = RUNNING
                self.job_pool.update_job(job)
                for k, v in next_tasks.items():
                    task_queue.put(v)

    @classmethod
    def build_job_from_json(cls, job_id, job_batch_num, job_content):
        job = Job(job_id, job_batch_num, f"job-{job_id}-{job_batch_num}")

        for v in job_content.values():
            prev_task_ids = v.pop("prev_task_ids")
            v["job_id"] = job_id
            v["job_batch_num"] = job_batch_num
            t = Task(**v)
            t.replace_vars(job.global_vars())
            if prev_task_ids:
                for i in prev_task_ids:
                    t.add_prev_id(i)
            job.add_task(task=t)

        return job


def job_start():
    j = JobManager()
    job_listener = Thread(target=j.listen_job_queue, args=(_job_queue, _task_queue), name="job_listener")
    job_listener.start()
    state_listener = Thread(target=j.listen_state_queue, args=(_task_queue, _state_queue), name="state_listener")
    state_listener.start()

    return job_listener, state_listener


if __name__ == '__main__':
    job_start()


