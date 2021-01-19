#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 07:02:28 2021

@author: bnorthan
"""

def tomarkdown(data, racename, outname ):
    markdown='## '+racename+'\n\n'
    markdown+=data.to_markdown()
    out_file=open(outname, "w")
    out_file.write(markdown)
    out_file.close()
