#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 07:16:47 2021

@author: bnorthan
"""
import sys
import pandas as pd

sys.path.append('../markdown')

import markdownutil

results = pd.read_csv('../../data/2020/VirtualStockadeFinal.csv')

markdownutil.tomarkdown(results, 'Virtual Stockade-athon','../../results/2020/VirtualStockade.md')
