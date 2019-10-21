# !/bin/python
# -*- coding: utf-8 -*-
# @File  : state.py
# @Author: wangms
# @Date  : 2019/7/15
# @Brief: 简述报表功能

# from multiprocessing import  Queue
from core.task import Task

t1= Task(1, "start", "")
t2= Task(1, "test1", "dir")
print(t1.children)
t1.add_child(t2)
print(t1.children)

