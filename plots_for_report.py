# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 20:36:19 2025

@author: David Mawson
"""
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import _ball_folder, PLOTS_FOLDER
from get_fit_params import true_power_law, _log_linear_data, get_fit_params
from constants import BALL_DIAMETERS
from value_to_string import value_to_string
from get_preset import *
from matplotlib import rcParams
from matplotlib.lines import Line2D
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
rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
crop_speed = (0, 1000)

log_scale = True
dimensionless = True
linear = True

SAVE_FIG = False
NEW_FIT = False
save_file = 'test_image.png'

#==============================================================================

def load_data(ball_info):
    """Load data for a single ball."""
    ball_folder = _ball_folder(ball_dict=ball_info)
    try:
        return np.genfromtxt(ball_folder / "dimensionless_data.txt")
    except FileNotFoundError:
        return None

def crop_data(data, ball_info):
    if 'cropping' in ball_info.keys():
        crop = ball_info['cropping']
    else:
        crop = crop_speed
    data = data[(crop[0]<data[:, 1]) & (data[:, 1]<crop[1]), :]
    return data
    
def _errorbar(data, label=None, ax=None, marker=None, legend=True, colour=None):
    if ax is None:
        ax = plt.gca()
    ax.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], yerr=data[:, 3],
    linestyle='', markeredgecolor='black', marker =marker,
    markersize=4, elinewidth=0.8, markeredgewidth=0.5, label=label, c=colour)

    if legend:
        ax.legend(framealpha=0)
    
def plot_balls(balls, ax, ax2=None):
    
    for ball in balls:
        data = load_data(ball)
        if data is None:
            continue
        data = crop_data(data, ball)
        if len(data) < 10: 
            continue
        ball_folder = _ball_folder(ball_dict = ball)

        #get_fit_params(ball_folder)
        params = np.genfromtxt(ball_folder / 'fit_params.txt')[1]
        beta, sd_beta = params[:3], params[3:]
        
        data = _log_linear_data(data, beta)

        ball_size = BALL_DIAMETERS[ball['name'].split('_')[0]][0]

        _errorbar(data, legend=False, marker=markers[ball['name']], ax=ax, label='Data', 
                  colour=colours[ball['name']])
        ax.set_ylim(0.005, 6)

        x_fit = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 50)
        y_fit = true_power_law(beta, x_fit)
            
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.plot(x_fit, y_fit, label="Fit", c=colours[ball['name']])
    ax.tick_params(labelsize=16)
    ax.set_xlabel(r"$\lambda$", fontsize=20)
    ax.set_ylabel(r"$P^*-P^*_{th}$", fontsize=20)
    
colours = {
    'ball1': 'black',
    'ball4': 'tab:blue',
    }
markers = {
    'ball1': 'p',
    'ball4': 'D'
    }

oil_balls = {
    'no-hold': [
            {'name': 'ball1',
             'method': 'no-hold',
             'fluid': 'oil',},
            
            {'name': 'ball4',
             'method': 'no-hold',
             'fluid': 'oil',}
        ], 
    'hold': [
                {'name': 'ball1',
                 'method': 'hold',
                 'fluid': 'oil',},
                
                {'name': 'ball4',
                 'method': 'hold',
                 'fluid': 'oil',}
            ]
    }

glycerol_balls = {
    'no-hold': [
            {'name': 'ball1',
             'method': 'no-hold',
             'fluid': 'glycerol',},
            
            {'name': 'ball4',
             'method': 'no-hold',
             'fluid': 'glycerol',}
        ], 
    'hold': [
                {'name': 'ball1',
                 'method': 'hold',
                 'fluid': 'glycerol',},
                
                {'name': 'ball4',
                 'method': 'hold',
                 'fluid': 'glycerol',}
            ]
    }
def legend(fig, ax):
    header_nohold = Line2D([], [], linestyle='none')
    header_hold   = Line2D([], [], linestyle='none')
    handles, labels = ax['hold'].get_legend_handles_labels()
    order = [3, 1, 2, 0]
    handles, labels = [handles[i] for i in order], [labels[i] for i in order]
    handles = [
    header_nohold, handles[0],     handles[1],  # data
    header_hold, handles[2],    handles[3],   # derived trends
    ]
    
    labels = [
        r'$\delta_m = 0.62\,\mathrm{mm}$', labels[2], labels[3],
        r'$\delta_m = 3.12\,\mathrm{mm}$', labels[0], labels[1],
    ]

    leg = fig.legend(handles, labels, framealpha=1, edgecolor='k', fontsize=20, loc = 'lower center', bbox_to_anchor=(0.51, 0), ncol=2)
    for i, text in enumerate(leg.get_texts()):
        if i in (0, 2):  # header rows
            text.set_fontweight('bold')
def oil_results():
    fig = plt.figure(figsize=(8,16))  
    gs = fig.add_gridspec(nrows=3, ncols=1, height_ratios=[1, 1,   0.2], 
                          wspace=0.18, hspace=0.1)
    axes = {
        'no-hold': fig.add_subplot(gs[0]),
        'hold': fig.add_subplot(gs[1]),
        }
    for method, balls in oil_balls.items():
        plot_balls(balls, axes[method])
    legend(fig, axes)
    for _, ax in axes.items():
        ax.set_ylim(6e-3, 6)
        ax.set_xlim(1e-5, 2.01e-3)
        
    for method, label in {'no-hold': r'\textbf{(a) No-Hold}', 'hold': r'\textbf{(b) Hold}'}.items():
        axes[method].text(
                0.02, 0.97, label,
                transform=axes[method].transAxes,
                fontsize=20,
                fontweight='bold',
                va='top', ha='left'
            )
    plt.savefig(PLOTS_FOLDER / 'oil_results.png', dpi=300)
    plt.show()
    
def glycerol_results():
    fig = plt.figure(figsize=(16, 6))  
    gs = fig.add_gridspec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1,  0.24], 
                          wspace=0.18, hspace=0.1)
    axes = {
        'no-hold': fig.add_subplot(gs[0, 0]),
        'hold': fig.add_subplot(gs[0, 1]),
        }
    for method, balls in glycerol_balls.items():
        plot_balls(balls, axes[method])
    legend(fig, axes)
    for _, ax in axes.items():
        ax.set_ylim(1e-2, 6)
        ax.set_xlim(3e-6, 1.5e-3)
    for method, label in {'no-hold': r'\textbf{(a) No-Hold}', 'hold': r'\textbf{(b) Hold}'}.items():
        axes[method].text(
                0.02, 0.97, label,
                transform=axes[method].transAxes,
                fontsize=20,
                fontweight='bold',
                va='top', ha='left'
            )
    plt.savefig(PLOTS_FOLDER / 'glycerol_results.png', dpi=300)

if __name__ == '__main__':
    oil_results()
    glycerol_results()
    