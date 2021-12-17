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
import os

def make_markdown(racename, results, outname):
    markdown='## '+racename+'\n\n'
    markdown+=results.to_markdown()
    outfile=open(outname, "w")
    outfile.write(markdown)
    outfile.close()

results = pd.read_csv('../data/2020/VirtualStockadeFinal.csv')
racename='Virtual Stockade-athon'
outname='../results/2020/VirtualStockade.md'

results=results.drop('Company', axis=1)
results=results.drop('Team', axis=1)

results = pd.read_csv('../data/2021/Stockade/Stockade_parsed.csv')
racename='Stockade-athon 2021'
outdir = '../results/2021/'
outname=outdir+'Stockade.md'

if os.path.exists(outdir)==False:
    os.makedirs(outdir)

make_markdown(racename, results, outname)
