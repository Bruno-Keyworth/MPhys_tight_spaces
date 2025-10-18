#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 18:56:34 2025

@author: brunokeyworth
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt

def rect_with_uncertainties(img, thresh_levels, ROI_top, ROI_bot, tube_left, tube_right):
    rects = []
    contours_list = []
    
    for level in thresh_levels:
        _, binary = cv2.threshold(img, level, 255, cv2.THRESH_BINARY_INV)
        ROI = binary[ROI_top:ROI_bot, tube_left:tube_right]
        contours, _ = cv2.findContours(ROI, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        rects.append([x, y, w, h])
        contours_list.append(c)

    if len(rects) == 0:
        return None, None

    rects = np.array(rects)
    mean_rect = np.mean(rects, axis=0)
    std_threshold = np.std(rects, axis=0, ddof=1)

    # rough contour uncertainty (for mid threshold)
    mid_idx = len(thresh_levels) // 2
    c = contours_list[mid_idx].reshape(-1, 2)
    x_min, x_max = np.min(c[:,0]), np.max(c[:,0])
    y_min, y_max = np.min(c[:,1]), np.max(c[:,1])

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
    images = {}
    position_arr = np.empty((0,2))
    pos_uncert = np.empty((0,2))  # new: store uncertainties
    dec_array = np.empty(0)
    
    thresh_levels = range(55, 80, 5)  # adjust as needed
    
    for img_path in folder.glob("*.tiff"):  
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        images[img_path.name] = img
        
        image_copy = img.copy()
        tube_left, tube_right = calc_tube_left_right(image_copy)
        
        mean_rect, σrect = rect_with_uncertainties(
            img, thresh_levels, ROI_top, ROI_bot, tube_left, tube_right
        )
        if mean_rect is None:
            continue
        
        col, row, w, h = mean_rect.astype(int)
        σx, σy, σw, σh = σrect
        
        area = w * h
        c_x = col + w / 2
        c_y = 2056 - (row + h / 2)
        
        rectangularity = cv2.contourArea(np.array([[
            [col, row],
            [col+w, row],
            [col+w, row+h],
            [col, row+h]
        ]])) / area if area > 0 else 0
        
        if rectangularity >= circularity_threshold:
            position_arr = np.vstack([position_arr, [c_y, h]])
            pos_uncert = np.vstack([pos_uncert, [σy, σh]])
            
            file_name = img_path.name
            hex_num = file_name.split("_")[1].split(".")[0]
            dec_array = np.append(dec_array, [int(hex_num, 16)])
            
            if disp:
                fig, ax = plt.subplots()
                ax.imshow(image_copy, cmap='gray')
                ax.axvline(tube_left)
                ax.axvline(tube_right)
                rect = plt.Rectangle((col, row), w, h, color='red', fill=False, linewidth=2)
                ax.add_patch(rect)
                plt.title(f"{img_path.name}\nσy={σy:.2f}, σh={σh:.2f}")
                plt.show()
    
    # centre correction etc. can follow here
    return dec_array, position_arr, pos_uncert
