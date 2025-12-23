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
from get_fit_params import power_law, true_power_law
from fit_power_law_beta import fit_power_law_simple
from value_to_string import value_to_string
from matplotlib import rcParams
from scipy import odr
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 10,
    "font.size": 10,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

colours = {
    'Hold': 'tab:orange',
    'No-Hold': 'black'
    }
marker = {
    'Hold': 'o',
    'No-Hold': 's',
    }
labels = {
    'Hold': 'Derived Trend',
    'No-Hold': 'Weighted Average',
    }
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
    
def _plot(data, ax, method):
    ax.errorbar(data[:, 0], data[:, 2], xerr=data[:, 1], yerr=data[:, 3], ls='',
                    color=colours[method], label='Data', zorder=2, fmt=marker[method], markersize=4)
    
def _add_to_plot(hold_data, no_hold_data, ax):
    
    for i in range(2):
        data_dict = {
            'Hold': np.column_stack((hold_data[:, 0+i*4], hold_data[:, 1+i*4], hold_data[:, 2+i*4], hold_data[:, 3+i*4])),
            'No-Hold': np.column_stack((no_hold_data[:, 0+i*4], no_hold_data[:, 1+i*4], no_hold_data[:, 2+i*4], no_hold_data[:, 3+i*4])),
            }
        for method, data in data_dict.items():
            if len(ax) == 3 and i==1:
                mask = data[:, 2] > 1e5
                bottom_data = data[~mask]
                bottom_data[:, 2:]/=1e3
                top_data = data #[mask]
                top_data[:, 2:]/=1e6
                _plot(top_data, ax[1], method)
                _plot(bottom_data, ax[2], method)
            else:
                _plot(data, ax[i], method)
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

    y = (delta / l)
    yerr = np.abs(y) * np.sqrt(
        (delta_err / delta)**2 +
        (lerr / l)**2
    )
    data[:, 0] = delta *1000
    data[:, 1] = delta_err *1000
    return np.column_stack((data[:, :4], y, yerr, data[:, 4:]))

def read_data(filename):
    data = np.genfromtxt(MASTER_FOLDER / filename, usecols=(0,1,2,3,4,5))
    return change_beta_data(data)

def weighted_average(values, errors):
    weights = 1/errors**2
    
    average = np.average(values, weights=weights)
    std = np.sqrt(1 / np.sum(weights))
    
    N = len(values)
    s_w = np.sqrt(np.sum(weights * (values - average)**2) / np.sum(weights) * N/(N-1))
    
    print(f'formal error: {std}')
    print(f'scatter error: {s_w}')
    
    return average, np.sqrt(s_w**2 + std**2)

def quadratic_func(params, x):
    return params[2]+params[0]*x**2

def linear_func(params, x):
    return params[0]*x + params[1]

def linear_fit(data, ax, method, usecols=(0,1,2,3)):
    data = data[:, usecols]
    mask = data[:, 2]>1.4
    if len(data[~mask])!=0:
        data=data[~mask]
    
    model = odr.Model(linear_func)
    odr_data = odr.RealData(x=data[:, 0], y=data[:, 2], sx=data[:, 1], sy=data[:, 3])
    odr_instance = odr.ODR(odr_data, model, beta0=[-1, 1], iprint=0)  # initial guess
    output = odr_instance.run()
    x = np.linspace(min(data[:, 0]), max(data[:, 0]), 100)
    y = np.polyval(output.beta, x)
    print(output.beta)
    print(output.sd_beta)
    ax.plot(x, y, c=colours[method], label='Linear Fit')
    return 0

def beta_fit(data, ax, method, scale=1, beta0=[-1, 0, 10], ymax=True):
    if ymax:
        mask = data[:, 2] > 1
        data = data[~mask]
    model = odr.Model(quadratic_func)
    odr_data = odr.RealData(x=data[:, 4], y=data[:, 6], sx=data[:, 5], sy=data[:, 7])
    odr_instance = odr.ODR(odr_data, model, beta0=beta0, iprint=0)  # initial guess
    output = odr_instance.run()
    x = np.linspace(0.1, 0.28, 100)
    y = np.polyval(output.beta, x)
    print(output.beta)
    print(output.sd_beta)
    ax.plot(x, y/scale, c=colours[method], label='Derived Trend')
    
