# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 20:36:19 2025

@author: David Mawson
"""
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER
from plot_ball_data import _errorbar, true_power_law, power_law
from make_dimensionless import BALL_DIAMETERS
from fit_power_law_odr import fit_power_law_odr
from value_to_string import value_to_string


balls = [
    {'name': 'ball3',
     'method': 'no-hold',
     'fluid': 'oil',},

    {'name': 'ball3_repeat',
     'method': 'no-hold',
     'fluid': 'oil',},

    {'name': 'ball3',
     'method': 'hold',
     'fluid': 'oil',},

    {'name': 'ball3_repeat',
     'method': 'hold',
     'fluid': 'oil',}
]

crop_speed = (0, 0.5)

log_scale = False
dimensionless = False
linear = False

def load_data(ball_info):
    """Load data for a single ball."""
    ball_name = ball_info['name']
    method = ball_info['method']
    fluid = ball_info['fluid']

    if dimensionless:
        path = MASTER_FOLDER / fluid / method / ball_name / "dimensionless_data.txt"
    else:
        path = MASTER_FOLDER / fluid / method / ball_name / "speed_pressure.txt"

    return np.genfromtxt(path, delimiter=' ')


def crop_data(data, ball_info):
    if 'cropping' in ball_info.keys():
        crop = ball_info['cropping']
    else:
        crop = crop_speed
    data = data[(crop[0]<data[:, 1]) & (data[:, 1]<crop[1]), :]
    return data

def adjust_to_make_linear(data, beta, ball_info):
    """Apply linear correction and mask if needed."""
    if linear:
        data[:, 0] -= beta[2]
        data = data[data[:, 0] > 0, :]
    return data

def comparison_plot():
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    results = []

    for ball in balls:
        data = load_data(ball)
        data = crop_data(data, ball)
        beta, sd_beta = fit_power_law_odr(data)
        data = adjust_to_make_linear(data, beta, ball)

        label = f"{ball['name']} {ball['method']} {ball['fluid']}"
        ball_size = BALL_DIAMETERS[ball['name'].split('_')[0]][0]

        _errorbar(data, dimensions=not dimensionless, legend=False)

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