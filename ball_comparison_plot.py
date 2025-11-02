# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 10:41:11 2025

@author: David Mawson
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER

#MASTER_FOLDER = r"D:\2025-26 MPhys Project\new_camera"


def ball_comparison():
    
    plt.figure(figsize=(8, 6))
    
    for folder_name in os.listdir(MASTER_FOLDER):
        folder_path = os.path.join(MASTER_FOLDER, folder_name)
        
        # Ensure it's a directory (e.g., "ball1", "ball2", ...)
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, "speed_pressure.txt")
            
            # Check if the text file exists
            if os.path.isfile(file_path):
                try:
                    data = np.genfromtxt(file_path, delimiter = ' ', 
                                         skip_header = False)
                    
                    # Plot data with label
                    plt.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], 
                                 yerr=data[:, 3], fmt='o',
                                 linestyle='-', markeredgecolor='black',
                                 markersize=4, elinewidth=0.8, markeredgewidth=0.5,
                                 label = folder_name)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    # Add labels and legend
    plt.xlabel("Speed, m/s")
    plt.ylabel("Pressure, Pa")
    plt.title("Speed vs Pressure for All Balls")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.yscale('log')
    plt.xscale('log')
    plt.savefig(MASTER_FOLDER / ('ball_comparison'), dpi=300)
    
    # Show the plot
    plt.show()

if __name__ == '__main__':
    ball_comparison()