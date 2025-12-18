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
from constants import BALL_DIAMETERS, TUBE_PARAMS
from fit_power_law_odr_params import fit_power_law_odr
from get_fit_params import power_law
from fit_power_law_beta import fit_power_law_simple
from value_to_string import value_to_string

def _fetch_params(ball):
    #get_fit_params(_ball_folder(ball_dict=ball))
    params_file = _ball_folder(ball_dict=ball) / 'fit_params.txt'
    if not params_file.exists():
        return None, None
    # params will be ordered: alpha, alpha_err, beta, beta_err (threshold has 
    # been considered separately)
    params = np.genfromtxt(params_file, usecols=(0,3,1,4))
    return params[0, :], params[1, :]

def create_data(balls, save_as):
    
    ball_sizes = []
    dimless_params_list = []
    for ball in balls:
        # dimless_params refers to params obtained through fitting to the dimensionless data;
        # both alpha are dimensionless values.
        _, dimless_params, = _fetch_params(ball)
        if dimless_params is None:
            continue
        ball_size = BALL_DIAMETERS[ball['name'].split('_')[0]]
        ball_sizes.append(ball_size)
        dimless_params_list.append(dimless_params)
    
    data = np.column_stack((ball_sizes, dimless_params_list))
    np.savetxt(save_as, data)
    
def _add_to_plot(data, ax, c, label):
    ax.errorbar(data[:, 0], data[:, 2], xerr=data[:, 1], yerr=data[:, 3], ls='',
                color=c, marker='.', label=label)

def change_beta_data(data):
    a = TUBE_PARAMS['radius']      # a = [value, error]

    R = data[:, 0] / 2
    err = data[:, 1] / 2

    delta = R - a[0]
    delta_err = np.sqrt(err**2 + a[1]**2)

    l = 2 * np.sqrt(R**2 - a[0]**2)
    lerr = np.sqrt(
        ((2 * R / np.sqrt(R**2 - a[0]**2)) * err)**2 +
        ((-2 * a[0] / np.sqrt(R**2 - a[0]**2)) * a[1])**2
    )

    y = delta / l
    yerr = np.abs(y)**2 * 2 * np.sqrt(
        (delta_err / delta)**2 +
        (lerr / l)**2
    )

    data[:, 0] = y**2
    data[:, 1] = yerr
    return data

def weighted_average(values, errors):
    weights = 1/errors**2
    
    average = np.average(values, weights=weights)
    std = np.sqrt(1 / np.sum(weights))
    
    N = len(values)
    s_w = np.sqrt(np.sum(weights * (values - average)**2) / np.sum(weights) * N/(N-1))
    
    print(f'formal error: {std}')
    print(f'scatter error: {s_w}')
    
    return average, np.sqrt(s_w**2 + std**2)

