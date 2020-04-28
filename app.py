#!/bin/python
# -*- coding: utf-8 -*-
# @File  : app.py
# @Author: wangms
# @Date  : 2019/7/15
import os
import json
from model.task import Task
from model.job import Job
from flask import Flask, request, Response, render_template, jsonify
from core import job_dispatch_manager, task_manager_start
from common import JobStatus, TaskStatus, TaskType, DependenCondition

app = Flask(__name__)
task_manager_start()


@app.route("/job")
def job_start():
    job_id = int(request.args.get("job_id"))
    with open(f"job_{job_id}.json", "r", encoding="utf8") as f:
        job_json = json.loads(f.read())
    job = job_dispatch_manager.job_submit(job_id, job_json)
    job.wait()
    return Response(json.dumps(job, cls=CustomJSONEncoder, ensure_ascii=False, indent=4),
                    mimetype="application/json")


@app.route("/job/flow")
def job_flow():
    job_id = request.args.get("job_id")
    return render_template("job_flow.html", job_id=job_id)


@app.route("/steps/status")
def steps_status():
    job_id = request.args.get("job_id")
    job_batch_num = request.args.get("job_batch_num")
    #job = jobmanager.wait_job(job_id, job_batch_num)
    path = os.path.join(os.path.dirname(__file__), f"job_{job_id}.json")
    with open(path, "r", encoding="utf8") as f:
        job_json = json.loads(f.read())
    return jsonify(job_json)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Task):
            return {
                "task_id": o.task_id,
                "task_name": o.task_name,
                "task_content": o.task_content,
                "task_type": TaskType(o.task_type).name,
                "exec_condition": DependenCondition(o.exec_condition).name,
                "prev_task_ids": o.prev_ids,
                "status": TaskStatus(o.status).name
            }
        elif isinstance(o, Job):
            return {
                "job_id": o.job_id,
                "job_batch_num": o.job_batch_num,
                "tasks": list(o.tasks),
                "status": JobStatus(o.status).name
            }


if __name__ == "__main__":
    app.run()
