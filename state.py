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

#
# j = Job(1)
# print(j.next_task())
# print(j.next_task(1, 2))


import asyncio

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

asyncio.run(run('sleep 5'))
print("here")