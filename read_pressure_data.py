#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 14:29:03 2025

@author: brunokeyworth
"""

import numpy as np

def read_pressure_data(folder_path):
    
    file_path = folder_path / 'pressure_data.txt'
    
    if not file_path.exists():
        return None
    
    data = np.genfromtxt(file_path, skip_header=1, usecols=(1, 2))
    
    data*=100 # convert to Pa
    # Find indices where the first column is zero
    split_indices = np.where(data[:, 0] == 0)[0]
    
    # Split after those indices
    parts = np.split(data, split_indices + 1)
    
    # Remove any rows starting with 0 and empty arrays
    cleaned_parts = []
    for p in parts:
        # Filter out rows where the first column == 0
        p = p[p[:, 0] != 0]
        if len(p) > 0:
            cleaned_parts.append(p)
            
    data_dict = {}
    for p in cleaned_parts:
        key = int(p[0, 0])
        value = (np.mean(p[:, 1]), np.std(p[:, 1])) 
        data_dict[key] = value

    return data_dict
    
    