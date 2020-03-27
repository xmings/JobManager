#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_manager.py
# @Author: wangms
# @Date  : 2019/7/15
import time
from threading import Thread, Event
from core import _job_queue, _task_queue, _state_queue
from common import PREPARE, RUNNING, SUCCESS, FAILED, logger
from dao.zk import JobTaskRunningState
from model.job import Job
from model.task import Task
from core.job_pool import JobPool
from common import ALL_DONE, ALL_SUCCESS, ALL_FAILED, AT_LEAST_ONE_FAILED, AT_LEAST_ONE_SUCCESS

job_queue_listener_running_event = Event()

class JobManager(object):
    def __init__(self):
        self.job_pool = JobPool()
        self.zkStat = JobTaskRunningState()
        # 启动时加载上次未完成的Job，略

    def listen_job_queue(self, job_queue):
        while True:
            job_id, job_batch_num, job_content = job_queue.get()
            job = self.build_job_from_json(job_id, job_batch_num, job_content)
            logger.info(f"[job listener] {job}")
            job.status = RUNNING
            self.job_pool.add_job(job)
            self.next_executable_tasks(job=job)
            self.zkStat.init_job(job)
            for t in job.current_prepare_tasks:
                self.zkStat.job_task_change_listener(t, self.task_finish_action)


    def task_finish_action(self, data, stat):
        print(data, stat)
        job = self.job_pool.fetch_job(job_id=data.get("job_id"), job_batch_num=data.get("job_batch_num"))
        task = job.get_task(data.get("task_id"))
        task.status = int(data.get("status"))
        self.next_executable_tasks(task)
        self.job_pool.update_job(job)
        self.zkStat.create_or_update_job(job)
        return True


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

    def next_executable_tasks(self, task: Task = None, job: Job = None, prepare = True):
        j = self.job_pool.fetch_job(job_id=task.task_id, job_batch_num=task.job_batch_num)

        final_next_task = []
        if not j:
            if prepare:
                job.start_task.status = PREPARE
            return [job.start_task]
        # 如果作业已经结束就不会继续作下一个任务的计算
        if self.status in (SUCCESS, FAILED):
            return final_next_task

        # 如果任务未结束也不会计算下一个任务
        assert task.status in (SUCCESS, FAILED), "This task has not finished"

        for child in job.next_tasks(task.task_id):
            child_prev_tasks = [job.get_task(ptid) for ptid in child.prev_ids]
            if child.exec_condition == ALL_DONE and \
                    all(map(lambda x: x.status in (SUCCESS, FAILED), child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == ALL_SUCCESS and \
                    all(map(lambda x: x.status == SUCCESS, child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == ALL_FAILED and \
                    all(map(lambda x: x.status == FAILED, child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == AT_LEAST_ONE_FAILED and \
                    any(map(lambda x: x.status == FAILED, child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == AT_LEAST_ONE_SUCCESS and \
                    any(map(lambda x: x.status == SUCCESS, child_prev_tasks)):
                final_next_task.append(child)

        # 如果该任务是end_task也没必要计算下一个任务，直接结束。
        # 如果不是end_task并且final_next_task为空，说明依赖未满足，作业执行失败
        if final_next_task == []:
            if task == job.end_task:
                self.status = SUCCESS
                logger.info("[job] this job has finished: {}".format(self))
            else:
                if all([i.status != RUNNING for i in job._tasks.values()]):
                    self.status = FAILED
                    logger.info("[job] this job finished with error: {}".format(self))

        if prepare:
            for t in final_next_task:
                t.status = PREPARE

        return final_next_task

    def poll_job(self, job_id, job_batch_num):
        job = self.job_pool.fetch_job(job_id=job_id, job_batch_num=job_batch_num)
        if not job:
            raise Exception(f"The Job which job_id is {job_id} and job_batch_num is {job_batch_num} was not found")
        if job.status in (SUCCESS, FAILED):
            return job
        return None

    def wait_job(self, job_id, job_batch_num):
        while True:
            job = self.poll_job(job_id, job_batch_num)
            if job:
                return job
            time.sleep(1)


def job_start():
    j = JobManager()
    job_listener = Thread(target=j.listen_job_queue, args=(_job_queue, _task_queue), name="job_listener")
    job_listener.start()
    state_listener = Thread(target=j.listen_state_queue, args=(_task_queue, _state_queue), name="state_listener")
    state_listener.start()

    return job_listener, state_listener


if __name__ == '__main__':
    job_start()


