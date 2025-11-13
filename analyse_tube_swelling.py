#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 14:35:41 2025

@author: brunokeyworth
"""

from numpy import np
from map_ball_path import FRAME_SIZE

def find_tube_radius(ROI):
    
    return 0
    
def get_swelling(folder):
    positions = np.genfromtxt(folder / 'position_time.txt', use_cols=(1))
    photos = sorted(
    [f for f in folder.glob("*.tif") if "empty" not in f.name.lower()]
    )
    mask = (positions < 0.05) | ((FRAME_SIZE - positions) < 0.05)
    
    positions = positions[~mask]
    photos = np.array(photos)[~mask]
    
    for i, x in enumerate(positions):
        photo = photos[i]
        frame_pixels = len(photo)
        lower_edge = (x - 0.015) * (frame_pixels / FRAME_SIZE)
        upper_edge = (x + 0.015) * (frame_pixels / FRAME_SIZE)
        

    return 0
