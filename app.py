#!/bin/python
# -*- coding: utf-8 -*-
# @File  : app.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能

from flask import Flask, jsonify, request
from job_manager import JobManager
from task_manager import TaskManager
app = Flask(__name__)

j = JobManager()
j.start()
t = TaskManager()
t.start()

@app.route("/task/add")
def add_job():
    job_id = request.args.get("job_id")

    return "ok"



if __name__ == "__main__":
    app.run(threaded=True, debug=True)
    j.join()
    t.join()

