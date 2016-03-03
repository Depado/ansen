#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# __author__ = 'Benjamin'

import os
import time


def log_info(info):
    with open(os.path.dirname(os.path.realpath(__file__)) +'/output.log','a') as log:
        log.write('\n' + time.strftime("%Y/%m/%d - %H:%M") + ' : ' + info)