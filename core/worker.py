#!/bin/python
# -*- coding: utf-8 -*-
# @File  : worker.py
# @Author: wangms
# @Date  : 2019/6/20
import subprocess
import sys
from common import SUCCESS, FAILED, RUNNING, logger
from dao.zk import JobTaskRunningState


class Worker(object):
    def __init__(self, task):
        self.task = task
        self.zkStat = JobTaskRunningState()

    def run(self):
        encoding = "gbk" if sys.platform == "win32" else "utf8"
        self.task.status = RUNNING
        try:
            if self.task.task_content:
                proc = subprocess.Popen(self.task.task_content, shell=True, encoding=encoding,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                while proc.poll() is None:
                    out = proc.stdout.read()
                    if out:
                        logger.info(f"[worker] <job_id:{self.task.job_id}>, "
                         f"job_batch_num: {self.task.job_batch_num}, task_id: {self.task.task_id}: {out}")
                    err = proc.stderr.read()
                    if err:
                        logger.error(f"[worker] This task <job_id:{self.task.job_id}>, "
                         f"job_batch_num: {self.task.job_batch_num}, task_id: {self.task.task_id} finished with error: {err}")
                self.task.status = SUCCESS if proc.returncode == 0 else FAILED
            else:
                self.task.status = SUCCESS
        except Exception as e:
            self.task.status = FAILED
            logger.error(f"[worker] This task <job_id:{self.task.job_id}>, "
                         f"job_batch_num: {self.task.job_batch_num}, task_id: {self.task.task_id} finished with error: {str(e)}")


        self.zkStat.update_task(task=self.task)


