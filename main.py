#!/usr/bin/python
# -*- coding: UTF-8 -*-
# __author__ = 'Benjamin'

from fonctions import *
import time

start_time = time.time()

update_db_proj('AN.db')
delta = time.time() - start_time
print('List OK - %s' % delta)

update_db_amd_list('AN.db')
delta2 = time.time() - start_time - delta
print('Update OK - %s' % delta2)

download_amd('AN.db')
