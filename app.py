#!/bin/python
# -*- coding: utf-8 -*-
# @File  : app.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
import pickle, time
from redis import Redis
from flask import Flask, request, Response
import json

app = Flask(__name__)

from jobcenter import submit_job, job_start, task_start, COMPLETED
from jobs import Job, Task

job_start()
task_start()
conn = Redis(host='192.168.1.111', port=6379, db=0, password="create")

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Task):
            return {
                "task_id": o.task_id,
                "task_name": o.task_name,
                "exec_condition_id": o.exec_condition_id,
                "status": o.status,
                "result": o.exec_result
            }
        elif isinstance(o, Job):
            return {
                "job_id": o.job_id,
                "tasks": o.tasks,
                "status": o._status
            }


@app.route("/job")
def call_job():
    job_id = request.args.get("job_id")
    submit_job(job_id)
    job = None
    while not job or job._status != COMPLETED:
        time.sleep(0.5)
        job_bin = conn.hget("job_manager.jobs", job_id)
        if job_bin:
            job = pickle.loads(job_bin)

    return Response(json.dumps(job, cls=CustomJSONEncoder, ensure_ascii=False, indent=4), mimetype="application/json")



if __name__ == "__main__":
    app.run(threaded=True)
