#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 09:44:25 2025

@author: brunokeyworth
"""

from get_preset import *
import numpy as np
import matplotlib.pyplot as plt
from get_folderpaths import _ball_folder, MASTER_FOLDER, PLOTS_FOLDER
from constants import BALL_DIAMETERS

def _fetch_params(ball):
    params_file = _ball_folder(ball_dict=ball) / 'fit_params.txt'
    if not params_file.exists():
        return None, None
    # params will be ordered: alpha, alpha_err, beta, beta_err (threshold has 
    # been considered separately)
    params = np.genfromtxt(params_file, usecols=(0,3,1,4))
    return params[1, :], params[0, :]

def create_data(balls, save_as):
    
    ball_sizes = []
    params_list = []    
    dimless_params_list = []
    for ball in balls:
        # dimless_params refers to params obtained through fitting to the dimensionless data;
        # both alpha are dimensionless values.
        params, dimless_params, = _fetch_params(ball)
        if params is None:
            continue
        ball_size = BALL_DIAMETERS[ball['name'].split('_')[0]]
        ball_sizes.append(ball_size)
        params_list.append(params)
        dimless_params_list.append(dimless_params)
    
    data = np.column_stack((ball_sizes, params_list, dimless_params_list))
    np.savetxt(save_as, data)
    
def _add_to_plot(data, ax):
    ax.errorbar(data[:, 0], data[:, 2], xerr=data[:, 1], yerr=data[:, 3], ls='')

def plot_params(balls, redo=False, stretched=None):
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    
    file_path = MASTER_FOLDER / balls[0]['fluid'] / balls[0]['method'] / f'{stretched or ""}_params_data.txt'
    if (not file_path.exists()) or redo:
        create_data(balls, save_as=file_path)
    alpha_data = np.genfromtxt(file_path, usecols=(0,1,2,3))
    beta_data = np.genfromtxt(file_path, usecols=(0,1,4,5))
    plt.suptitle(r"$\Delta P = \beta\lambda^\alpha$ parameter comparison for " +
                   f"{balls[0]['method']} in {balls[0]['fluid']}", fontsize=18)
    
    _add_to_plot(alpha_data, ax[0])
    _add_to_plot(beta_data, ax[1])
    ax[0].set_title(r'$\alpha$', fontsize=18)
    for power in [4/5, 2/3, 1/2]:
        ax[0].axhline(power, c='k', ls='dashed')
    ax[1].set_title(r'$\beta$', fontsize=18)
    ax[0].set_ylabel(r'$\alpha$', fontsize=14)
    ax[1].set_ylabel(r'$\beta$', fontsize=14)
    for axes in ax:
        axes.set_xlabel('Ball Diameter (m)')
    plt.tight_layout()
    save_as = PLOTS_FOLDER /f"{balls[0]['method']}_{balls[0]['fluid']}_{stretched or ''}_parameters.png"
    plt.savefig(save_as, dpi=300)
    
plot_params(all_balls_no_hold_glycerol + all_balls_hold_glycerol)
