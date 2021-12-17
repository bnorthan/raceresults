#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 12:09:12 2021

@author: bnorthan

- this script needs to be run in the Django python shell
- to start Django python shell from the mysite project 
- (or other project that imports the raceresults plugin) 
- run python manageserver shell


"""

import sys
from datetime import timedelta
from raceresults.models import Race
from raceresults.models import Result
from raceresults.models import Runner

from scoreware.race import utils

first_name="Erika"
last_name="Oesterle"

runner=Runner(first_name=first_name, last_name=last_name)
runner.save()

for r in Result.objects.all():
    if r.first_name==first_name and r.last_name==last_name:
        print(r.first_name+" "+r.last_name+" "+str(r.time))
        r.runner=runner
        r.save()
