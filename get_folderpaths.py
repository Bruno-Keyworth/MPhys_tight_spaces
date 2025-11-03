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

HYDROSTATIC_ERROR = 100 #Pa

if socket.gethostname() == "Brunos-MacBook-Air-2.local":
    if os.path.exists("/Volumes/Transcend/"):
        MASTER_FOLDER = Path("/Volumes/Transcend/2025-26 MPhys Project") / 'new_camera'
    else:
        MASTER_FOLDER = Path("/Users/brunokeyworth/Desktop/MPhys/2025-26 MPhys Project") / 'new_camera'
else:
    MASTER_FOLDER = Path(r"D:\2025-26 MPhys Project") / 'new_camera'
    
def get_folder(ball, pressure):
    folder = MASTER_FOLDER / ball / f'{int(pressure/100)}mbar'
    data_dict = read_pressure_data(MASTER_FOLDER / ball)
    if data_dict is not None:
        values = data_dict[pressure]
    else:
        values = [pressure, HYDROSTATIC_ERROR]
    return [(folder, values[0], np.sqrt(values[1]**2 + HYDROSTATIC_ERROR**2))]

def get_folderpaths(ball, version=None):
    # Determine master folder

    base_path = MASTER_FOLDER / ball
    
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
                    subdirs.append((p, number, HYDROSTATIC_ERROR))
                else:
                    values = data_dict[number]
                    error = np.sqrt(values[1]**2 + HYDROSTATIC_ERROR**2)
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