#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 07:16:47 2021

@author: bnorthan

This script reads a csv containing race results and converts it to markdown

The result can be viewed at...

https://bnorthan.github.io/raceresults/results/2020/VirtualStockade

"""

import pandas as pd

results = pd.read_csv('../data/2020/VirtualStockadeFinal.csv')
racename='Virtual Stockade-athon'
outname='../results/2020/VirtualStockade.md'

results=results.drop('Company', axis=1)
results=results.drop('Team', axis=1)

markdown='## '+racename+'\n\n'
markdown+=results.to_markdown()
outfile=open(outname, "w")
outfile.write(markdown)
outfile.close()
