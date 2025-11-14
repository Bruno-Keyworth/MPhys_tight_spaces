# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 12:17:15 2025

@author: User
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_image(img, title, left, right):
    plt.imshow(img, cmap='gray')
    plt.axvline(left)
    plt.axvline(right)
    plt.title(title)
    plt.axis('off')
    plt.show()    

def calc_tube_left_right(img):
    
    cropping = int(len(img[0, :])/4)
    img = img[:, cropping:-cropping]
    gray_blur = cv2.medianBlur(img, 9)
    gray_blur = cv2.medianBlur(gray_blur, 9)
    #show_image(gray_blur, 'gray blur image')
    #show_image(gray_blur, "", 0, 0)

    #convert to binary using threshold intensity
    _, binary_inv = cv2.threshold(
        gray_blur, 110, 255, cv2.THRESH_BINARY_INV)
    
    #show_image(binary_inv, "", 0, 0)
    
    
    binary = binary_inv > 0  
    
    ys, xs = np.where(binary)
    if xs.size == 0:
        return cropping, 3*cropping
        #raise ValueError("No tube edges found — check image contrast, ROI, or threshold settings.")

    leftmost_x = np.min(xs) + cropping
    rightmost_x = np.max(xs) + cropping
    
    return leftmost_x, rightmost_x