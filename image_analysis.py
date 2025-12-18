# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 15:49:42 2025

@author: David Mawson
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from get_tube_ROI import calc_tube_left_right
import matplotlib.transforms as mtransforms

#parameters
min_radius = 10
max_radius = 500
rectangularity_threshold = 0.7

cmap = plt.get_cmap('viridis', 80)

def show_image(img, title, left, right):
    plt.imshow(img, cmap='gray')
    plt.axvline(left)
    plt.axvline(right)
    plt.title(title)
    plt.axis('off')
    plt.show()

def find_rectangle(threshold, ROI, tube_left):
    
    _, binary_inv = cv2.threshold(ROI, threshold, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None
    
    c = max(contours, key=cv2.contourArea)
    col, row, w, h = cv2.boundingRect(c)
    if (w < min_radius and w > max_radius) or h > max_radius:
        return None, None

    area = cv2.contourArea(c)
    rect_area = w*h
    rectangularity = area / rect_area if rect_area > 0 else 0 
        
    # checks how rectangular the object is
    if rectangularity < rectangularity_threshold:
        return None, None
        
    x= col + tube_left +  w / 2
    y= row + h / 2
    
    centre = (int(x), int(y))
    print(f"Centre = {centre}, height = {h:.2f}, Rectangularity = {rectangularity:.2f}\n")
    
    rect = plt.Rectangle((col+tube_left, row), w, h, color=cmap(threshold),
    fill=False, linewidth=0.5, linestyle='dashed', label = f'Threshold = {threshold}')

    return np.array([x, y, h]), rect

def get_rect_with_errors(ROI, tube_left):
    
    rects = []
    rect_coords = np.empty((0, 3))
    
    thresh_levels = range(30, 100, 10)
    for level in thresh_levels:
        print(level)
        coords, rect = find_rectangle(level, ROI, tube_left)
        if rect is None:
            continue
        rects.append(rect)
        rect_coords = np.vstack((rect_coords, coords))
    if not rects:
        return None
    mean_rect = np.mean(rect_coords, axis=0)
    if len(rect_coords) > 1:
        std_threshold = np.std(rect_coords, axis=0, ddof=1)
    else:
        std_threshold = np.array([1, 1, 1])
    
    return mean_rect, std_threshold, rects

def find_ball_position(img_path, disp=False):
    
    filename = img_path.name
    if filename.split('_')[0]=='empty':
        return None
    
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    
    # only searches this region for rectangles
    tube_left, tube_right = calc_tube_left_right(img)
    ROI = img[0:len(img), tube_left:tube_right]

    print(f"Image: {img_path.name}")
    rect = get_rect_with_errors(ROI, tube_left)
    
    if disp:
        plt.close('all')
        #plots image with rectangle on it
        fig, ax = plt.subplots()
        ax.imshow(img, cmap='gray')
        ax.axis('off')
        height = len(img)
        cm = 1/14.9 * height
        ax.plot([80, 80], [150, 150+cm], c='b', linewidth=0.5)
        # ax.axvline(tube_left)                       
        # ax.axvline(tube_right)
    if rect is None:
        img_path.rename(img_path.with_name('empty_'+filename))
        #plt.title(img_path.parent.name +'\n'+ filename + '\nempty')
        return None
    mean_rect = np.array(rect[0]) / len(img)
    rect_err = np.array(rect[1]) / len(img)
    rects = rect[2]
    if disp:
        ax.add_patch(rects[0])
        ax.add_patch(rects[-1])
        # leg = plt.legend(labelspacing=1.2, frameon=True)
        # trans = mtransforms.Affine2D().rotate_deg(90) + ax.transAxes
        # leg.set_transform(trans)
        plt.savefig(img_path.parent / (img_path.name.split('.')[0] + 'png'), dpi=500)
        #plt.title(img_path.parent.name +'\n'+ filename)
        plt.show() 
        
    file_name = img_path.name
    timestamp = file_name.split("_")[1].split(".")[0]
    if len(timestamp) == 16:
        time = int(timestamp, 16) / 1000
    else:
        time = int(timestamp) * 10**-6
        
    return np.concatenate(([time], mean_rect, rect_err))

