#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:05:12 2025

@author: brunokeyworth
"""

import os, socket
from pathlib import Path
import re
import numpy as np
from read_pressure_data import read_pressure_data

FLUID_DEPTH_ERROR = 0.01 #m
FLUID_DENSITY = { # kg/m^3
    "oil": [907, 45], # value, error
    "glycerol": [1261, 2]
    }
g = 9.81 #m/s^2

if socket.gethostname() == "Brunos-MacBook-Air-2.local":
    if os.path.exists("/Volumes/Transcend/"):
        MASTER_FOLDER = Path("/Volumes/Transcend/2025-26 MPhys Project") / 'new_camera'
    else:
        MASTER_FOLDER = Path("/Users/brunokeyworth/Desktop/MPhys/2025-26 MPhys Project") / 'new_camera'
else:
    MASTER_FOLDER = Path(r"D:\2025-26 MPhys Project") / 'new_camera' 
    
def _hydrostatic_err(fluid):
    if fluid is None: 
        fluid = 'oil'
    return g * FLUID_DEPTH_ERROR * FLUID_DENSITY[fluid][0]

def get_folder(ball, pressure, fluid=None, method=None):
    folder = MASTER_FOLDER / (fluid or "") / (method or "") / ball / f'{int(pressure/100)}mbar'
    data_dict = read_pressure_data(MASTER_FOLDER / ball)
    if data_dict is not None:
        values = data_dict[pressure]
    else:
        values = [pressure, 0]
    return [(folder, values[0], np.sqrt(values[1]**2 + _hydrostatic_err(fluid)**2))]

def get_folderpaths(ball, version=None, fluid=None, method=None):
    # Determine master folder

    base_path = MASTER_FOLDER / (fluid or "") / (method or "") / ball
    
    data_dict = read_pressure_data(base_path)

    # Regex: capture the number before "mbar"
    pattern = re.compile(r"^(\d+)mbar$")

    # List all subdirectories matching the pattern
    subdirs = []
    for p in base_path.iterdir():
        if p.is_dir():
            m = pattern.match(p.name)
            if m and any(p.iterdir()):
                number = int(m.group(1)) * 100
                if data_dict is None:
                    subdirs.append((p, number, _hydrostatic_err(fluid)))
                else:
                    values = data_dict[number]
                    error = np.sqrt(values[1]**2 + _hydrostatic_err(fluid)**2)
                    subdirs.append((p, values[0], error))

    # Sort by pressure number (optional)
    subdirs.sort(key=lambda x: x[1])

    # If version is provided, attempt to substitute folders
    if version is not None:
        updated_subdirs = []
        for p, number in subdirs:
            new_path = base_path / f"{number}mbar_{version}"
            if new_path.is_dir() and any(new_path.iterdir()):
                updated_subdirs.append((new_path, number))
            else:
                updated_subdirs.append((p, number))
        return updated_subdirs

    return subdirs

def get_folder_dict(folders):
    for fluid in folders.keys():
        for method in folders[fluid].keys():
            folders[fluid][method] = sorted(folders[fluid][method])

    return {
        "oil no-hold": [MASTER_FOLDER / "oil" / 'no-hold' / folder for folder in folders["oil"]["no-hold"]],
        "oil hold": [MASTER_FOLDER / "oil" / 'hold' / folder for folder in folders["oil"]["hold"]],
        "glycerol no-hold": [MASTER_FOLDER / "glycerol" / 'no-hold' / folder for folder in folders["glycerol"]["no-hold"]],
        "glycerol hold": [MASTER_FOLDER / "glycerol" / 'hold' / folder for folder in folders["glycerol"]["hold"]],
        }
    
    