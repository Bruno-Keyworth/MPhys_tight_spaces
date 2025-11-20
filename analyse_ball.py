#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:47:55 2025

@author: brunokeyworth
"""

from get_folderpaths import get_folderpaths, MASTER_FOLDER, get_folder, _ball_folder
from find_ball_speed import find_ball_speed
from get_fit_params import get_fit_params, plot_ball_data
from read_ASCII_timestamp import sort_folder
from make_dimensionless import make_dimensionless
import numpy as np
import os
import argparse

FLUID = 'glycerol'
METHOD = 'no-hold'
BALL = 'ball3'   

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f"Will analyse image data stored at fluid/method/ball inside\
 {MASTER_FOLDER} and fit power law."
    )
    parser.add_argument(
        "--fluid",
        default = FLUID,
        type=str,
        choices=('oil', 'glycerol'),
        help=f"The name of the fluid folder the data is stored in. Default is {FLUID}.",
    )
    parser.add_argument(
        "--method",
        default = METHOD,
        type=str,
        choices=('hold', 'no-hold'),
        help=f"The name of the method folder the data is stored in. Default is {METHOD}.",
    )
    parser.add_argument(
        "--ball",
        default = BALL,
        type=str,
        help=f"The name of the ball folder the data is stored in. Default is {BALL}.",
    )
    parser.add_argument(
        "--redo",
        action='store_true',
        help="If given, the speed fitting will be reperformed for each pressure:" +
            "the fitting for position in each photo will not be redone.",
    )
    parser.add_argument(
        "--redo_all",
        action='store_true',
        help="If given, the fitting for the position in each photo will be redone.",
    )
    parser.add_argument(
        "--delete_empty",
        action='store_true',
        help="If given, the photos in which the code could not identify a ball will be deleted.",
    )
    return parser.parse_args()

def redo_pressure(ball, pressure, version=None, fluid=FLUID, method=METHOD):
    """
    Reruns the code to find position for images at a given pressure (in mbar), 
    then fits to find the speed. Updates the cached value for this pressure and
    repeats power law fitting. 
    """
    ball_folder = _ball_folder(ball, fluid=fluid, method=method)
    if version is None:
        speed_path = ball_folder / f'{pressure}mbar' / 'position_time.txt'
    else:
        speed_path = ball_folder / f'{pressure}mbar_{version}' / 'position_time{version}.txt'
    pressure *= 100
    folder = get_folder(ball, pressure, fluid=fluid, method=METHOD)
    if speed_path.exists():
        os.remove(speed_path)

    file_path = ball_folder / 'speed_pressure.txt'
    
    _update_data(folder, file_path)
    get_fit_params(ball_folder, plot=True)

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

def analyse_ball(ball, redo=False, version=None, plot=True, fluid=FLUID, method=METHOD):
    ball_folder = _ball_folder(ball, fluid=fluid, method=method)
    sort_folder(ball_folder)
    folders = get_folderpaths(ball, version, fluid=fluid, method=method)
    file_path = ball_folder / f'speed_pressure{version or ""}.txt'
    data_exists = _ensure_file_initialized(file_path, folders)
    if redo:
        for folder, _, _ in folders:
            speed_path = folder / 'position_time.txt'
            if speed_path.exists():
                os.remove(speed_path)
    if not data_exists:
        _update_data(folders, file_path)
    if redo:
        get_fit_params(ball_folder, plot=plot)
    if plot:
        plot_ball_data(ball_folder)

def _update_data(folders, file_path):
    """
    Helper function
    """
    data = np.genfromtxt(file_path)
    
    for folder, pressure, error in reversed(folders):
        print(folder)
        speed, error = find_ball_speed(folder, True, True)

        data[data[:, 0]==pressure, 1] = speed
        data[data[:, 0]==pressure, 2] = error

    dimensionless_data = make_dimensionless(data, file_path)
    np.savetxt(file_path, data)
    np.savetxt(file_path.parent / "dimensionless_data.txt", dimensionless_data)

    return data, dimensionless_data 

def redo(ball, version=None, fluid=FLUID, method=METHOD):
    """
    Refits to distance time graphs but uses the data cached for ball position in
    each photo.
    """
    if version is not None:
        file_path = MASTER_FOLDER / (fluid or "") / (method or "") / ball / f'speed_pressure_{version}.txt'
    else: 
        file_path = MASTER_FOLDER / (fluid or "") / (method or "") / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    analyse_ball(ball, version=version)

def redo_all(ball, version=None, fluid=FLUID, method=METHOD):
    """
    Completely reruns the code including finding the position of the ball in each image. 
    """
    if version is not None:
        file_path = MASTER_FOLDER / (fluid or "") / (method or "") / ball / f'speed_pressure_{version}.txt'
    else: 
        file_path = MASTER_FOLDER / (fluid or "") / (method or "") / ball / 'speed_pressure.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    analyse_ball(ball, redo=True, version=version)
    
def delete_empty(ball=BALL, fluid=FLUID, method=METHOD):
    """
    Deletes all photos in which a ball was not identified. Can be called manually
    after checking that images with the ball have not been deleted. This is not required 
    as the code will already ignore these images in future runs. 
    """
    folder = MASTER_FOLDER / fluid / method / ball
    
    for file_path in folder.rglob("*.tif"): 
        if file_path.name.startswith("empty_"):
            print(f"Deleting: {file_path}")
            file_path.unlink()
    
if __name__ == '__main__':
    args = parse_arguments()
    if args.redo_all:
        redo_all(args.ball, fluid=args.fluid, method=args.method)
    elif args.redo:
        redo(args.ball, fluid=args.fluid, method=args.method)
    else:
        analyse_ball(ball=args.ball, fluid=args.fluid, method=args.method)
    if args.delete_empty:
        delete_empty(ball=args.ball, fluid=args.fluid, method=args.method)