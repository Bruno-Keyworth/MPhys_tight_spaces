# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 15:49:42 2025

@author: David Mawson
"""

import cv2
import matplotlib.pyplot as plt
from get_tube_ROI import calc_tube_left_right

#constants
min_radius = 100
max_radius = 1000
rectangularity_threshold = 0.7

ROI_top = 0 
ROI_bot = 2056 #2*max_radius


def show_image(img, title, left, right):
    plt.imshow(img, cmap='gray')
    plt.axvline(left)
    plt.axvline(right)
    plt.axhline(ROI_bot)
    plt.title(title)
    plt.axis('off')
    plt.show()
    
def find_best_rectangle(contours, tube_left):
    c = max(contours, key=cv2.contourArea)

    col, row, w, h = cv2.boundingRect(c)
    if (w < min_radius and w > max_radius) or h > max_radius:
        return None

    area = cv2.contourArea(c)
    rect_area = w*h
    rectangularity = area / rect_area if rect_area > 0 else 0 
        
    # checks how rectangular the object is
    if rectangularity < rectangularity_threshold:
        return None
        
    x= col + tube_left
    y= ROI_bot - row
    
    centre = (int(x), int(y))
    print(f"Centre = {centre}, height = {h:.2f}, Rectangularity = {rectangularity:.2f}\n")
    
    rect = plt.Rectangle((x, row), w, h, color='red', fill=False, linewidth=2)

    return x, y, h, rect
    
    
def find_ball_position(img_path, disp=False):
    
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    #convert to binary using threshold intensity
    _, binary_inv = cv2.threshold(img, 65, 255, cv2.THRESH_BINARY_INV)
    
    # only searches this region for rectangles
    tube_left, tube_right = calc_tube_left_right(img)
    ROI = binary_inv[ROI_top:ROI_bot, tube_left:tube_right]
    
    # Find contours
    contours, _ = cv2.findContours(ROI, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None

    print(f"Image: {img_path.name}")

    best_rect = find_best_rectangle(contours, tube_left)
    if best_rect is None:
        return None
    x, y, h, rect = best_rect
    
    if disp:
        #plots image with rectangle on it
        fig, ax = plt.subplots()
        ax.imshow(img, cmap='gray')
        ax.axvline(tube_left)                       
        ax.axvline(tube_right)

        ax.add_patch(rect)
        plt.title("Rectangle Found")
        plt.show() 
        
    file_name = img_path.name
    hex_num = file_name.split("_")[1].split(".")[0]
    time = int(hex_num, 16)
    # dummy errors
    xerr = 0.1
    yerr = 0.1
    herr = 0.1
        
    return [time, x, y, h, xerr, yerr, herr]

