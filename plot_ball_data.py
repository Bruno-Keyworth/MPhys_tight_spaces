#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 22:35:26 2025

@author: brunokeyworth
"""
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER
from fit_power_law_odr import fit_power_law_odr

def power_law(beta, x):
    return beta[2] + beta[1] * x**beta[0]

def true_power_law(beta, x):
    return beta[1] * x**beta[0]

def _errorbar(data, dimensions=False, label=None, ax=None):
    if ax is None:
        ax = plt.gca()
    ax.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], yerr=data[:, 3], fmt='o',
    linestyle='', markeredgecolor='black',
    markersize=4, elinewidth=0.8, markeredgewidth=0.5, label=label)
    if dimensions:
        ax.set_xlabel('Speed (m/s)')
    else:
        ax.set_xlabel(r'$\lambda$')
    ax.legend(framealpha=0)

def plot_ball_data(ball, data, version=''):
    
    if version.split('_')[-1] == 'dimensionless':
        dimensions = False
    else:
        dimensions = True
    
    save_name = f'speed_pressure_{version or ""}.png'

    beta, sd_beta = fit_power_law_odr(data)

    fit_results = '\n'+fr" $\alpha$ = {beta[0]:.2f} ± {sd_beta[0]:.2f}"+'\n'+\
    fr"b = {beta[1]:.2f} ± {sd_beta[1]:.2f}"+'\n'+fr"  a = {beta[2]:.2f} ± {sd_beta[2]:.2f}"
    
    x = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 100)
    y = power_law(beta, x)

    fig, ax = plt.subplots()
    ax.plot(x, y, color = "blue",  label = r"$y=a+bx^\alpha$" + fit_results)
    _errorbar(data, dimensions)
    if dimensions:
        ax.set_ylabel('Pressure (Pa)')
    else:
        ax.set_ylabel('Dimensionless Pressure')
    ax.set_title(ball)

    plt.savefig(MASTER_FOLDER / ball / save_name, dpi=300)
    ax.set_yscale('log')
    ax.set_xscale('log')
    plt.savefig(MASTER_FOLDER / ball / ('log_' + save_name), dpi=300)
    plt.show()
    
    data[:, 0] -= beta[2]
    mask = data[:, 0] > 0
    data = data[mask, :]

    y_fit_corr = true_power_law(beta, x)
    
    fig, ax = plt.subplots()
    ax.plot(x, y_fit_corr, color='blue', label=r"$y' = (y-a) = bx^\alpha$" + fit_results)
    _errorbar(data, dimensions)
    if dimensions:
        ax.set_ylabel(r'$y - a$ (Pa)')
    else:
        ax.set_ylabel(r'Dimensionless Pressure $y - a$')
    ax.set_title(ball + ' (log–log straightened)')
    ax.set_yscale('log')
    ax.set_xscale('log')

    plt.savefig(MASTER_FOLDER / ball / ('log_linear_' + save_name), dpi=300)
    plt.show()