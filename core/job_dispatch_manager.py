#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_dispatch_manager.py
# @Author: wangms
# @Date  : 2019/7/15
import time
from threading import Thread, Lock
from datetime import datetime, timedelta
from .job_state_manager import zk
from model.job import Job
from model.task import Task
from core.job_cache_pool import JobCachePool
from common import TaskStatus, JobStatus, TaskNodeStatus, DependenCondition, sl4py
from threading import current_thread

assign_task_lock = Lock()

@sl4py
class JobDispatchManager(object):
    def __init__(self):
        # TODO 启动时加载上次未完成的Job
        self.task_nodes = {}
        self.zk = zk
        self.job_cache_pool = JobCachePool()
        self.zk.children_listener_callback(self.zk.node_register_base_path, self.node_register_callback)

    def job_submit(self, job_id, job_content):
        job_batch_num = self.zk.fetch_job_batch_num()
        job = self.build_job_from_json(job_id, job_batch_num, job_content)
        self.logger.info(f"[job listener] {job}")
        job.status = JobStatus.RUNNING
        self.job_cache_pool.add_job(job)
        self.zk.create_job_with_tasks(job)
        if not any(filter(lambda y: y.get("status") == TaskNodeStatus.ONLINE, self.task_nodes.values())):
            self.logger.error("Not any valid task_manager is been found, Pls submit job just a moment")
            return False
        t = Thread(target=self.assign_task, args=(job.start_task,))
        t.start()
        return job

    def assign_task(self, task: Task):
        while True:
            self.logger.info(f"[assign_task] {task}")
            # 作业被终止时，正在等待分配的任务也必须结束
            job = self.job_cache_pool.fetch_job(task.job_id, task.job_batch_num)
            if job.status == JobStatus.TERMINATE:
                break
            elif job.status == JobStatus.PAUSE:
                self.logger.info("job status pause")
                time.sleep(10)
                continue

            with assign_task_lock:
                task.status = TaskStatus.ASSIGN_PREPARE
                task_path = self.zk.generate_path_by_id(task.job_id, task.job_batch_num, task.task_id)
                #self.logger.info(f"all_task_nodes: {self.task_nodes} {current_thread().ident}")
                for task_node_id, info in self.task_nodes.items():
                    if info.get("status") == TaskNodeStatus.OFFLINE:
                        continue
                    elif info.get("update_time") < datetime.now() - timedelta(minutes=5):
                        # TODO: 节点掉线，需要task manager重新注册，该检测机制为被动触发，待改进
                        self.task_nodes[task_node_id].update({"status": TaskNodeStatus.OFFLINE})
                        continue

                    if info.get("current_task_count") < info.get("max_task_count"):
                        print(f"task: {task}, create task assign path")
                        self.zk.data_listener_callback(task_path, self.task_finish_callback)
                        self.zk.create(self.zk.task_assign_path(task_node_id, task))
                        info["current_task_count"] += 1
                        return  # 保证一个任务只被分配给一个task manager

            time.sleep(5)

    def task_finish_callback(self, data, state):
        self.logger.info(f"task_finish_callback: data:{data}, state:{state}")
        job = self.job_cache_pool.fetch_job(job_id=data.get("job_id"), job_batch_num=data.get("job_batch_num"))
        task = job.get_task(data.get("task_id"))
        task.status = TaskStatus(data.get("status"))
        if task.status in (TaskStatus.SUCCESS, TaskStatus.FAILED) \
                and job.status in (JobStatus.RUNNING, JobStatus.MARK_FAILED):

            for child in self.next_executable_tasks(task):
                child.status = TaskStatus.ASSIGN_PREPARE
                thread = Thread(target=self.assign_task, args=(child,))
                thread.start()
            # self.job_cache_pool.update_job(job)
            # return True

        self.job_cache_pool.update_job(job)
        # return False  # 返回True，关闭监听节点

    def node_register_callback(self, children):
        for task_node_id in children:
            if task_node_id not in self.task_nodes:
                path = f"{self.zk.node_register_base_path}/{task_node_id}"
                self.task_nodes[task_node_id] = self.zk.fetch_data(path)
                self.zk.data_listener_callback(path, self.node_resouce_listener_callback)

        # 由于临时节点下不能创建子节点，所以task manager注册时创建的节点改为永久节点，故以下代码失去意义
        # for task_node_id in self.task_nodes.keys():
        #     if task_node_id not in children:
        #         self.task_nodes[task_node_id].update({"status": "OFFLINE"})
        #         # TODO 节点离线，已分配给该节点正在运行的任务需要重分配给其他节点

    def node_resouce_listener_callback(self, data, state):
        if data:
            task_node_id = data.get("task_node_id")
            data["update_time"] = datetime.fromtimestamp(state.mtime / 1000)
            self.task_nodes[task_node_id].update(data)
            #self.logger.info(f"[node_resouce_listener_callback]: data:{data}data, state:{state}")

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

    def next_executable_tasks(self, task: Task):
        job = self.job_cache_pool.fetch_job(job_id=task.job_id, job_batch_num=task.job_batch_num)

        final_next_task = []
        # 如果作业已经结束就不会继续作下一个任务的计算
        if job.status in (JobStatus.SUCCESS, JobStatus.FAILED):
            return final_next_task

        # 如果任务未结束也不会计算下一个任务
        assert task.status in (TaskStatus.SUCCESS, TaskStatus.FAILED), "This task has not finished"

        if task.task_id>=4:
            print(task)
        for child in job.next_tasks(task.task_id):
            child_prev_tasks = [job.get_task(ptid) for ptid in child.prev_ids]
            if child.exec_condition == DependenCondition.ALL_DONE and \
                    all(map(lambda x: x.status in (TaskStatus.SUCCESS, TaskStatus.FAILED), child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == DependenCondition.ALL_SUCCESS and \
                    all(map(lambda x: x.status == TaskStatus.SUCCESS, child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == DependenCondition.ALL_FAILED and \
                    all(map(lambda x: x.status == TaskStatus.FAILED, child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == DependenCondition.AT_LEAST_ONE_FAILED and \
                    any(map(lambda x: x.status == TaskStatus.FAILED, child_prev_tasks)):
                final_next_task.append(child)
            elif child.exec_condition == DependenCondition.AT_LEAST_ONE_SUCCESS and \
                    any(map(lambda x: x.status == TaskStatus.SUCCESS, child_prev_tasks)):
                final_next_task.append(child)

        # 如果该任务是end_task也没必要计算下一个任务，直接结束。
        # 如果不是end_task并且final_next_task为空，说明依赖未满足，作业执行失败
        if final_next_task == []:
            if task == job.end_task:
                job.status = JobStatus.SUCCESS
                self.logger.info("[job] this job has finished: {}".format(job))
            else:
                if all([i.status != TaskStatus.RUNNING for i in job.tasks]):
                    job.status = JobStatus.FAILED
                    self.logger.info("[job] this job finished with error: {}".format(job))

        return final_next_task

    def poll_job(self, job_id, job_batch_num):
        job = self.job_pool.fetch_job(job_id=job_id, job_batch_num=job_batch_num)
        if not job:
            raise Exception(f"The Job which job_id is {job_id} and job_batch_num is {job_batch_num} was not found")
        if job.status in (JobStatus.SUCCESS, JobStatus.FAILED):
            return job
        return None

    def wait_job(self, job_id, job_batch_num):
        while True:
            job = self.poll_job(job_id, job_batch_num)
            if job:
                return job
            time.sleep(1)


job_dispatch_manager = JobDispatchManager()
