#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 09:18:02 2025

@author: brunokeyworth
"""

from rectangle_fit_code import find_ball_position
import numpy as np

TIME_ERROR = 0.01 #s
ruler_len = 12.8 #cm
pix_2_dist = ruler_len / 2056 # cm per pixel
CONVERSION_ERROR = 0.3 /2056 #cm

def frame_edge_correction(position_arr):

    ball_height = np.max(position_arr[:,3])
    
    for i, row in enumerate(position_arr):
        if row[3] < ball_height - 1:
            if row[2] < 1000:
                centre = row[2] - ball_height +row[3]
                position_arr[i,2] = centre
            else:
                centre = row[2] + ball_height - row[3]
                position_arr[i,2] = centre
    
    return position_arr

def map_ball_path(folder, disp=False):   
    position_arr = np.empty((0,6))
    
    for img_path in folder.glob("*.tiff"):  
        position = find_ball_position(img_path, disp)
        
        if position is None:
            continue

        position_arr = np.vstack((position_arr, position))
    
    position_arr = frame_edge_correction(position_arr)
    
    #=====UNIT=CONVERSION==========================================================
    position_arr[:, 1:] *= pix_2_dist
    position_arr[:, 0] -= np.min(position_arr[:, 0])
    position_arr[:, 0]/= 1000
    
    t_err = np.linspace(TIME_ERROR, TIME_ERROR, len(position_arr))
    p_err = np.sqrt((CONVERSION_ERROR * np.absolute(position_arr[:, 2]))**2 + 0.5**2)

    return (position_arr[:, 0], position_arr[:, 2], t_err, p_err)