def label_axes(ax):
    ax[-1].set_ylabel(r'$\beta$', fontsize=20)
    ax[0].set_ylabel(r'$\alpha$', fontsize=20)
    ax[0].set_xlabel('$\delta_m$ (mm)', fontsize=20)
    ax[-1].set_xlabel(r'$\delta_m/l$', fontsize=20)
    
def legend(fig, ax):
    header_nohold = Line2D([], [], linestyle='none', label=r'\textbf{No-Hold}')
    header_hold   = Line2D([], [], linestyle='none', label=r'\textbf{Hold}')
    handles, labels = ax[0].get_legend_handles_labels()
    order = [3, 1, 2, 0]
    handles, labels = [handles[i] for i in order], [labels[i] for i in order]
    handles = [
    header_nohold, handles[0],     handles[1],  # data
    header_hold, handles[2],    handles[3],   # derived trends
    ]
    
    labels = [
        r'\textbf{No-Hold}', labels[0], labels[1],
        r'\textbf{Hold}', labels[2], labels[3],
    ]

    fig.legend(handles, labels, framealpha=1, edgecolor='k', fontsize=20, loc = 'lower center', bbox_to_anchor=(0.51, 0), ncol=2)
    
def set_xticks(ax, data):
    ax[0].set_xticks(data[:, 0])
    ax[-1].set_xticks(data[:, 4])
    ax[0].xaxis.set_major_formatter(
    mticker.FormatStrFormatter('%.2f')
    )
    ax[-1].xaxis.set_major_formatter(
    mticker.FormatStrFormatter('%.2f')
    )
def oil_plot():
    no_hold = all_balls_no_hold_oil
    hold = all_balls_hold_oil
    
    create_data(no_hold, MASTER_FOLDER / 'no_hold_oil.txt')
    create_data(hold, MASTER_FOLDER / 'hold_oil.txt')
    hold_data = read_data('hold_oil.txt')
    no_hold_data = read_data('no_hold_oil.txt')

    fig = plt.figure(figsize=(16, 7))  
    gs = fig.add_gridspec(nrows=3, ncols=2, width_ratios=[1, 1], height_ratios=[1, 1, 0.5], wspace=0.15, hspace=0.1)
    ax = [fig.add_subplot(gs[:2, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])]
    alpha_av= weighted_average(no_hold_data[:, 2], no_hold_data[:, 3])
    print(alpha_av)
    print(weighted_average(hold_data[:, 2], hold_data[:, 3]))

    #beta_fit(no_hold_data, ax[1], 'No-Hold', 1e6, [0.1, 0, 1], False)
    beta_fit(hold_data, ax[2], 'Hold', 1e3, [-10, 0, 10], False)
    linear_fit(hold_data, ax[0], 'Hold')
    label_axes(ax)
    ax[1].tick_params(labelbottom=False)
    ax[1].set_yticks([0, 2, 4])
    ax[2].set_yticks([0,2, 6, 10])
    set_xticks(ax, hold_data)
    ax[1].set_ylabel(r'$\beta\ (\times 10^{6})$', fontsize=20)
    ax[2].set_ylabel(r'$\beta\ (\times 10^{3})$', fontsize=20)
    _add_to_plot(hold_data, no_hold_data, ax)
    ax[0].axhline(alpha_av[0], color=colours['No-Hold'], label='Weighted Average')
    for axes in ax:
        axes.tick_params(labelsize=14)
    legend(fig, ax)
    ax[0].set_ylim(1, 2)
    ax[1].set_ylim(-0.2, 3)
    ax[2].set_ylim(2, 11)
    for i, label in enumerate([r'\textbf{(a)}', r'\textbf{(b)}', r'\textbf{(c)}']):
        ax[i].text(
                0.02, 0.97, label,
                transform=ax[i].transAxes,
                fontsize=20,
                fontweight='bold',
                va='top', ha='left'
            )
    plt.savefig(PLOTS_FOLDER / 'oil_params.png', dpi=300)
    plt.show()
    
