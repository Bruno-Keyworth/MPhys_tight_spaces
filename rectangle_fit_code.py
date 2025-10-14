# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 10:51:17 2025

@author: User
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 15:49:42 2025

@author: David Mawson
"""

from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_image(img, title):
    plt.imshow(img, cmap='gray')
    plt.axvline(tube_left)
    plt.axvline(tube_right)
    plt.axhline(ROI_bot)
    plt.title(title)
    plt.axis('off')
    plt.show()

#constants
iterator = 0
tube_left = 295
tube_right = 516
min_radius = 100
max_radius = 1000
circularity_threshold = 0.5

start = -20
end = -6

ROI_top = 0 
ROI_bot = 2056 #2*max_radius
ROI_left = tube_left
ROI_right = tube_right


folder = Path(r"C:\Users\User\OneDrive - The University of Manchester\DM UNI\YEAR 4\MPHYS SEM 1\test_codes\test_images_ball_in_tube")


images = {}
position_arr = np.empty((0,2))
dec_array = np.empty(0)


for img_path in folder.glob("*.tiff"):  
    img = cv2.imread(str(img_path))  # read as BGR NumPy array
    
    file_name = img_path.name
    hex_num = file_name.split("_")[1].split(".")[0]
    dec_array = np.append(dec_array, [int(hex_num, 16)])
    
    if img is not None:
        images[img_path.name] = img
        
            
        #show_image(img, 'original image')
        
        # Convert to grayscale
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Reduce noise
        gray_blur = cv2.medianBlur(gray_image, 9)
        
        #show_image(gray_blur, 'gray blur image')

        _, binary_inv = cv2.threshold(
            gray_image, 80, 255, cv2.THRESH_BINARY_INV)
        #show_image(binary_inv, 'Binary Threshold Inverted ')
        
        
        
        image_copy = img.copy()
        
        ROI = binary_inv[ROI_top:ROI_bot, ROI_left:ROI_right]
        
        # Find contours
        contours, _ = cv2.findContours(ROI, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        output = cv2.cvtColor(binary_inv, cv2.COLOR_GRAY2BGR)
        
        for c in contours:
            # Shift contour coordinates to global frame
            c[:, :, 0] += ROI_left
            c[:, :, 1] += ROI_top 
    
            '''
            (x, y), radius = cv2.minEnclosingCircle(c)
            if radius < min_radius or radius > max_radius:
                continue
            '''
            col,row,w,h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            x=col
            y= 2056 - row
            
            
            rect_area = w*h
            rectangularity = area / rect_area if rect_area > 0 else 0 
            '''
            circle_area = np.pi * radius**2
            circularity = area / circle_area if circle_area > 0 else 0
            '''
           
            
    
            if rectangularity >= circularity_threshold:
                
                # adjust ROI to reduce search area
                #ROI_bot = np.abs(int(radius) + int(y))
                
                # add circle centres to array
                position_arr = np.vstack([position_arr, [y, h]])
                
                centre = (int(x), int(y))
                
                
                front_edge = y + h
                #radius = int(radius)
                print(f"Image: {img_path.name}")
                print(f"Centre = {centre}, height = {h:.2f}, Rectangularity = {rectangularity:.2f}")
                print(f"front edge = {front_edge:.2f}")
                
                
                #plots image with circle on it
                fig, ax = plt.subplots()
                ax.imshow(output, cmap='gray')
                #ax.imshow(image_copy)
                ax.axvline(tube_left)
                ax.axvline(tube_right)
                #ax.axis('off')
                rect = plt.Rectangle((col,row), w,h, color='red', fill=False, 
                                    linewidth=2)
                ax.add_patch(rect)
                plt.title("Circle Found")
                plt.show() 

height = np.max(position_arr[:,1])

for i, row in enumerate(position_arr):
    if row[1] < height - 1:
        centre = row[0] - height +row[1]
        position_arr[i,0] = centre
        

pos_time_arr = np.dstack((position_arr[:,0], dec_array))
print(pos_time_arr)

plt.scatter(dec_array, position_arr[:,0])
plt.show()
                
                
print(f"\nLoaded {len(images)} images.")
