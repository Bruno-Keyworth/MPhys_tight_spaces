#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 15:46:18 2025

@author: brunokeyworth
"""

import cv2
import numpy as np
from get_folderpaths import MASTER_FOLDER
import matplotlib.pyplot as plt
import os
import glob

def bcd_to_digits(bcd_byte):
    """Convert a single BCD byte to two decimal digits."""
    high = (bcd_byte >> 4) & 0xF
    low = bcd_byte & 0xF
    return high, low

def read_bcd_from_image(image_path, num_bcd=14):
    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError(f"Image not found: {image_path}")    # raw pixel values
    
    # Flatten to 1D array and take first num_bcd pixels
    flat_pixels = img.flatten()[:num_bcd]
    print(img.dtype, img.shape)  # see if it's uint8 or uint16
    print(flat_pixels[:20])  
    
    # Convert each BCD pixel to digits
    all_digits = []
    for pix in flat_pixels:
        all_digits.extend(bcd_to_digits(pix))
    
    # Return digits as a list
    return all_digits


def decode_bcd_timestamp(image_path):
    """
    Reads the first 16 pixels (8-bit) from the image and decodes:
    - Image number (integer)
    - Time as seconds since midnight (float, includes microseconds)
    """
    # Read grayscale image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image not found: {image_path}")

    # Extract first 16 pixels (flattened)
    first_pixels = img.flatten()[:16]

    # Convert each byte to 2 BCD digits
    digits = []
    for pix in first_pixels:
        high = (pix >> 4) & 0xF
        low = pix & 0xF
        digits.extend((high, low))

    # Extract fields
    image_number = int("".join(map(str, digits[0:7])))

    hour = int("".join(map(str, digits[15:17])))
    minute = int("".join(map(str, digits[17:19])))
    second = int("".join(map(str, digits[19:21])))
    microsecond = int("".join(map(str, digits[21:27])))

    # Convert time to seconds since midnight with microsecond precision
    time_in_seconds = hour * 3600 + minute * 60 + second + microsecond / 1_000_000

    return image_number, time_in_seconds


def process_folder(folder_path):
    """
    Loops through all .tif files in a folder and extracts
    image_number and time_in_seconds for each.
    """
    file_list = sorted(glob.glob(os.path.join(folder_path, "*.tif")))
    image_numbers = []
    times = []

    for file_path in file_list:
        img_num, time_sec = decode_bcd_timestamp(file_path)
        image_numbers.append(img_num)
        times.append(time_sec)

    return image_numbers, times


def plot_image_number_vs_time(image_numbers, times):
    """
    Plots image_number (y-axis) vs time_in_seconds (x-axis).
    """
    plt.figure()
    plt.scatter(times, image_numbers, marker='o')
    plt.xlabel("Time since midnight (s)")
    plt.ylabel("Image number")
    plt.title("Image Number vs Timestamp")
    plt.grid(True)
    plt.show()

# Example usage
folder_path = MASTER_FOLDER / "timestamp_test/binary"
numbers, times = process_folder(folder_path)
plot_image_number_vs_time(numbers, times)
