#!/bin/python
# -*- coding: utf-8 -*-
# @File  : db.py
# @Author: wangms
# @Date  : 2019/7/18
# @Brief: 简述报表功能
from redis import Redis


class RedisService(object):
    def __init__(self):
        self.conn = Redis(host='192.168.1.111', port=6379, db=0)


