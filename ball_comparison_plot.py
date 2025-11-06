# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 10:41:11 2025

@author: David Mawson
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER
from fit_power_law_odr import fit_power_law_odr
from plot_ball_data import _errorbar, true_power_law
from make_dimensionless import ball_sizes
from value_to_string import value_to_string
import matplotlib.colors as mcolors

# pick a colormap
cmap = plt.get_cmap('viridis', 10)  # '10' = number of distinct colors you want

plt.rcParams['axes.prop_cycle'] = plt.cycler(
    color=[mcolors.to_hex(cmap(i)) for i in range(cmap.N)]
)

def _add_to_plot(data, label, ax=None):
    if ax is None:
        ax = plt.gca()
    print(label)
    
    beta, sd_beta = fit_power_law_odr(data)
    
    data[:, 0] -= beta[2]
    mask = data[:, 0] > 0
    data = data[mask, :]

    x = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 2)
    y = true_power_law(beta, x)
    
    # Plot data with label
    _errorbar(data, label=label, ax=ax)
    ax.plot(x, y, label=label +': \n' + fr'$\alpha$={value_to_string(beta[0], sd_beta[0])}' + '\n' + fr'$\beta$={value_to_string(beta[1], sd_beta[1])}')
    
def ball_comparison():
    
    _, axes = plt.subplots(ncols = 2, figsize=(12, 8))
    
    for folder_name in sorted(os.listdir(MASTER_FOLDER)):
        folder_path = os.path.join(MASTER_FOLDER, folder_name)
        
        # Ensure it's a directory (e.g., "ball1", "ball2", ...)
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, "dimensionless_data.txt")

            if folder_name in ['ball3', 'ball4', 'ball1_repeat', 'ball2_repeat', 'ball3_repeat', 'ball5']:
                ax = axes[0]
            elif folder_name in ['ball3_hold_method', 'ball4_hold_method', 'ball3_hold_repeat', 'ball1_hold_repeat', 'ball2_hold_repeat', 'ball5_hold']:
                ax = axes[1]
            else:
                continue
            # Check if the text file exists
            if os.path.isfile(file_path):
                try:
                    data = np.genfromtxt(file_path)
                    ball_size = ball_sizes[folder_name.split("_")[0]]
                    _add_to_plot(data, label=f'Diametre = {ball_size:g} mm', ax=ax)
                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
    plt.tight_layout(rect=[0, 0.4, 1, 1])  # Leave space at the bottom for legends

    # Add legends below each subplot
    for i, ax in enumerate(axes):
        ax.set_xlabel(r"Dimensionless Speed, $\lambda$")
        ax.set_ylabel("Dimensionless Pressure, P")
        ax.set_title(r"$P = \beta \lambda^\alpha$")
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