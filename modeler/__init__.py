#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/6/24
# @Brief: 简述报表功能
from flask import Blueprint

modeler = Blueprint('modeler', __name__)

from modeler import view

