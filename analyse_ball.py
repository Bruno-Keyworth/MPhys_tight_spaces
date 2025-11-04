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
from make_dimensionless import make_dimensionless
import numpy as np
import os

BALL = 'ball3'   

def redo_pressure(ball, pressure, version=None):
    """
    Reruns the code to find position for images at a given pressure (in mbar), 
    then fits to find the speed. Updates the cached value for this pressure and
    repeats power law fitting. 
    """
    pressure *= 100
    folder = get_folder(ball, pressure)
    if version is None:
        speed_path = MASTER_FOLDER / ball / f'{pressure}mbar' / 'position_time.txt'
    else:
        speed_path = MASTER_FOLDER / ball / f'{pressure}mbar_{version}' / 'position_time{version}.txt'
    
    if speed_path.exists():
        os.remove(speed_path)

    file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    
    data, dimless_data = _update_data(folder, file_path)
    plot_ball_data(ball, data, version=(version or ''))
    plot_ball_data(ball, dimless_data, version = (version or '') + '_dimensionless')
    
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

def analyse_ball(ball, redo=False, version=None, plot=True):
    sort_folder(MASTER_FOLDER / ball)
    folders = get_folderpaths(ball, version)
    file_path = MASTER_FOLDER / ball / f'speed_pressure{version or ""}.txt'
    data_exists = _ensure_file_initialized(file_path, folders)
    if redo:
        for folder, _, _ in folders:
            speed_path = folder / 'position_time.txt'
            if speed_path.exists():
                os.remove(speed_path)
    if data_exists:
        data = np.genfromtxt(file_path)
        dimless_data = np.genfromtxt(file_path.parent / "dimensionless_data.txt")
    else:
        data, dimless_data = _update_data(folders, file_path)
        
    if plot:
        plot_ball_data(ball, data, version=(version or ''))
        plot_ball_data(ball, dimless_data, version = (version or '') + '_dimensionless')

def _update_data(folders, file_path):
    """
    Helper function
    """
    data = np.genfromtxt(file_path)
    
    for folder, pressure, error in folders:
        print(folder)
        speed, error = find_ball_speed(folder, True, True)

        data[data[:, 0]==pressure, 1] = speed
        data[data[:, 0]==pressure, 2] = error
        
    data[:, 0] -= 5800 * data[:, 1]

    dimensionless_data = make_dimensionless(data, ball=file_path.parent.name)
    np.savetxt(file_path, data)
    np.savetxt(file_path.parent / "dimensionless_data.txt", dimensionless_data)

    return data, dimensionless_data 

def redo(ball, version=None):
    """
    Refits to distance time graphs but uses the data cached for ball position in
    each photo.
    """
    if version is not None:
        file_path = MASTER_FOLDER / ball / f'speed_pressure_{version}.txt'
    else: 
        file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    analyse_ball(ball, version=version)

def redo_all(ball, version=None):
    """
    Completely reruns the code including finding the position of the ball in each image. 
    """
    if version is not None:
        file_path = MASTER_FOLDER / ball / f'speed_pressure_{version}.txt'
    else: 
        file_path = MASTER_FOLDER / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    analyse_ball(ball, redo=True, version=version)
    
def delete_empty(ball):
    """
    Deletes all photos in which a ball was not identified. Can be called manually
    after checking that images with the ball have not been deleted. This is not required 
    as the code will already ignore these images in future runs. 
    """
    folder = MASTER_FOLDER / ball
    
    for file_path in folder.rglob("*.tif"): 
        if file_path.name.startswith("empty_"):
            print(f"Deleting: {file_path}")
            file_path.unlink()
    
if __name__ == '__main__':
    analyse_ball(BALL)