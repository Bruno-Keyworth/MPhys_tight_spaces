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

import cv2
import numpy as np
import matplotlib.pyplot as plt

#constants
tube_left = 295
tube_right = 450
min_radius = 100
max_radius = 1000
circularity_threshold = 0.7
ruler_len = 9.7 #cm
pix_2_dist = ruler_len / 2056 # cm per pixel

ROI_top = 0 
ROI_bot = 2056 #2*max_radius
ROI_left = tube_left
ROI_right = tube_right

def show_image(img, title):
    plt.imshow(img, cmap='gray')
    plt.axvline(tube_left)
    plt.axvline(tube_right)
    plt.axhline(ROI_bot)
    plt.title(title)
    plt.axis('off')
    plt.show()    

def map_ball_path(folder, disp=False):   
    images = {}
    position_arr = np.empty((0,2))
    dec_array = np.empty(0)
    
    
    for img_path in folder.glob("*.tiff"):  
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        
        if img is not None:
            images[img_path.name] = img
            #show_image(img, 'original image')
            
            # Reduce noise
            #gray_blur = cv2.medianBlur(gray_image, 9)
            #show_image(gray_blur, 'gray blur image')

            #convert to binary using threshold intensity
            _, binary_inv = cv2.threshold(
                img, 80, 255, cv2.THRESH_BINARY_INV)
            #show_image(binary_inv, 'Binary Threshold Inverted ')
            
            # creates copy of original image
            image_copy = img.copy()
            
            # only searches this region for rectangles
            ROI = binary_inv[ROI_top:ROI_bot, ROI_left:ROI_right]
            
            # Find contours
            contours, _ = cv2.findContours(ROI, cv2.RETR_EXTERNAL, 
                                           cv2.CHAIN_APPROX_SIMPLE)
            
            for c in contours:
                # Shift contour coordinates to global frame
                c[:, :, 0] += ROI_left
                c[:, :, 1] += ROI_top 
        
                '''
                if radius < min_radius or radius > max_radius:
                    continue
                '''
                col,row,w,h = cv2.boundingRect(c)
                if w < min_radius and w > max_radius:
                    continue
                if  h > max_radius:
                    continue
                area = cv2.contourArea(c)
                x=col
                y= 2056 - row
                
                
                rect_area = w*h
                rectangularity = area / rect_area if rect_area > 0 else 0 
               
                
                # checks how rectangular the object is
                if rectangularity >= circularity_threshold:
                    
                    # add circle centres to array
                    position_arr = np.vstack([position_arr, [y, h]])
                    
                    file_name = img_path.name
                    hex_num = file_name.split("_")[1].split(".")[0]
                    dec_array = np.append(dec_array, [int(hex_num, 16)])
                    
                    centre = (int(x), int(y))
                    
                    
                    front_edge = y + h
                    print(f"Image: {img_path.name}")
                    print(f"Centre = {centre}, height = {h:.2f}, Rectangularity = {rectangularity:.2f}")
                    print(f"front edge = {front_edge:.2f} \n")
                    
                    if disp:
                        #plots image with circle on it
                        fig, ax = plt.subplots()
                        ax.imshow(image_copy, cmap='gray')
                        ax.axvline(tube_left)
                        ax.axvline(tube_right)
                        #ax.axis('off')
                        rect = plt.Rectangle((col,row), w,h, color='red', fill=False, 
                                            linewidth=2)
                        ax.add_patch(rect)
                        plt.title("Rectangle Found")
                        plt.show() 
                    
    
    #==========centre==correction==================================================
    height = np.max(position_arr[:,1])
    
    for i, row in enumerate(position_arr):
        if row[1] < height - 1:
            if row[0] < 1000:
                centre = row[0] - height +row[1]
                position_arr[i,0] = centre
            else:
                centre = row[0] + height - row[1]
                position_arr[i,0] = centre
    
    #=====UNIT=CONVERSION==========================================================
    position_arr *= pix_2_dist
    dec_array = dec_array-np.min(dec_array)
    dec_array*= (1/1000)
    return (dec_array, position_arr[:, 0])

