#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
from dao.zk import ZKJobStateManager

zk = ZKJobStateManager()
zk.create("/job/task_node_id")