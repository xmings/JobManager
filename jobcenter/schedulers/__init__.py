#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/10/17
import sys
import utils


@utils.oneday('yesterday')
def main(dateStr):
    pass


if __name__ == '__main__':
    sys.exit(main())
