#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 14:35:41 2025

@author: brunokeyworth
"""

import numpy as np
from constants import FRAME_SIZE
import cv2
from get_folderpaths import get_folderpaths, ball_folder
import matplotlib.pyplot as plt
import itertools
from make_dimensionless import _get_delta

colors = itertools.cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

def _get_radius(ROI, label, plot=False):
    
    profile = ROI.mean(axis=0)
    profile /= max(profile)
    
    average = np.mean(profile)
    minimum = np.min(profile)
    mask = profile > minimum + 0.05 * (average - minimum)
    # Find the indices where mask is False
    false_indices = np.where(~mask)[0]
    
    # Split into consecutive groups
    groups = np.split(false_indices, np.where(np.diff(false_indices) != 1)[0] + 1)
    
    # Remove empty groups (can happen if mask has no False values)
    groups = [g for g in groups if g.size > 0]
    
    if len(groups) != 2:
        return None
    
    radius = 0.5 * (np.mean(groups[1]) - np.mean(groups[0]))
    if plot: 
        color = next(colors)
        plt.axvline(np.mean(groups[0]), ls='dashed', color=color)
        plt.axvline(np.mean(groups[1]), ls='dashed', color=color)
        plt.scatter(np.arange(len(profile)), profile, label=label, s=5)
    
    return radius

def _plot_title(img_path):
    pressure = img_path.parent
    ball = pressure.parent
    method = ball.parent
    fluid = method.parent
    
    return f'{fluid.name} {method.name} {ball.name} {pressure.name}'

def _get_swelling(img_path, x, plot=False):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    m_to_pixel = len(img) / FRAME_SIZE
    lower_edge = int((x - 0.02) * m_to_pixel)
    upper_edge = int((x + 0.02) * m_to_pixel)
    width = len(img[0, :])
    ROI_high_pressure = img[:lower_edge, int(0.3*width):int(0.7*width)]
    ROI_low_pressure = img[upper_edge:, int(0.3*width):int(0.7*width)]
    r_0 = _get_radius(ROI_low_pressure, label='Low Pressure', plot=plot)
    r = _get_radius(ROI_high_pressure, label='High Pressure', plot=plot)
    if (r_0 is None) or (r is None) or (r < r_0):
        return None
    if plot:
        plt.title(_plot_title(img_path) + f': Swelling = {r/r_0:.2g}')
        plt.xlabel('width (pixels)')
        plt.ylabel('relative intensity')
        plt.legend()
        plt.savefig(img_path.parent / 'swelling_plot.png', dpi=300)
        plt.show()
    return (r - r_0)
    
def _sample_paths(paths, positions, n=10):
    """Return up to n evenly spaced Path objects from a list."""
    if len(paths) <= n:
        return [[paths[i], positions[i]] for i in range(len(paths))]
    idx = np.linspace(0, len(paths) - 1, n).astype(int).tolist()
    return [[paths[i], positions[i]] for i in idx]

def average_swelling(pressure_folder, plot=False, n=10):
    positions = np.genfromtxt(pressure_folder / 'position_time.txt', usecols=(1))
    paths = sorted([
        f for f in pressure_folder.glob("*.tif") 
        if "empty" not in f.name.lower() 
        and not f.name.startswith("._")
    ])
    mask = (positions < 0.05) | ((FRAME_SIZE - positions) < 0.05)

    positions = positions[~mask]
    paths = np.array(paths)[~mask]
    
    photos = _sample_paths(paths, positions, n=n)
    
    swellings = []
    
    for photo, position in photos:
        swelling = _get_swelling(photo, position, plot=plot)
        if swelling is None:
            continue
        swellings.append(swelling)
    if not swellings:
        return None, None
    
    average = np.mean(swellings)
    error = np.std(swellings)
    
    delta, delta_err = _get_delta(pressure_folder.parent.name.split('_')[0])
    
    dimless_swelling = average/(2 * delta)
    dimless_err = dimless_swelling * np.sqrt((error/average)**2 + (delta_err/delta)**2)
    return dimless_swelling, dimless_err

def analyse_swelling(ball, fluid='glycerol', method='no-hold'):
    
    folders = get_folderpaths(ball, fluid=fluid, method=method)
    
    data = np.empty((len(folders), 4))
    count = 0
    
    for folder, P, P_err in folders:
        swelling, swelling_err = average_swelling(folder)
        if swelling is None:
            continue
        data[count] = [P, P_err, swelling, swelling_err]
        count += 1
        
    data = data[:count] 
    
    np.savetxt(ball_folder(ball, fluid, method) / 'swelling_data.txt', data)
    
def plot_swelling(ball, fluid='glycerol', method='no-hold', redo=True):
    file_path = ball_folder(ball, fluid, method) / 'swelling_data.txt'
    if (not file_path.exists()) or redo:
        analyse_swelling(ball, fluid, method)
    
    data = np.genfromtxt(file_path)
    
    plt.errorbar(data[:, 0], data[:, 2], xerr=data[:, 1], yerr=data[:, 3], ls='')
    #plt.yscale('log')
    #plt.xscale('log')
    plt.xlim(10000, 60000)
    
if __name__ == '__main__':
    plot_swelling('ball1')
    plot_swelling('ball2')
    plot_swelling('ball3')
    plot_swelling('ball4')
    plot_swelling('ball5')