def oil_plot():
    no_hold = all_balls_no_hold_oil
    hold = all_balls_hold_oil
    
    create_data(no_hold, MASTER_FOLDER / 'no_hold_oil.txt')
    create_data(hold, MASTER_FOLDER / 'hold_oil.txt')
    
    alpha_hold = np.genfromtxt(MASTER_FOLDER / 'hold_oil.txt', usecols=(0,1,2,3))
    alpha_no_hold = np.genfromtxt(MASTER_FOLDER / 'no_hold_oil.txt', usecols=(0,1,2,3))
    beta_hold = np.genfromtxt(MASTER_FOLDER / 'hold_oil.txt', usecols=(0,1,4,5))
    beta_no_hold = np.genfromtxt(MASTER_FOLDER / 'no_hold_oil.txt', usecols=(0,1,4,5))
    beta_hold = change_beta_data(beta_hold)
    beta_no_hold = change_beta_data(beta_no_hold)
    
    fig, ax = plt.subplots(1, 2, figsize=(16, 7))
    
    alpha_no_hold_av, alpha_no_hold_std = weighted_average(alpha_no_hold[:, 2], alpha_no_hold[:, 3])
    alpha_hold_av, alpha_hold_std = weighted_average(alpha_hold[:, 2], alpha_hold[:, 3])
    beta_no_hold_av, beta_no_hold_std = weighted_average(beta_no_hold[:, 2], beta_no_hold[:, 3])
    beta_hold_av, beta_hold_std = weighted_average(beta_hold[:, 2], beta_hold[:, 3])
    
    _add_to_plot(alpha_hold, ax[0], 'r', 'Hold Weighted Average:'+
                 '\n'+fr'    $\alpha=${value_to_string(alpha_hold_av, alpha_hold_std)}'+
                 '\n'+fr'    $\beta=${value_to_string(beta_hold_av, beta_hold_std)}')
    _add_to_plot(alpha_no_hold, ax[0], 'b', 'No-Hold Weighted Average:'+
                 '\n'+fr'    $\alpha=${value_to_string(alpha_no_hold_av, alpha_no_hold_std)}'+
                 '\n'+fr'    $\beta=${value_to_string(beta_no_hold_av, beta_no_hold_std)}')
    _add_to_plot(beta_hold, ax[1], 'r', label=None)
    _add_to_plot(beta_no_hold, ax[1], 'b', label=None)
    ax[1].set_ylabel(r'$\beta$', fontsize=20)
    ax[0].set_ylabel(r'$\alpha$', fontsize=20)
    ax[1].set_yscale('log')
    ax[0].axhline(alpha_no_hold_av, color='b', ls='dashed')
    ax[0].axhline(alpha_hold_av, color='r', ls='dashed')
    ax[1].axhline(beta_no_hold_av, color='b', ls='dashed')
    ax[1].axhline(beta_hold_av, color='r', ls='dashed')
    ax[0].set_xlabel('Intruder Diamter (m)', fontsize=20)
    ax[1].set_xlabel(r'$(\delta_m/l)^2$', fontsize=20)
    for axes in ax:
        axes.tick_params(labelsize=14)
    plt.tight_layout(rect=[0, 0.18, 1, 1])
    fig.legend(framealpha=1, edgecolor='k', fontsize=20, loc = 'lower center', bbox_to_anchor=(0.5, 0), ncol=2)
    plt.savefig(PLOTS_FOLDER / 'oil_params.png', dpi=300)
    plt.show()
    
def glycerol_plot():
    no_hold = all_balls_no_hold_glycerol
    hold = all_balls_hold_glycerol
    
    create_data(no_hold, MASTER_FOLDER / 'no_hold_glycerol.txt')
    create_data(hold, MASTER_FOLDER / 'hold_glycerol.txt')
    
    alpha_hold = np.genfromtxt(MASTER_FOLDER / 'hold_glycerol.txt', usecols=(0,1,2,3))
    alpha_no_hold = np.genfromtxt(MASTER_FOLDER / 'no_hold_glycerol.txt', usecols=(0,1,2,3))
    beta_hold = np.genfromtxt(MASTER_FOLDER / 'hold_glycerol.txt', usecols=(0,1,4,5))
    beta_no_hold = np.genfromtxt(MASTER_FOLDER / 'no_hold_glycerol.txt', usecols=(0,1,4,5))
    beta_hold = change_beta_data(beta_hold)
    beta_no_hold = change_beta_data(beta_no_hold)
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    
    params, _ = fit_power_law_odr(beta_no_hold)
    print(params)
    x = np.linspace(0.01, 0.08, 100)
    y = power_law(params, x)
    
    ax[1].plot(x, y, c='b')
    _add_to_plot(alpha_hold, ax[0], 'r', 'Hold Method')
    _add_to_plot(alpha_no_hold, ax[0], 'b', 'No-Hold Method')
    ax[0].legend(framealpha=0.5, fontsize=18)
    _add_to_plot(beta_hold, ax[1], 'r', 'Hold Method')
    _add_to_plot(beta_no_hold, ax[1], 'b', 'No-Hold Method')
    ax[1].legend(framealpha=0.5, fontsize=18)
    ax[1].set_ylabel(r'$\beta$', fontsize=20)
    ax[0].set_ylabel(r'$\alpha$', fontsize=20)
    ax[1].set_yscale('log')
    for power in [4/5, 2/3, 1/2]:
        ax[0].axhline(power, c='k', ls='dashed')
    ax[0].set_xlabel('Intruder Diamter (m)', fontsize=20)
    ax[1].set_xlabel(r'$(\delta_m/l)^2$', fontsize=20)
    for axes in ax:
        axes.tick_params(labelsize=14)
    
    plt.tight_layout()
    plt.savefig(PLOTS_FOLDER / 'glycerol_params.png', dpi=300)

    
oil_plot()
#glycerol_plot()
