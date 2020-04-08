#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
import yaml

def configuration(prefix):
    with open("config.yaml", "r", encoding="utf8") as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    for i in prefix.split("."):
        config = config.get(i)

    def _fun(cls):
        for k, type in cls.__annotations__.items():
            v = config.get(k)
            setattr(cls, k, v)
        return cls
    return _fun

@configuration(prefix="People")
class Test:
    id: int
    name: str

    def __str__(self):
        return f"id: {self.id}, name: {self.name}"

print(Test.id, Test.name)