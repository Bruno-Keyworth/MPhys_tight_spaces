# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 20:36:19 2025

@author: David Mawson
"""
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import _ball_folder
from get_fit_params import _errorbar, true_power_law, power_law, _log_linear_data, get_fit_params
from constants import BALL_DIAMETERS
from value_to_string import value_to_string


balls = [
    {'name': 'ball3',
     'method': 'no-hold',
     'fluid': 'glycerol',},

    {'name': 'ball3_repeat',
     'method': 'no-hold',
     'fluid': 'glycerol',},

    {'name': 'ball3_stretched',
     'method': 'hold',
     'fluid': 'glycerol',},

    {'name': 'ball3_repeat',
     'method': 'hold',
     'fluid': 'glycerol',}
]

crop_speed = (0, 0.1)

log_scale = False
dimensionless = False
linear = False

def load_data(ball_info):
    """Load data for a single ball."""
    ball_folder = _ball_folder(ball=ball_info['name'], fluid=ball_info['fluid'],
                               method=ball_info['method'])

    if dimensionless:
        return np.genfromtxt(ball_folder / "dimensionless_data.txt")
    else:
        return np.genfromtxt(ball_folder / "speed_pressure.txt")

def crop_data(data, ball_info):
    if 'cropping' in ball_info.keys():
        crop = ball_info['cropping']
    else:
        crop = crop_speed
    data = data[(crop[0]<data[:, 1]) & (data[:, 1]<crop[1]), :]
    return data

def comparison_plot():
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    results = []

    for ball in balls:
        data = load_data(ball)
        data = crop_data(data, ball)
        if len(data) < 10: 
            continue
        ball_folder = _ball_folder(ball=ball['name'], fluid=ball['fluid'],
                                   method=ball['method'])
        if not (ball_folder / 'fit_params.txt').exists():
            get_fit_params(ball_folder)
        if dimensionless:
            params = np.genfromtxt(ball_folder / 'fit_params.txt')[1]
        else:
            params = np.genfromtxt(ball_folder / 'fit_params.txt')[0]
        beta, sd_beta = params[:3], params[3:]
        data = _log_linear_data(data, beta)

        label = f"{ball['name']} {ball['method']} {ball['fluid']}"
        ball_size = BALL_DIAMETERS[ball['name'].split('_')[0]][0]

        _errorbar(data, legend=False)

        x_fit = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 50)
        
        if linear:
            y_fit = true_power_law(beta, x_fit)
        else:
            y_fit = power_law(beta, x_fit)
            
        
        ax.plot(x_fit, y_fit, linestyle='--', label=(
            f"{label}:\n"
            + fr"$\alpha$={value_to_string(beta[0], sd_beta[0])}" + "\n"
            + fr"$\beta$={value_to_string(beta[1], sd_beta[1])}" + "\n"
            + fr"Diametre = {ball_size * 1000} mm"
        ))

        results.append((label, beta, sd_beta))

    # a, b = balls
    # ax.set_title(f"{a['name']} {a['method']} {a['fluid']} vs "
    #              f"{b['name']} {b['method']} {b['fluid']}")

    if log_scale:
        ax.set_xscale('log')
        ax.set_yscale('log')
    ax.legend(
        framealpha=0,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.12),  # position below each subplot
        ncol=2)
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    comparison_plot()