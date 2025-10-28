#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:05:12 2025

@author: brunokeyworth
"""

import os, socket
from pathlib import Path
import re

if socket.gethostname() == "Brunos-MacBook-Air-2.local":
    if os.path.exists("/Volumes/Transcend/"):
        MASTER_FOLDER = Path("/Volumes/Transcend/2025-26 MPhys Project") / 'new_camera'
    else:
        MASTER_FOLDER = Path("/Users/brunokeyworth/Desktop/MPhys/2025-26 MPhys Project") / 'new_camera'
else:
    MASTER_FOLDER = Path(r"D:\2025-26 MPhys Project") / 'new_camera'
    
def get_folder(ball, pressure):
    return MASTER_FOLDER / ball / f'{pressure}mbar'

def get_folderpaths(ball, version=None):
    # Determine master folder

    base_path = MASTER_FOLDER / ball

    # Regex: capture the number before "mbar"
    pattern = re.compile(r"^(\d+)mbar$")

    # List all subdirectories matching the pattern
    subdirs = []
    for p in base_path.iterdir():
        if p.is_dir():
            m = pattern.match(p.name)
            if m and any(p.iterdir()):
                number = int(m.group(1))
                subdirs.append((p, number))

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
        subdirs = updated_subdirs

    return subdirs