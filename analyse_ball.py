#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:47:55 2025

@author: brunokeyworth
"""

from get_folderpaths import get_folderpaths, MASTER_FOLDER, get_folder
from find_ball_speed import find_ball_speed
from plot_ball_data import plot_ball_data
from read_ASCII_timestamp import sort_folder
import numpy as np
import os

BALL = 'ball1'   

def redo_pressure(ball, pressure, version=None):

    folder = get_folder(ball, pressure)
    if version is None:
        speed_path = MASTER_FOLDER / ball / f'{pressure}mbar' / 'position_time.txt'
    else:
        speed_path = MASTER_FOLDER / ball / f'{pressure}mbar_{version}' / 'position_time.txt'
    
    if speed_path.exists():
        os.remove(speed_path)

    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    
    data = update_ball_data([(folder, pressure)], file_path)
    plot_ball_data(ball, data, version=version)
    
def _ensure_file_initialized(file_path, folders):
    if not file_path.exists():
        pressures = np.array([f[1] for f in folders])
        pressure_err = np.array([f[2] for f in folders])
        data = np.column_stack((pressures,
                                np.full(len(pressures), np.nan),
                                np.full(len(pressures), np.nan), pressure_err))
        np.savetxt(file_path, data)
        return False
    return True

def analyse_ball(ball, redo=False, version=None):
    sort_folder(MASTER_FOLDER / ball)
    folders = get_folderpaths(ball, version)
    if version is not None:
        file_path = MASTER_FOLDER / ball / f'speed_pressure_{version}.txt'
    else: 
        file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    data_exists = _ensure_file_initialized(file_path, folders)
    if redo:
        for folder, _, _ in folders:
            speed_path = folder / 'position_time.txt'
            if speed_path.exists():
                os.remove(speed_path)
    if data_exists:
        data = np.genfromtxt(file_path)
    else:
        data = update_ball_data(folders, file_path)
        
    plot_ball_data(ball, data, version=version)

def update_ball_data(folders, file_path):
    
    data = np.genfromtxt(file_path)
    
    for folder, pressure, error in folders:
        print(folder)
        speed, error = find_ball_speed(folder, True, True)

        data[data[:, 0]==pressure, 1] = speed
        data[data[:, 0]==pressure, 2] = error

    np.savetxt(file_path, data)

    return data  

def redo(ball, version=None):
    if version is not None:
        file_path = MASTER_FOLDER / ball / f'speed_pressure_{version}.txt'
    else: 
        file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    analyse_ball(ball, version=version)

def redo_all(ball, version=None):
    if version is not None:
        file_path = MASTER_FOLDER / ball / f'speed_pressure_{version}.txt'
    else: 
        file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    analyse_ball(ball, redo=True, version=version)
    
if __name__ == '__main__':
    analyse_ball(BALL)