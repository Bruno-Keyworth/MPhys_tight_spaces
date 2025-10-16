#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:47:55 2025

@author: brunokeyworth
"""

from get_folderpaths import get_folderpaths, MASTER_FOLDER, get_folder
from find_ball_speed import find_ball_speed
import numpy as np
import matplotlib.pyplot as plt
import os

ball = 'ball4_retake'      

def get_ball_data(ball):
    
    data = np.empty((0, 2))
    folders = get_folderpaths(ball)
    
    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if file_path.exists():
        data = np.genfromtxt(file_path)
    else:
        for folder, pressure in folders:
            
            speed = find_ball_speed(folder)
            data = np.vstack((data, np.array([pressure, speed])))
        
        np.savetxt(file_path, data)
        
    return data

def redo_pressure(ball, pressure):
    
    folder = get_folder(ball, pressure)
    
    speed = find_ball_speed(folder, True)
    
    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    
    data = np.genfromtxt(file_path)
    
    data[data[:, 0]==pressure, 1] = speed
    
    np.savetxt(file_path, data)

def plot_ball_data(ball):
    
    data = get_ball_data(ball)
    
    y = np.linspace(200, 1000, 100)
    
    x = 2.2*y**0.5
    
    fig, ax = plt.subplots()
    ax.scatter(data[:, 1], data[:, 0])
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel('Pressure (mbar)')
    ax.set_xlabel('Speed (cm/s)')
    ax.plot(x, y)
    plt.savefig(MASTER_FOLDER / ball / 'speed_pressure.png', dpi=300)
    plt.show()
    
def redo_all(ball):
    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)
    
    plot_ball_data(ball)
    
if __name__ == '__main__':
    plot_ball_data(ball)