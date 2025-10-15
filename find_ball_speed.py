#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:20:26 2025

@author: brunokeyworth
"""

from rectangle_fit_code import map_ball_path
import matplotlib.pyplot as plt
import numpy as np

def find_ball_speed(folder, disp=False, savefig=False):
    print(folder)
    
    time, position = map_ball_path(folder, disp)
    
    coef = np.polyfit(time, position, 1) #w=weights
    if disp:
        print("Coefficients:", coef)
        
        x_fit = np.linspace(0, np.max(time), 2)
        y_fit = coef[0] * x_fit + coef[1]
        
        fig, ax1 = plt.subplots()
        ax1.scatter(time, position)
        ax1.plot(x_fit, y_fit, label = f"y = {coef[0]:.2f}x + {coef[1]:.2f}")
        ax1.set_ylabel("distance (cm)")
        ax1.set_xlabel("time (s)")
        ax1.legend()
        ax1.grid()
        if savefig:
            plt.savefig(folder / 'position_time.png' , dpi=300)
        plt.show()
        
    return coef[0]
        