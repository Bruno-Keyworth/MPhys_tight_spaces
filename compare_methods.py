#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 12:33:20 2025

@author: brunokeyworth
"""

import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER

marker = {
    'hold': '.',
    'no-hold': 'x',
    }

for i in range(5):

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    
    for method in ['hold', 'no-hold']:
        file = MASTER_FOLDER / 'oil' / method / f'ball{i+1}' / 'speed_pressure.txt'
        
        data = np.genfromtxt(file)
        
        ax.scatter(data[:, 1], data[:, 0], label=method, marker=marker[method])
    
    plt.legend()
    plt.savefig(MASTER_FOLDER / 'oil' / f'ball{i+1}_comparison.png', dpi=300)
    