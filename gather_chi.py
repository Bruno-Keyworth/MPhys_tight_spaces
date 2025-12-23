#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 21 17:43:36 2025

@author: brunokeyworth
"""

from get_preset import all_balls
from get_folderpaths import _ball_folder
import numpy as np

chi_dict = {
    'oil': {
        'no-hold': [],
        'hold': []
        },
    'glycerol': {
        'no-hold': [],
        'hold': []
        }
    }

for ball in all_balls:
    file = _ball_folder(ball_dict=ball) / 'fit_params.txt'
    if not file.exists():
        continue
    params = np.genfromtxt(file)[1, :]
    
    chi_dict[ball['fluid']][ball['method']].append(params[6])
    
for fluid, a in chi_dict.items():
    for method, b in a.items():
        print(fluid, method)
        print(np.mean(b))
        print(max(b))
        print(min(b))