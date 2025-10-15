#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:47:55 2025

@author: brunokeyworth
"""

from get_folderpaths import get_folderpaths, MASTER_FOLDER
from find_ball_speed import find_ball_speed
import numpy as np
import matplotlib.pyplot as plt

ball = 'ball3'

def get_ball_data(ball):
    
    data = np.empty((0, 2))
    folders = get_folderpaths(ball)
    
    for folder, pressure in folders:
        
        speed = find_ball_speed(folder)
        data = np.vstack((data, np.array([pressure, speed])))
        
    return data

def plot_ball_data(ball):
    
    data = get_ball_data(ball)
    
    fig, ax = plt.subplots()
    ax.scatter(data[:, 0], data[:, 1])
    
    plt.savefig(MASTER_FOLDER / ball / 'speed_pressure.png', dpi=300)
    
    plt.show()
    
if __name__ == '__main__':
    plot_ball_data(ball)