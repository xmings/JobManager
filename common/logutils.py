#!/bin/python
# -*- coding: utf-8 -*-
# @File  : logutils.py
# @Author: wangms
# @Date  : 2020/3/30
import logging
from os import path


def sl4py(cls):
    logger = logging.getLogger(cls.__name__)
    logger.setLevel(logging.INFO)

    if len(logger.handlers)==0:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))

        log_file = path.join(path.dirname(path.dirname(__file__)), "log", "job_manager.log")
        file = logging.FileHandler(log_file)
        file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(console)
        logger.addHandler(file)
    setattr(cls, "logger", logger)
    return cls
