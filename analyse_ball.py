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
from get_preset import*
import numpy as np
import os
import argparse
from matplotlib.pyplot import close

FLUID = 'glycerol'
METHOD = 'hold'
BALL = 'ball1_repeat'   

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
    parser.add_argument(
        "--all_balls",
        action='store_true',
        help="If given, the code will run for all balls listed in get_preset.py.",
    )
    return parser.parse_args()

def redo_pressure(ball, pressure_mbar, fluid=FLUID, method=METHOD):
    """
    Reruns the code to find position for images at a given pressure (in mbar), 
    then fits to find the speed. Updates the cached value for this pressure and
    repeats power law fitting. 
    """
    ball_folder = _ball_folder(ball, fluid=fluid, method=method)
    speed_path = ball_folder / f'{pressure_mbar}mbar' / 'position_time.txt'
    pressure_pa = pressure_mbar * 100
    folder = get_folder(ball, pressure_pa, fluid=fluid, method=method)
    if speed_path.exists():
        os.remove(speed_path)

    file_path = ball_folder / 'speed_pressure.txt'
    
    _update_data(folder, file_path)
    get_fit_params(ball_folder, plot=False)

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

def analyse_ball(ball, redo=False, redo_fit=False, plot=True, fluid=FLUID, method=METHOD):
    ball_folder = _ball_folder(ball, fluid=fluid, method=method)
    if not ball_folder.exists():
        print(f'Folder Not Found: {ball_folder}')
        return 0
        #raise FileNotFoundError(f"Ball folder does not exist: {ball_folder}")
    sort_folder(ball_folder)
    folders = get_folderpaths(ball, fluid=fluid, method=method)
    file_path = ball_folder / 'speed_pressure.txt'
    data_exists = _ensure_file_initialized(file_path, folders)
    if redo:
        for folder, _, _ in folders:
            speed_path = folder / 'position_time.txt'
            if speed_path.exists():
                os.remove(speed_path)
    if not data_exists:
        _update_data(folders, file_path)
    if redo_fit or (not (ball_folder/"fit_params.txt").exists()):
        get_fit_params(ball_folder, plot=plot)
    if plot:
        plot_ball_data(ball_folder)

def _update_data(folders, file_path):
    """
    Helper function
    """
    data = np.genfromtxt(file_path)
    
    for folder, pressure, _ in folders:
        print(folder)
        speed, error = find_ball_speed(folder, True, True)
        mask = np.isclose(data[:, 0], pressure)

        data[mask, 1] = speed
        data[mask, 2] = error

    dimensionless_data = make_dimensionless(data, file_path)
    np.savetxt(file_path, data)
    np.savetxt(file_path.parent / "dimensionless_data.txt", dimensionless_data)

    return data, dimensionless_data 

def _delete_data_file(ball, fluid, method):
    fname = "speed_pressure.txt"

    path = _ball_folder(ball, fluid, method) / fname
    if os.path.exists(path):
        os.remove(path)

def redo(ball, fluid=FLUID, method=METHOD, plot=True):
    """ 
    Refits to distance time graphs but uses the data cached for ball position in each photo.
    """
    _delete_data_file(ball, fluid, method)
    analyse_ball(ball, plot=plot, redo_fit=True)


def redo_all(ball, fluid=FLUID, method=METHOD, plot=True):
    """
    Completely reruns the code including finding the position of the ball in each image.
    """
    _delete_data_file(ball, fluid, method)
    analyse_ball(ball, redo=True, plot=plot, redo_fit=True)
    
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
    if args.all_balls:
        for ball in all_balls:
            redo(ball['name'], fluid=ball['fluid'], method=ball['method'])
            analyse_ball(ball['name'], fluid=ball['fluid'], method=ball['method'])
    elif args.redo_all:
        redo_all(args.ball, fluid=args.fluid, method=args.method)
    elif args.redo:
        redo(args.ball, fluid=args.fluid, method=args.method)
        analyse_ball(ball=args.ball, fluid=args.fluid, method=args.method)
    else:
        analyse_ball(ball=args.ball, fluid=args.fluid, method=args.method)
    if args.delete_empty:
        delete_empty(ball=args.ball, fluid=args.fluid, method=args.method)
    close('all')
