#!/bin/python
# -*- coding: utf-8 -*-
# @File  : rdb.py
# @Author: wangms
# @Date  : 2019/10/17
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime


Base = declarative_base()

class Job(Base):
    __tablename__ = 't_jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer)
    job_name = Column(String)
    job_cron = Column(String)
    depends_job_id = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    next_time = Column(DateTime)
    state = Column(String)
    valid_start_time = Column(DateTime)
    valid_end_time = Column(DateTime)


class Task(Base):
    __tablename__ = 't_tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer)
    job_id = Column(Integer)
    task_name = Column(String)
    task_content = Column(String)
    task_type_id = Column(String)
    exec_condition_id = Column(String)
    prev_task_ids = Column(String)
    state = Column(String)
    valid_start_time = Column(DateTime)
    valid_end_time = Column(DateTime)


class JobLog(Base):
    __tablename__ = 't_jog_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer)
    job_id = Column(Integer)
    task_id = Column(Integer)
    log_time = Column(DateTime)
    log_level = Column(String)
    message = Column(String)
    execute_host = Column(String)