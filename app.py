#!/bin/python
# -*- coding: utf-8 -*-
# @File  : app.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
import time
from flask import Flask, request, Response
import json
from model.task import Task
from model.job import Job
from common import SUCCESS, FAILED
from dao.redis import JobCenterPersist
from core import submit_job, job_start, task_start


app = Flask(__name__)

job_start()
task_start()

db = JobCenterPersist()

@app.route("/job")
def execute_job():
    job_id = int(request.args.get("job_id"))
    job_batch_num = db.fetch_job_batch_num(job_id)

    with open(f"job_{job_id}.json", "r", encoding="utf8") as f:
        job_json = json.loads(f.read())
    submit_job(job_id, job_batch_num, job_json)

    job = None
    while not job or job.status not in (SUCCESS, FAILED):
        time.sleep(0.5)
        job = db.fetch_job_by_id(job_id, job_batch_num)

    return Response(json.dumps(job, cls=CustomJSONEncoder, ensure_ascii=False, indent=4), mimetype="application/json")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Task):
            return {
                "task_id": o.task_id,
                "task_name": o.task_name,
                "task_content": o.task_content,
                "task_type": o.task_type,
                "exec_condition": o.exec_condition,
                "prev_task_ids": o.prev_ids,
                "status": o.status
            }
        elif isinstance(o, Job):
            return {
                "job_id": o.job_id,
                "tasks": o._tasks,
                "status": o._status
            }

if __name__ == "__main__":
    app.run()
