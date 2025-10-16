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
    
    cropping = 150
    img = img[:, cropping:-cropping]
    gray_blur = cv2.medianBlur(img, 9)
    gray_blur = cv2.medianBlur(gray_blur, 9)
    #show_image(gray_blur, 'gray blur image')
    #show_image(gray_blur, "", 0, 0)

    #convert to binary using threshold intensity
    _, binary_inv = cv2.threshold(
        gray_blur, 160, 255, cv2.THRESH_BINARY_INV)
    
    #show_image(binary_inv, "", 0, 0)
    
    
    binary = binary_inv > 0  
    
    ys, xs = np.where(binary)
    if xs.size == 0:
        raise ValueError("No tube edges found — check image contrast, ROI, or threshold settings.")

    leftmost_x = np.min(xs) + cropping
    rightmost_x = np.max(xs) + cropping
    
    return leftmost_x, rightmost_x



# # Define the folder path correctly
# folder = Path(r"C:\Users\User\OneDrive - The University of Manchester\DM UNI\YEAR 4\MPHYS SEM 1\test_codes\test_images_ball_in_tube")

# # Dictionary to store images as NumPy arrays
# images = {}
# centre_arr = np.empty((0,2))

# # Use glob for files in this folder only, or rglob for all subfolders
# for img_path in folder.glob("*.tiff"):  
#     img = cv2.imread(str(img_path))  # read as BGR NumPy array
#     if img is not None:
#         images[img_path.name] = img
        
#         # Convert to grayscale
#         gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#         tube_left, tube_right = calc_tube_left_right(gray_image)
#         show_image(img, "tube boundary", tube_left, tube_right)
    