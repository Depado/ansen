#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# __author__ = 'Benjamin'

import plotly, re
import plotly.plotly as plotpy
from plotly.graph_objs import Scatter

plotly.tools.set_credentials_file(username='blawesom', api_key='d6z7xwbnlq')

with open('output.log', 'r') as dataset:
    data_x, data_y = [], []
    p = re.compile('([0-9\/ \- :]*[| ]*)([0-9]*)([a-z ]*)')
    for lines in dataset:
        data_x.append(re.search(p, lines).group(0))
        data_y.append(re.search(p, lines).group(2))
    data_x.pop(0)
    data_y.pop(0)
    trace = Scatter(x = data_x, y = data_y)
    data = [trace,]
    print(plotpy.plot(data, filename = 'basic-line'))