def glycerol_plot():
    no_hold = all_balls_no_hold_glycerol
    hold = all_balls_hold_glycerol

    create_data(no_hold, MASTER_FOLDER / 'no_hold_glycerol.txt')
    create_data(hold, MASTER_FOLDER / 'hold_glycerol.txt')

    hold_data = read_data('hold_glycerol.txt')
    no_hold_data = read_data('no_hold_glycerol.txt')

    fig = plt.figure(figsize=(16, 7))  
    gs = fig.add_gridspec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1,  0.2], wspace=0.15, hspace=0.1)
    ax = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]

    #beta_fit(hold_data, ax[1], 'Hold')
    #beta_fit(no_hold_data, ax[1], 'No-Hold')
    linear_fit(hold_data, ax[0], 'Hold')
    linear_fit(no_hold_data, ax[0], 'No-Hold')
    _add_to_plot(hold_data, no_hold_data, ax)
    label_axes(ax)
    set_xticks(ax, hold_data)
    ax[1].set_ylim(0, 1200)
    ax[0].set_xlim(0.2, 4.4)
    for power in [4/5, 2/3, 1/2]:
        ax[0].axhline(power, color='0.4', ls='dotted', zorder=0)
    for axes in ax:
        axes.tick_params(labelsize=14)

    legend(fig, ax)
    for i, label in enumerate([r'\textbf{(a)}', r'\textbf{(b)}']):
        ax[i].text(
                0.02, 0.97, label,
                transform=ax[i].transAxes,
                fontsize=20,
                fontweight='bold',
                va='top', ha='left'
            )
    plt.savefig(PLOTS_FOLDER / 'glycerol_params.png', dpi=300)
    
def stretched_plot():
    no_hold = all_stretched_no_hold_glycerol
    hold = all_stretched_hold_glycerol

    create_data(no_hold, MASTER_FOLDER / 'no_hold_stretched.txt')
    create_data(hold, MASTER_FOLDER / 'hold_stretched.txt')

    hold_data = read_data('hold_stretched.txt')
    no_hold_data = read_data('no_hold_stretched.txt')

    fig = plt.figure(figsize=(16, 7))
    gs = fig.add_gridspec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1,  0.2], wspace=0.15, hspace=0.1)
    ax = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]

    #beta_fit(hold_data, ax[1], 'Hold')
    #beta_fit(no_hold_data, ax[1], 'No-Hold')
    average= weighted_average(np.append(no_hold_data[:, 2], hold_data[:, 2]), np.append(no_hold_data[:, 3], hold_data[:, 3]))
    print('stretch', average)
    _add_to_plot(hold_data, no_hold_data, ax)
    ax[0].axhline(average[0], color='tab:green', label='weighted_average')
    label_axes(ax)
    set_xticks(ax, no_hold_data)
    ax[1].set_ylim(0, 300)
    for power in [4/5, 2/3, 1/2]:
        ax[0].axhline(power, color='0.4', ls='dotted', zorder=0)
    for axes in ax:
        axes.tick_params(labelsize=14)
    handles, labels = ax[0].get_legend_handles_labels()
    labels = [rf'Weighted Average $\alpha=$ {value_to_string(average[0], average[1])}', 'Hold Data', 'No-Hold Data']
    handles.reverse()
    labels.reverse()
    fig.legend(handles, labels, framealpha=1, edgecolor='k', fontsize=20, loc = 'lower center', bbox_to_anchor=(0.51, 0), ncol=1)
    #legend(fig, ax)
    plt.savefig(PLOTS_FOLDER / 'stretched_params.png', dpi=300)

    
#oil_plot()
#glycerol_plot()
stretched_plot()