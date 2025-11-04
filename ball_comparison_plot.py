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
    ax.plot(x, y, label=label + fr': $\alpha$={beta[0]:.2f}±{sd_beta[0]:.2f}')
    
def ball_comparison():
    
    _, axes = plt.subplots(2, figsize=(6, 6))
    
    for folder_name in os.listdir(MASTER_FOLDER):
        folder_path = os.path.join(MASTER_FOLDER, folder_name)
        
        # Ensure it's a directory (e.g., "ball1", "ball2", ...)
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, "dimensionless_data.txt")

            if folder_name in ['ball3', 'ball4', 'ball1', 'ball2']:
                ax = axes[0]
            elif folder_name in ['ball3_hold_method', 'ball4_hold_method']:
                ax = axes[1]
            else:
                continue
            # Check if the text file exists
            if os.path.isfile(file_path):
                try:
                    data = np.genfromtxt(file_path)
                    _add_to_plot(data, label=folder_name, ax=ax)
                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    # Add labels and legend
    for ax in axes:
        ax.set_xlabel(r"$\lambda$")
        ax.set_ylabel("Dimensionless Pressure")
        #ax.set_title("Speed vs Pressure for All Balls")
        ax.legend(framealpha=0)
        ax.set_yscale('log')
        ax.set_xscale('log')
    plt.tight_layout()
    plt.savefig(MASTER_FOLDER / ('ball_comparison'), dpi=300)
    
    # Show the plot
    plt.show()

if __name__ == '__main__':
    ball_comparison()