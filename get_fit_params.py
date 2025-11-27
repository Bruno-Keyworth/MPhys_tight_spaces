#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 22:35:26 2025

@author: brunokeyworth
"""
import matplotlib.pyplot as plt
import numpy as np
from fit_power_law_odr import fit_power_law_odr
from value_to_string import value_to_string

def power_law(beta, x):
    return beta[2] + beta[1] * x**beta[0]

def true_power_law(beta, x):
    return beta[1] * x**beta[0]

def _errorbar(data, label=None, ax=None, marker=None, legend=True):
    if ax is None:
        ax = plt.gca()
    ax.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], yerr=data[:, 3],
    linestyle='', markeredgecolor='black', marker =marker,
    markersize=4, elinewidth=0.8, markeredgewidth=0.5, label=label)

    if legend:
        ax.legend(framealpha=0)
        
def _log_linear_data(data, beta):
    data[:, 0] -= beta[2]
    mask = data[:, 0] > 0
    return data[mask, :]

def _plot(data, params, log=False):
    axes = plt.gcf().get_axes()
    beta = params[:3]
    sd_beta = params[3:]
    x = np.linspace(min(data[:, 1]), max(data[:, 1]), 100)
    if log:
        ax = axes[1]
        ax.set_yscale('log')
        ax.set_xscale('log')
        data = _log_linear_data(data, beta)
        y = true_power_law(beta, x)
    else:
        ax = axes[0]
        y = power_law(beta, x)
    ax.plot(x, y, color='blue', label= fr"$\alpha$={value_to_string(beta[0], sd_beta[0])}"
    + "\n" + fr"$\beta$={value_to_string(beta[1], sd_beta[1])}" + "\n"
    + fr"$\gamma$={value_to_string(beta[2], sd_beta[2])}")
    _errorbar(data, ax=ax)

def dimless_plot(ball_folder):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("/".join(ball_folder.parts[-3:]) + ' Non-Dimensional Fit')
    data = np.genfromtxt(ball_folder / 'dimensionless_data.txt')
    params = np.genfromtxt(ball_folder / 'fit_params.txt')[1]
    _plot(data, params)
    _plot(data, params, log=True)
    for ax in axes:
        ax.set_ylabel('Dimensionless Pressure, P')
        ax.set_xlabel(r'Dimensionless Speed, $\lambda$')
    plt.savefig(ball_folder / 'non-dimensional-plot.png', dpi=300)
    
def dimensional_plot(ball_folder):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("/".join(ball_folder.parts[-3:]) + ' Dimensional Fit')
    data = np.genfromtxt(ball_folder / 'speed_pressure.txt')
    params = np.genfromtxt(ball_folder / 'fit_params.txt')[0]
    _plot(data, params)
    _plot(data, params, log=True)
    for ax in axes:
        ax.set_ylabel('Pressure (Pa)')
        ax.set_xlabel('Speed (m/s)')
    plt.savefig(ball_folder / 'dimensional-plot.png', dpi=300)
    
def plot_ball_data(ball_folder):
    dimless_plot(ball_folder)
    dimensional_plot(ball_folder)

def get_fit_params(ball_folder, plot=False):
    save_params = ball_folder / 'fit_params.txt'
    dim_data = np.genfromtxt(ball_folder / 'speed_pressure.txt')
    beta, sd_beta = fit_power_law_odr(dim_data)
    dim_params = np.append(beta, sd_beta)
    
    dimless_data = np.genfromtxt(ball_folder / 'dimensionless_data.txt')
    beta, sd_beta = fit_power_law_odr(dimless_data)
    dimless_params = np.append(beta, sd_beta)
    
    params = np.vstack((dim_params, dimless_params))
    np.savetxt(save_params, params)
        
    
        