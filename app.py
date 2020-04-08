#!/bin/python
# -*- coding: utf-8 -*-
# @File  : app.py
# @Author: wangms
# @Date  : 2019/7/15
from flask import Flask, request, Response
import json
from .model.task import Task
from .model.job import Job
from .core import job_manager, task_manager_start


app = Flask(__name__)
task_manager_start()


@app.route("/job")
def execute_job():
    job_id = int(request.args.get("job_id"))
    with open(f"job_{job_id}.json", "r", encoding="utf8") as f:
        job_json = json.loads(f.read())
    job = job_manager.job_submit(job_id, job_json)
    if job is None:
        return Response("提交作业失败，详情请查看日志", status=400)
    job.wait()
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
                "job_batch_num": o.job_batch_num,
                "tasks": o.tasks,
                "status": o.status
            }


if __name__ == "__main__":
    app.run()
