# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 10:41:11 2025

@author: David Mawson
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER, get_folder_dict
from fit_power_law_odr import fit_power_law_odr
from plot_ball_data import _errorbar, true_power_law
from make_dimensionless import ball_sizes
from value_to_string import value_to_string
import matplotlib.colors as mcolors
from itertools import cycle

# pick a colormap
cmap = plt.get_cmap('cividis', 20)

# generate reversed list of colours from the colormap
colors = [mcolors.to_hex(cmap(i)) for i in range(cmap.N)][::-1]

# set as the default color cycle
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

# Define linestyles and markers
linestyles = cycle(['-', '--', '-.', ':'])
markers = cycle(['o', 's', 'D', '^', 'v', '*', 'x', 'P'])

def _add_to_plot(data, label, ax=None):
    if ax is None:
        ax = plt.gca()
    print(label)
    ls = next(linestyles)
    mk = next(markers)
    
    beta, sd_beta = fit_power_law_odr(data)
    
    data[:, 0] -= beta[2]
    mask = data[:, 0] > 0
    data = data[mask, :]

    x = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 2)
    y = true_power_law(beta, x)
    
    # Plot data with label
    _errorbar(data, label=label, ax=ax, marker=mk)
    ax.plot(x, y, linestyle=ls, label=label +': \n' + 
            fr'$\alpha$={value_to_string(beta[0], sd_beta[0])}' 
            + '\n' + fr'$\beta$={value_to_string(beta[1], sd_beta[1])}')
    
def _process_folder(folder_path, ax):
    file_path = os.path.join(folder_path, "dimensionless_data.txt")
    print(file_path)
    # Check if the text file exists
    try:
        data = np.genfromtxt(file_path)
        ball_size = ball_sizes[folder_path.name.split("_")[0]]
        _add_to_plot(data, label=f'Diametre = {(ball_size*1000):g} mm', ax=ax)
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
def ball_comparison():
    
    _, axes = plt.subplots(ncols = 4, figsize=(24, 10))
    
    axes = {
        "oil hold": axes[1],
        "oil no-hold": axes[0],
        "glycerol hold": axes[3],
        "glycerol no-hold": axes[2],
    }
    
    folders_to_plot = {
        "oil": {
            "no-hold": ['ball3', 'ball4', 'ball1_repeat', 'ball2', 'ball3', 'ball5'],
            "hold":    ['ball3', 'ball4', 'ball3_repeat', 
                        'ball1', 'ball2', 'ball5'],
        },
        "glycerol": {
            "no-hold": ['ball1', 'ball3', 'ball2', 'ball4', 'ball5'],
            "hold": ['ball2', 'ball3', 'ball4', 'ball1'],
            }
    }
    folders = get_folder_dict(folders_to_plot)
    
    for method in folders.keys():
        for folder in folders[method]:
            _process_folder(folder, axes[method])
        
    plt.tight_layout(rect=[0, 0.4, 1, 0.95])  # Leave space at the bottom for legends

    # Add legends below each subplot
    for method, ax in axes.items():
        ax.set_xlabel(r"Dimensionless Speed, $\lambda$")
        ax.set_ylabel("Dimensionless Pressure, P")
        ax.set_title(rf"{method} $P = \beta \lambda^\alpha$")
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.legend(
            framealpha=0,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.12),  # position below each subplot
            ncol=2
        )
    plt.savefig(MASTER_FOLDER / ('ball_comparison'), dpi=300)
    
    # Show the plot
    plt.show()

if __name__ == '__main__':
    ball_comparison()