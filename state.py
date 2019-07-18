#!/bin/python
# -*- coding: utf-8 -*-
# @File  : state.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能
from task import Task
from job import Job

# t = Task(1, 1, "test", "..")
# print(t.status)


j = Job(1)
print(j.next_task())
print(j.next_task(1, 2))