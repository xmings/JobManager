#!/bin/python
# -*- coding: utf-8 -*-
# @File  : job_manager.py
# @Author: wangms
# @Date  : 2019/7/15
import time
from datetime import datetime, timedelta
from common import PREPARE, RUNNING, SUCCESS, FAILED, logger
from .job_state_manager import ZKJobStateManager
from model.job import Job
from model.task import Task
from core.job_cache_pool import JobPool
from common import ALL_DONE, ALL_SUCCESS, ALL_FAILED, AT_LEAST_ONE_FAILED, AT_LEAST_ONE_SUCCESS


class JobManager(object):
    def __init__(self):
        self.job_pool = JobPool()
        # TODO 启动时加载上次未完成的Job
        self.task_nodes = {}
        self.zk = ZKJobStateManager()
        self.zk.children_listener_callback(self.zk.node_register_base_path, self.node_register_callback)

    def job_submit(self, job_id, job_content):
        job_batch_num = self.zk.fetch_job_batch_num()
        job = self.build_job_from_json(job_id, job_batch_num, job_content)
        logger.info(f"[job listener] {job}")
        if not self.task_nodes:
            logger.error("Not any task_manager is been found, Pls submit job just a moment")
            return None
        job.status = RUNNING
        self.zk.create_job_with_tasks(job)
        job.start_task.status = PREPARE
        self.job_pool.add_job(job)
        self.assign_task(job.start_task, force=True)
        return job

    def assign_task(self, task: Task, force=False):
        task_path = self.zk.generate_path_by_id(task.job_id, task.job_batch_num, task.task_id)
        for task_node_id, info in self.task_nodes.items():
            if info.get("update_time") < datetime.now() - timedelta(minutes=20):
                # TODO: 节点掉线，需要task manager重新注册，该检测机制为被动触发，待改进
                self.zk.update_data(f"{self.zk.node_register_base_path}/{info.get('task_node_id')}",
                                    {"status": "offline"})
                continue

            if info.get("current_task_count") < info.get("max_task_count"):
                self.zk.data_listener_callback(task_path, self.task_finish_callback)
                path = f"{self.zk.node_register_base_path}/{task_node_id}/{task.job_id}_{task.job_batch_num}_{task.task_id}"
                self.zk.create(path)
                info["current_task_count"] += 1
                return True  # 保证一个任务只被分配给一个task manager

        if force:
            self.zk.data_listener_callback(task_path, self.task_finish_callback)
            task_node_id = list(filter(lambda x: self.task_nodes[x]["status"] != "offline", self.task_nodes))[-1]
            path = f"{self.zk.node_register_base_path}/{task_node_id}/{task.job_id}_{task.job_batch_num}_{task.task_id}"
            self.zk.create(path)
            self.task_nodes[task_node_id]["current_task_count"] += 1
            return True

        return False

    def task_finish_callback(self, data, state):
        logger.info(f"task_finish_callback: data:{data}, state:{state}")
        job = self.job_pool.fetch_job(job_id=data.get("job_id"), job_batch_num=data.get("job_batch_num"))
        task = job.get_task(data.get("task_id"))
        task.status = int(data.get("status"))
        if task.status in (SUCCESS, FAILED):
            self.next_executable_tasks(task)
            for t in job.current_prepare_tasks:
                self.assign_task(t)
        self.job_pool.update_job(job)
        return True  # 返回True，关闭监听节点

    def node_register_callback(self, children):
        for task_node_id in children:
            if task_node_id not in self.task_nodes:
                path = f"{self.zk.node_register_base_path}/{task_node_id}"
                self.task_nodes[task_node_id] = self.zk.fetch_data(path)
                self.zk.data_listener_callback(path, self.node_resouce_listener_callback)

        # 由于临时节点下不能创建子节点，所以task manager注册时创建的节点改为永久节点，故以下代码失去意义
        # for task_node_id in self.task_nodes.keys():
        #     if task_node_id not in children:
        #         self.task_nodes[task_node_id].update({"status": "offline"})
        #         # TODO 节点离线，已分配给该节点正在运行的任务需要重分配给其他节点

    def node_resouce_listener_callback(self, data, state):
        if data:
            task_node_id = data.get("task_node_id")
            data["update_time"] = datetime.fromtimestamp(state.mtime / 1000)
            self.task_nodes[task_node_id].update(data)
            logger.info(f"[node_resouce_listener_callback]: data:{data}, state:{state}")

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
        job = self.job_pool.fetch_job(job_id=task.job_id, job_batch_num=task.job_batch_num)

        final_next_task = []
        # 如果作业已经结束就不会继续作下一个任务的计算
        if job.status in (SUCCESS, FAILED):
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
                job.status = SUCCESS
                logger.info("[job] this job has finished: {}".format(job))
            else:
                if all([i.status != RUNNING for i in job._tasks.values()]):
                    job.status = FAILED
                    logger.info("[job] this job finished with error: {}".format(job))

        for task in final_next_task:
            task.status = PREPARE

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
