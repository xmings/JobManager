#!/bin/python
# -*- coding: utf-8 -*-
# @File  : worker.py
# @Author: wangms
# @Date  : 2019/6/20
# @Brief: 简述报表功能
import subprocess
import sys
from common import SUCCESS, FAILED, RUNNING, logger

class Worker(object):
    def __init__(self, job_id, job_batch_num, task_id, task_content):
        self.job_id = job_id
        self.job_batch_num = job_batch_num
        self.task_id = task_id
        self.task_content = task_content
        self.status = RUNNING

    def run(self, state_queue):
        encoding = "gbk" if sys.platform == "win32" else "utf8"
        try:
            if self.task_content:
                proc = subprocess.Popen(self.task_content, shell=True, encoding=encoding,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                while proc.poll() is None:
                    out = proc.stdout.read()
                    if out:
                        logger.info(f"[worker] <job_id:{self.job_id}>, "
                         f"job_batch_num: {self.job_batch_num}, task_id: {self.task_id}: {out}")
                    err = proc.stderr.read()
                    if err:
                        logger.error(f"[worker] This task <job_id:{self.job_id}>, "
                         f"job_batch_num: {self.job_batch_num}, task_id: {self.task_id} finished with error: {err}")
                self.status = SUCCESS if proc.returncode == 0 else FAILED
            else:
                self.status = SUCCESS
        except Exception as e:
            self.status = FAILED
            logger.error(f"[worker] This task <job_id:{self.job_id}>, "
                         f"job_batch_num: {self.job_batch_num}, task_id: {self.task_id} finished with error: {str(e)}")

        state_queue.put(self.__dict__)


