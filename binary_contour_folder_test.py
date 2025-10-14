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
tube_left = 200
tube_right = 616
min_radius = 100
max_radius = 1000
circularity_threshold = 0.5

ROI_top = 0 
ROI_bot = 2056 #2*max_radius
ROI_left = tube_left
ROI_right = tube_right


 
# Define the folder path correctly
folder = Path(r"C:\Users\User\OneDrive - The University of Manchester\DM UNI\YEAR 4\MPHYS SEM 1\test_codes\test_images_ball_in_tube")

# Dictionary to store images as NumPy arrays
images = {}
centre_arr = np.empty((0,2))

# Use glob for files in this folder only, or rglob for all subfolders
for img_path in folder.glob("*.tiff"):  
    img = cv2.imread(str(img_path))  # read as BGR NumPy array
    if img is not None:
        images[img_path.name] = img
        
            
        show_image(img, 'original image')
        
        # Convert to grayscale
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Reduce noise
        gray_blur = cv2.medianBlur(gray_image, 9)
        
        show_image(gray_blur, 'gray blur image')

        _, binary_inv = cv2.threshold(
            gray_image, 80, 255, cv2.THRESH_BINARY_INV)
        #show_image(binary_inv, 'Binary Threshold Inverted ')
        
        
        # # Copy the thresholded image.
        # im_floodfill = binary_inv.copy()
         
        # # Mask used to flood filling.
        # # Notice the size needs to be 2 pixels than the image.
        # h, w = binary_inv.shape[:2]
        # mask = np.zeros((h+2, w+2), np.uint8)
         
        # # Floodfill from point (0, 0)
        # cv2.floodFill(im_floodfill, mask, (0,0), 255);
         
        # # Invert floodfilled image
        # im_floodfill_inv = cv2.bitwise_not(im_floodfill)
         
        # # Combine the two images to get the foreground.
        # im_out = binary_inv | im_floodfill_inv
        
        
        # show_image(im_floodfill_inv, 'floodfill inv')
        # show_image(im_out, 'filled holes')
        
        
        image_copy = img.copy()
        
        ROI = binary_inv[ROI_top:ROI_bot, ROI_left:ROI_right]
        
        # Find contours
        contours, _ = cv2.findContours(ROI, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        output = cv2.cvtColor(binary_inv, cv2.COLOR_GRAY2BGR)
        
        for c in contours:
            # Shift contour coordinates to global frame
            c[:, :, 0] += ROI_left
            c[:, :, 1] += ROI_top 
    
            (x, y), radius = cv2.minEnclosingCircle(c)
            if radius < min_radius or radius > max_radius:
                continue
    
            area = cv2.contourArea(c)
            circle_area = np.pi * radius**2
            circularity = area / circle_area if circle_area > 0 else 0
    
            if circularity >= circularity_threshold:
                
                # adjust ROI to reduce search area
                ROI_bot = np.abs(int(radius) + int(y))
                
                # add circle centres to array
                centre_arr = np.vstack([centre_arr, [x, y]])
                
                centre = (int(x), int(y))
                radius = int(radius)
                print(f"Image: {img_path.name}")
                print(f"Centre = {centre}, Radius = {radius}, Circularity = {circularity:.2f}")
                
                
                '''
                cv2.circle(output, centre, radius, (0, 255, 0), 2)
                cv2.circle(output, centre, 2, (0, 0, 255), 3)
                cv2.imshow(f'Detected Circles - {img_path.name}', output)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                '''
                
                #plots image with circle on it
                fig, ax = plt.subplots()
                ax.imshow(output, cmap='gray')
                #ax.imshow(image_copy)
                ax.axvline(tube_left)
                ax.axvline(tube_right)
                ax.axis('off')
                circle = plt.Circle(centre, radius, color='red', fill=False, 
                                    linewidth=2)
                ax.add_patch(circle)
                plt.title("Circle Found")
                plt.show() 
                
                
print(f"\nLoaded {len(images)} images.")

