#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 14:35:41 2025

@author: brunokeyworth

Note that what are called r and r_0 in the code are actually diameters, not radii. 
"""

import numpy as np
from constants import BALL_DIAMETERS, TUBE_PARAMS
from get_folderpaths import _ball_folder, PLOTS_FOLDER
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.lines import Line2D
from scipy import odr
from get_preset import all_balls_hold_glycerol, all_balls_hold_oil, all_balls_no_hold_glycerol, all_balls_no_hold_oil, all_stretched_hold_glycerol, all_stretched_no_hold_glycerol
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
    'hold': 'tab:orange',
    'no-hold': 'black'
    }
marker = {
    'hold': 'o',
    'no-hold': 's',
    }
oil_balls = [
        {'name': 'ball4',
         'method': 'hold',
         'fluid': 'oil',},
        
        {'name': 'ball4',
         'method': 'no-hold',
         'fluid': 'oil',}
    ]
glycerol_balls = [
        {'name': 'ball4',
         'method': 'hold',
         'fluid': 'glycerol',},
        
        {'name': 'ball4',
         'method': 'no-hold',
         'fluid': 'glycerol',},
    ]

stretch_balls = [
        {'name': 'ball4_stretched_1.5',
         'method': 'no-hold',
         'fluid': 'glycerol',}
        
    ]

def linear_func(params, x):
    return params[0]*x + params[1]

def linear_fit(data, ax=None, method=None, usecols=(0,1,2,3), c=None):
    data = data[:, usecols]
    
    model = odr.Model(linear_func)
    odr_data = odr.RealData(x=data[:, 0], y=data[:, 2], sx=data[:, 1], sy=data[:, 3])
    odr_instance = odr.ODR(odr_data, model, beta0=[0.0001, 0.05], iprint=0)  # initial guess
    output = odr_instance.run()
    if output.info <= 4:
        params = output.beta
        sd_params = output.sd_beta
    else: 
        params, cov = np.polyfit(data[:, 0], data[:, 2],1,  w=1/(data[:,3]**2 + 1e-12), cov=True)
        sd_params = [np.sqrt(cov[i][i]) for i in range(2)]
    x = np.linspace(min(data[:, 0]), max(data[:, 0]), 100)
    y = np.polyval(params, x)
    if ax is None: 
        return params[0], sd_params[0]
    ax.plot(x/1e3, y, c=(c or colours[method]), label='Linear Fit')
    
def get_delta(ball):
    a = TUBE_PARAMS['radius']      # a = [value, error]
    R = [e/2 for e in BALL_DIAMETERS[ball['name'].split('_')[0]]]

    delta = R[0] - a[0]
    delta_err = np.sqrt(R[1]**2 + a[1]**2)
   
    return delta *1000, delta_err *1000

def get_gradients(balls):
    grads, errs, deltas, derrs = [], [], [], []
    for ball in balls:
        file_path = _ball_folder(ball['name'], ball['fluid'], ball['method']) / 'swelling_data.txt'
        if not file_path.exists():
            continue
        data = np.genfromtxt(file_path, usecols=(0, 1, 2, 3))
        if len(data) == 0:
            continue
        data[:, :2]/=100
        grad, err = linear_fit(data)
        grads.append(grad)
        errs.append(err)
        radius = BALL_DIAMETERS[ball['name'].split('_')[0]]
        delta, derr = get_delta(ball)
        deltas.append(delta)
        derrs.append(derr)
    data = np.column_stack((deltas, derrs, grads, errs))
    return data

def plot_gradients(hold_balls, no_hold_balls, ax, stretched_balls = None):
    
    balls = {
        'hold': hold_balls,
        'no-hold': no_hold_balls
        }
    for method, balls2 in balls.items():
        data = get_gradients(balls2)
        ax.errorbar(data[:, 0], data[:, 2]*1e3, xerr=data[:, 1], yerr=data[:, 3]*1e3, ls='',
                        color=colours[method], label='Data', zorder=2, fmt=marker[method], markersize=4)
    if stretched_balls is not None:
        data = get_gradients(stretched_balls)
        ax.errorbar(data[:, 0], data[:, 2]*1e3, xerr=data[:, 1], yerr=data[:, 3]*1e3, ls='',
                        color='tab:green', label='Data', zorder=2, fmt='D', markersize=4)
    

def plot_swelling(balls, ax, c=None):
    for ball in balls:
        file_path = _ball_folder(ball['name'], ball['fluid'], ball['method']) / 'swelling_data.txt'
        data = np.genfromtxt(file_path, usecols=(0, 1, 2, 3))
        data[:, :2]/=100
        if len(data) == 0:
            continue
        linear_fit(data, ax, ball['method'], c=c)
        ax.errorbar(data[:, 0]/1e3, data[:, 2], xerr=data[:, 1]/1e3, yerr=data[:, 3], ls='',
                        color=(c or colours[ball['method']]), label='Data', zorder=2, fmt=marker[ball['method']], markersize=4)
    ax.set_xlabel('$\Delta P$ (bar)', fontsize=20)
    ax.set_ylim(0, 0.45)
    ax.set_ylabel(r'$\varepsilon$', fontsize=20)

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
    
def legend_2(fig, ax):
    header_nohold = Line2D([], [], linestyle='none', label=r'\textbf{No-Hold}')
    header_hold   = Line2D([], [], linestyle='none', label=r'\textbf{Hold}')
    handles, labels = ax[1].get_legend_handles_labels()
    stretch_handle = handles[-1]
    stretch_label = labels[-1]
    handles, labels = ax[0].get_legend_handles_labels()
    order = [4, 1, 3, 0, 2, 5]
    handles, labels = [handles[i] for i in order], [labels[i] for i in order]
    handles = [
    header_nohold, handles[0],     handles[1],  # data
    header_hold, handles[2],    handles[3],   # derived trends
    header_hold, stretch_handle, handles[4]
    ]
    
    labels = [
        r'\textbf{No-Hold}', labels[0], labels[1],
        r'\textbf{Hold}', labels[2], labels[3],
        r'\textbf{Axial Tension}', stretch_label, labels[4]
    ]

    fig.legend(handles, labels, framealpha=1, edgecolor='k', fontsize=20, loc = 'lower center', bbox_to_anchor=(0.51, 0), ncol=3)

def oil_swelling():
    fig = plt.figure(figsize=(16,6))  
    gs = fig.add_gridspec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1,  0.24], 
                          wspace=0.18, hspace=0.1)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    plot_swelling(oil_balls, axes[0])
    plot_gradients(all_balls_hold_oil, all_balls_no_hold_oil, axes[1])
    #legend(fig, axes)
    for i, label in enumerate([r'\textbf{(a)}', r'\textbf{(b)}']):
        axes[i].text(
                0.02, 0.97, label,
                transform=axes[i].transAxes,
                fontsize=20,
                fontweight='bold',
                va='top', ha='left'
            )
    axes[-1].set_xticks([2.12, 3.12, 4.12])
    axes[1].set_xlabel(r'$\delta_m$ (mm)', fontsize=20)
    axes[1].set_ylabel(r'Fitted Gradient (bar$^{-1}$)', fontsize=20)
    for ax in axes:
        ax.tick_params(labelsize=14)
    legend(fig, axes)
    plt.savefig(PLOTS_FOLDER / 'oil_swelling.png', dpi=300)
    plt.show()
    
def glycerol_swelling():
    fig = plt.figure(figsize=(16, 6.8))  
    gs = fig.add_gridspec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1,  0.28], 
                          wspace=0.18, hspace=0.1)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    plot_swelling(glycerol_balls, axes[0])
    plot_swelling(stretch_balls, axes[0], c='tab:green')
    plot_gradients(all_balls_hold_glycerol, all_balls_no_hold_glycerol, axes[1], all_stretched_hold_glycerol + all_stretched_no_hold_glycerol)

    #legend(fig, axes)
    for i, label in enumerate([r'\textbf{(a)}', r'\textbf{(b)}']):
        axes[i].text(
                0.02, 0.97, label,
                transform=axes[i].transAxes,
                fontsize=20,
                fontweight='bold',
                va='top', ha='left'
            )
    axes[-1].set_xticks([0.62, 1.12, 2.12, 3.12, 4.12])
    axes[1].set_xlabel(r'$\delta_m$ (mm)', fontsize=20)
    axes[1].set_ylabel(r'Fitted Gradient (bar$^{-1}$)', fontsize=20)
    for ax in axes:
        ax.tick_params(labelsize=14)
    legend_2(fig, axes)
    axes[0].set_ylim(0, 0.6)
    plt.savefig(PLOTS_FOLDER / 'glycerol_swelling.png', dpi=300)
    
def stretch_swelling():
    fig = plt.figure(figsize=(16, 6.5))  
    gs = fig.add_gridspec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1,  0.2], 
                          wspace=0.18, hspace=0.1)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    plot_swelling(stretch_balls, axes[0])
    plot_gradients(all_stretched_hold_glycerol + all_stretched_no_hold_glycerol, [], axes[1])

    #legend(fig, axes)
    for i, label in enumerate([r'\textbf{(a)}', r'\textbf{(b)}']):
        axes[i].text(
                0.02, 0.97, label,
                transform=axes[i].transAxes,
                fontsize=20,
                fontweight='bold',
                va='top', ha='left'
            )
    axes[-1].set_xticks([0.62, 1.12, 2.12, 3.12, 4.12])
    axes[1].set_xlabel(r'$\delta_m$ (mm)', fontsize=20)
    axes[1].set_ylabel(r'Fitted Gradient (bar$^{-1}$)', fontsize=20)
    for ax in axes:
        ax.tick_params(labelsize=14)
    legend(fig, axes)
    axes[0].set_ylim(0, 0.6)
    plt.savefig(PLOTS_FOLDER / 'stretch_swelling.png', dpi=300)

if __name__ == '__main__':
   # oil_swelling()
    glycerol_swelling()
    #stretch_swelling()
    