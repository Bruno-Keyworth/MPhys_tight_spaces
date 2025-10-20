#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 18:56:34 2025

@author: brunokeyworth
"""

import numpy as np
import cv2

def rect_with_uncertainties(img, thresh_levels, ROI_top, ROI_bot, tube_left, tube_right):

    # rough contour uncertainty (for mid threshold)

    tol = 1
    left_edge = c[np.abs(c[:,0] - x_min) <= tol, 1]
    right_edge = c[np.abs(c[:,0] - x_max) <= tol, 1]
    top_edge = c[np.abs(c[:,1] - y_min) <= tol, 0]
    bot_edge = c[np.abs(c[:,1] - y_max) <= tol, 0]

    σx = np.std(left_edge) if len(left_edge) > 1 else 0.5
    σy = np.std(top_edge) if len(top_edge) > 1 else 0.5
    σw = np.std(right_edge) if len(right_edge) > 1 else 0.5
    σh = np.std(bot_edge) if len(bot_edge) > 1 else 0.5

    std_contour = np.array([σx, σy, σw, σh])
    std_total = np.sqrt(std_threshold**2 + std_contour**2)

    return mean_rect, std_total


def map_ball_path(folder, disp=False):   

    
    col, row, w, h = mean_rect.astype(int)
    σx, σy, σw, σh = σrect
    
    area = w * h
    c_x = col + w / 2
    c_y = 2056 - (row + h / 2)

            
