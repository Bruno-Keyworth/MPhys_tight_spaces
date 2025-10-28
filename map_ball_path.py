#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 09:18:02 2025

@author: brunokeyworth
"""

from rectangle_fit_code import find_ball_position
import numpy as np

TIME_ERROR = 0.01 #s
ruler_len = 14.9 #cm
frame_height = 1016 # pixels
pix_2_dist = ruler_len / frame_height # cm per pixel
CONVERSION_ERROR = 0.3 / frame_height #cm

def frame_edge_correction(position_arr):

    rect_heights = position_arr[:, 3]
    off_edge = (position_arr[:, 2] - rect_heights / 2 < 1) | (position_arr[:, 2] + rect_heights / 2 > 2055)

    ball_height = np.mean(rect_heights[~off_edge])
    ball_height_err = np.std(rect_heights[~off_edge])

    # For rows where row[2] < 1000
    low_edge = off_edge & (position_arr[:, 2] < 1000)
    position_arr[low_edge, 2] = position_arr[low_edge, 2] + (position_arr[low_edge, 3] - ball_height) / 2
    
    # For rows where row[2] >= 1000
    high_edge = off_edge & (position_arr[:, 2] >= 1000)
    position_arr[high_edge, 2] = position_arr[high_edge, 2] + (ball_height - position_arr[high_edge, 3]) / 2
    
    # Error calculation (works for all off edge rows)
    position_arr[off_edge, 5] = np.sqrt(position_arr[off_edge, 5]**2 + (ball_height_err**2  + position_arr[off_edge, 6]**2) / 4)
    
    return position_arr

def map_ball_path(folder, disp=False):   
    positions = []
    
    for ext in ("*.tiff", "*.bmp", "*.tif"):
        for img_path in folder.glob(ext):
            position = find_ball_position(img_path, disp)
            if position is not None:
                positions.append(position)
    position_arr = np.vstack(positions)
    
    position_arr = frame_edge_correction(position_arr)
    position_arr[:, 1:] *= pix_2_dist
    position_arr[:, 0] -= np.min(position_arr[:, 0])
    
    t_err = np.linspace(TIME_ERROR, TIME_ERROR, len(position_arr))
    p_err = np.sqrt((CONVERSION_ERROR * np.absolute(position_arr[:, 2]))**2 + 0.5**2)
    
    data = np.column_stack((position_arr[:, 0], position_arr[:, 2], t_err, p_err))
    
    np.savetxt(folder / 'position_time.txt', data)
