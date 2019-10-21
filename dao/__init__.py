#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/10/17
from .rdb import Job, Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine =create_engine
Session = sessionmaker(bind=engine)
session = Session()

__all__ = ("Job", "Task")
