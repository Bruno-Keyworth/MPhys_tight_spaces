#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 14:35:41 2025

@author: brunokeyworth
"""

import numpy as np
from constants import FRAME_SIZE
import cv2
from get_folderpaths import get_folderpaths, _ball_folder, MASTER_FOLDER
import matplotlib.pyplot as plt
from make_dimensionless import _get_delta
import matplotlib.colors as mcolors
from itertools import cycle


# Define linestyles and markers
linestyles = cycle(['-', '--', '-.', ':'])
markers = cycle(['o', 's', 'x', '^', 'v', '*', 'D', 'P'])


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
        return None, None
    if plot:
        plt.title(_plot_title(img_path) + f': Swelling = {r/r_0:.2g}')
        plt.xlabel('width (pixels)')
        plt.ylabel('relative intensity')
        plt.legend()
        plt.savefig(img_path.parent / 'swelling_plot.png', dpi=300)
        plt.show()
    return (r - r_0)/m_to_pixel, r/r_0
    
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
    
    swelling_ratio = []
    swelling_diff = []
    
    for photo, position in photos:
        diff, ratio = _get_swelling(photo, position, plot=plot)
        if diff is None:
            continue
        swelling_ratio.append(ratio)
        swelling_diff.append(diff)
    if not swelling_diff:
        return None, None, None, None
    
    ratio_av= np.mean(swelling_ratio)
    ratio_err = np.std(swelling_ratio)
    diff_av= np.mean(swelling_diff)
    diff_err = np.std(swelling_diff)
    
    delta, delta_err = _get_delta(pressure_folder.parent.name.split('_')[0])
    
    dimless_diff = diff_av/(2 * delta)
        
    valid = (diff_av != 0) & (delta != 0) & ~np.isnan(diff_av) & ~np.isnan(delta)
    dimless_err = np.full_like(dimless_diff, np.nan)
    dimless_err[valid] = (
    dimless_diff[valid] *
    np.sqrt((diff_err[valid]/diff_av[valid])**2 + (delta_err[valid]/delta[valid])**2)
    )

    return dimless_diff, dimless_err, ratio_av, ratio_err

def analyse_swelling(ball, fluid='glycerol', method='no-hold'):
    
    folders = get_folderpaths(ball, fluid=fluid, method=method)

    data = np.empty((len(folders), 6))
    count = 0
    
    for folder, P, P_err in folders:
        diff, diff_err, ratio, ratio_err = average_swelling(folder)
        if diff is None:
            continue
        data[count] = [P, P_err, diff, diff_err, ratio, ratio_err]
        count += 1
        
    data = data[:count] 
    
    np.savetxt(_ball_folder(ball, fluid, method) / 'swelling_data.txt', data)
    
def plot_swelling(balls, fluid='glycerol', method='no-hold', redo=False):
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for ball in balls:
        file_path = _ball_folder(ball, fluid, method) / 'swelling_data.txt'
        if (not file_path.exists()) or redo:
            analyse_swelling(ball, fluid, method)

        data = np.genfromtxt(file_path)
        if len(data) == 0:
            continue
        mk = next(markers)
        ax[0].errorbar(data[:, 0], data[:, 4], xerr=data[:, 1], yerr=data[:, 5], 
                       linestyle='', markeredgecolor='black', marker =mk,
                       markersize=4, elinewidth=0.8, markeredgewidth=0.5,label=ball)
        ax[1].errorbar(data[:, 0], data[:, 2], xerr=data[:, 1], yerr=data[:, 3], 
                       linestyle='', markeredgecolor='black', marker =mk,
                       markersize=4, elinewidth=0.8, markeredgewidth=0.5, label=ball)
    ax[0].set_ylim(1, 1.4)
    ax[1].set_ylim(0, 0.15)
    ax[0].set_ylabel(r'$r/r_0$')
    ax[1].set_ylabel(r'$(r-r_0)/\delta$')
    fig.suptitle(f'Tube Swelling Comparison for {method} method in {fluid}', fontsize=20)
    for axes in ax:
        axes.set_xlim(10000, 60000)
        axes.set_xlabel('Pressure (Pa)')
        axes.legend(framealpha=0)
    plt.savefig(MASTER_FOLDER /'PLOTS' / f'{fluid}_{method}_swelling.png', dpi=300)
if __name__ == '__main__':
    balls = [f'ball{i+1}' for i in range(5)]
    balls.append('ball3_stretched')
    #colour map
    cmap = plt.get_cmap('cmc.hawaii', len(balls))
    # generate reversed list of colours from the colormap
    colors = [mcolors.to_hex(cmap(i)) for i in range(cmap.N)][::-1]
    # set as the default color cycle
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

    plot_swelling(balls)