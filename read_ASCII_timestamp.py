#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 01:13:14 2025

@author: brunokeyworth
"""

import cv2
import numpy as np
import pickle
import os

with open('timestamp_templates.pkl', 'rb') as f:
    templates = pickle.load(f)
    
def match_template(digit):
    for key, template in templates.items():
        if np.array_equal(template, digit):
            return key
    return None  # or raise an error if no match

def get_microseconds(digits):
    hours = digits[0] * 10 + digits[1]
    minutes = digits[2] * 10 + digits[3]
    microseconds = (hours * 60 + minutes) * 60 * 10**6
    for i, digit in enumerate(reversed(digits[4:])):
        microseconds += digit * 10**i
        
    return microseconds

def get_timestamp(img):
    roi = img[:7, 172:292]
    digits = np.hsplit(roi, 15)
    # delete colons and deimal point (always in the same positions)
    for i in sorted([2, 5, 8], reverse=True):
        del digits[i]
    values = [match_template(digit) for digit in digits]
    return get_microseconds(values)

def sort_image(img_path, delete_original=True):
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    timestamp = get_timestamp(img)
    cropped_img = img[8:, :]

    output_folder, image_index = img_path.stem.split('_')
    save_as = f"{image_index}_{timestamp}.tif"
    
    output_folder = img_path.parent / output_folder
    output_folder.mkdir(exist_ok=True)
    
    # ---- Save cropped image ----
    save_path = output_folder / save_as
    cv2.imwrite(str(save_path), cropped_img)
    if delete_original:
        os.remove(img_path)
        
def sort_folder(folder_path):
    for filepath in folder_path.glob("*.tif"):
        sort_image(filepath)