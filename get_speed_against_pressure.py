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

PRESSURE_ERROR = np.sqrt(0.2**2 +0.3**2)

BALL = 'ball4_retake'   

def redo_pressure(ball, pressure):

    folder = get_folder(ball, pressure)

    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    
    data = update_ball_data([(folder, pressure)], file_path)
    plot_ball_data(ball, data)

def get_ball_data(ball):

    data = np.empty((0, 3))
    folders = get_folderpaths(ball)

    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if file_path.exists():
        return np.genfromtxt(file_path)
    else:
        pressures = np.array([f[1] for f in folders])
        data = np.column_stack((pressures, np.full(len(pressures), np.nan), 
                                np.full(len(pressures), np.nan)))
        np.savetxt(file_path, data)   
    
    return update_ball_data(folders, file_path)

def update_ball_data(folders, file_path):
    
    data = np.genfromtxt(file_path)
    
    for folder, pressure in folders:
        print(folder)
        speed, error = find_ball_speed(folder, True)

        data[data[:, 0]==pressure, 1] = speed
        data[data[:, 0]==pressure, 2] = error

    np.savetxt(file_path, data)

    return data  

def plot_ball_data(ball, data=None):
    
    if data is None:
        data = get_ball_data(ball)

    fig, ax = plt.subplots()
    ax.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], yerr=PRESSURE_ERROR, ls='', marker='.')
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel('Pressure (mbar)')
    ax.set_xlabel('Speed (cm/s)')
    
    plt.savefig(MASTER_FOLDER / ball / 'speed_pressure.png', dpi=300)
    plt.show()

def redo_all(ball):
    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    plot_ball_data(ball)
    
if __name__ == '__main__':
    plot_ball_data(BALL)